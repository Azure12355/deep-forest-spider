"""
species_host表数据导入脚本
功能：将cleaned_data/species_host目录下所有species_host_batch开头的CSV文件数据导入到MySQL的species_host表中
"""

import os
import pandas as pd
import pymysql
from pymysql import MySQLError
from datetime import datetime
import uuid
import logging
from tqdm import tqdm
import re

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log/species_host_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '12345678',
    'database': 'deep_forest',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# CSV文件目录路径 (相对于脚本的位置)
CSV_DIR = os.path.join('..', 'cleaned_data', 'species_host')

# 有效的interaction_type枚举值
VALID_INTERACTION_TYPES = {'primary', 'secondary', 'occasional'}


def get_all_batch_files():
    """
    获取所有species_host_batch开头的CSV文件
    :return: 按文件名排序的文件路径列表
    """
    files = []
    for filename in os.listdir(CSV_DIR):
        if filename.startswith('species_host_batch') and filename.endswith('.csv'):
            files.append(os.path.join(CSV_DIR, filename))
    # 按文件名排序确保导入顺序一致
    return sorted(files)


def validate_uuid(uuid_str):
    """
    验证UUID格式是否正确
    :param uuid_str: 待验证的UUID字符串
    :return: 验证通过的UUID字符串或None
    """
    if not uuid_str or pd.isna(uuid_str):
        return None
    try:
        return str(uuid.UUID(uuid_str.strip()))
    except (ValueError, AttributeError):
        return None


def clean_text_field(value, max_length=None):
    """
    清理文本字段
    :param value: 原始值
    :param max_length: 最大长度限制(可选)
    :return: 清理后的值或None
    """
    if pd.isna(value) or value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    if max_length and len(value) > max_length:
        value = value[:max_length]
        logger.warning(f"文本字段超出最大长度，已截断: {value}")
    return value


def clean_host_types(host_types):
    """
    清理和格式化host_types字段
    :param host_types: 原始host_types值
    :return: 清理后的host_types字符串
    """
    if pd.isna(host_types) or not host_types:
        return None

    # 处理带引号和逗号的格式
    host_types = str(host_types).strip()
    if host_types.startswith('"') and host_types.endswith('"'):
        host_types = host_types[1:-1]

    # 分割并清理每个类型
    types = [t.strip() for t in host_types.split(',') if t.strip()]

    # 去重并重新组合
    cleaned_types = list(set(types))
    return ','.join(cleaned_types) if cleaned_types else None


def validate_interaction_type(interaction_type):
    """
    验证interaction_type是否有效
    :param interaction_type: 原始interaction_type值
    :return: 验证后的interaction_type或None
    """
    if pd.isna(interaction_type) or not interaction_type:
        return None
    interaction_type = str(interaction_type).strip().lower()
    return interaction_type if interaction_type in VALID_INTERACTION_TYPES else None


def validate_and_clean_row(row):
    """
    验证和清洗单行数据
    :param row: 原始数据行
    :return: 清洗后的数据字典或None(如果数据无效)
    """
    # 验证必填字段
    species_guid = validate_uuid(row.get('species_guid'))
    host_guid = validate_uuid(row.get('host_guid'))
    host_name = clean_text_field(row.get('host_name'), max_length=512)

    if not all([species_guid, host_guid, host_name]):
        logger.warning(f"缺少必填字段或字段无效: species_guid={species_guid}, "
                       f"host_guid={host_guid}, host_name={host_name}")
        return None

    # 构建清洗后的数据字典
    cleaned_data = {
        'species_guid': species_guid,
        'host_guid': host_guid,
        'host_name': host_name,
        'host_name_cn': clean_text_field(row.get('host_name_cn'), max_length=512),
        'host_types': clean_host_types(row.get('host_types')),
        'interaction_type': validate_interaction_type(row.get('interaction_type'))
    }

    return cleaned_data


def create_table_if_not_exists(conn):
    """
    检查表是否存在，不存在则创建
    :param conn: 数据库连接
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS species_host (
        id BIGINT AUTO_INCREMENT COMMENT '自增主键ID' PRIMARY KEY,
        species_guid CHAR(36) NOT NULL COMMENT '关联物种的全局唯一标识符(UUID格式)',
        host_guid CHAR(36) NOT NULL COMMENT '寄主记录的全局唯一标识符(UUID格式)',
        host_name VARCHAR(512) NOT NULL COMMENT '寄主学名(拉丁名)',
        host_name_cn VARCHAR(512) NULL COMMENT '寄主中文名称',
        host_types VARCHAR(255) NULL COMMENT '寄主类型(逗号分隔，如自然寄主/接种寄主等)',
        interaction_type ENUM('primary', 'secondary', 'occasional') NULL COMMENT '主要寄主类型(主要/次要/偶发)',
        created_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '记录创建时间',
        updated_time DATETIME DEFAULT (now()) NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
        FULLTEXT INDEX ft_host_types (host_types) COMMENT '全文索引用于寄主类型搜索',
        INDEX idx_host_name (host_name),
        INDEX idx_host_name_cn (host_name_cn),
        INDEX idx_species_guid (species_guid)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='物种与寄主植物关联信息表';
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(create_table_sql)
        conn.commit()
        logger.info("表 species_host 已确认存在")
    except MySQLError as e:
        logger.error(f"创建表失败: {e}")
        raise


def import_data_to_mysql(batch_size=1000):
    """
    主函数：读取CSV文件并导入到MySQL
    :param batch_size: 批量提交的行数
    """
    # 获取所有批次文件
    batch_files = get_all_batch_files()
    if not batch_files:
        logger.warning("没有找到任何species_host_batch开头的CSV文件")
        return

    logger.info(f"找到 {len(batch_files)} 个数据文件准备导入...")

    try:
        # 建立数据库连接
        conn = pymysql.connect(**DB_CONFIG)

        # 确保表存在
        create_table_if_not_exists(conn)

        # 统计变量
        stats = {
            'total_files': len(batch_files),
            'total_rows': 0,
            'success_rows': 0,
            'error_rows': 0,
            'file_errors': 0
        }

        # 准备插入SQL
        insert_sql = """
        INSERT INTO species_host (
            species_guid, host_guid, host_name, host_name_cn,
            host_types, interaction_type
        ) VALUES (
            %(species_guid)s, %(host_guid)s, %(host_name)s, %(host_name_cn)s,
            %(host_types)s, %(interaction_type)s
        )
        """

        for file_path in batch_files:
            file_name = os.path.basename(file_path)
            logger.info(f"正在处理文件: {file_name}")

            try:
                # 读取CSV文件
                df = pd.read_csv(file_path)

                # 准备批量插入数据
                batch_data = []

                for _, row in tqdm(df.iterrows(), total=len(df), desc=f"处理 {file_name}"):
                    stats['total_rows'] += 1

                    # 验证和清洗数据
                    cleaned_data = validate_and_clean_row(row)
                    if not cleaned_data:
                        stats['error_rows'] += 1
                        continue

                    batch_data.append(cleaned_data)

                    # 达到批量大小则执行插入
                    if len(batch_data) >= batch_size:
                        try:
                            with conn.cursor() as cursor:
                                cursor.executemany(insert_sql, batch_data)
                            conn.commit()
                            stats['success_rows'] += len(batch_data)
                            batch_data = []
                        except MySQLError as e:
                            conn.rollback()
                            logger.error(f"批量插入失败: {e}")
                            stats['error_rows'] += len(batch_data)
                            batch_data = []

                # 插入剩余数据
                if batch_data:
                    try:
                        with conn.cursor() as cursor:
                            cursor.executemany(insert_sql, batch_data)
                        conn.commit()
                        stats['success_rows'] += len(batch_data)
                    except MySQLError as e:
                        conn.rollback()
                        logger.error(f"批量插入失败: {e}")
                        stats['error_rows'] += len(batch_data)

                logger.info(f"文件 {file_name} 处理完成")

            except Exception as e:
                stats['file_errors'] += 1
                logger.error(f"处理文件 {file_name} 时出错: {e}", exc_info=True)
                continue

        # 打印最终统计信息
        logger.info("\n导入完成! 统计信息:")
        logger.info(f"处理文件总数: {stats['total_files']}")
        logger.info(f"总数据行数: {stats['total_rows']}")
        logger.info(f"成功导入行数: {stats['success_rows']}")
        logger.info(f"失败行数: {stats['error_rows']}")
        logger.info(f"失败文件数: {stats['file_errors']}")
        if stats['total_rows'] > 0:
            logger.info(f"成功率: {stats['success_rows'] / stats['total_rows'] * 100:.2f}%")

    except MySQLError as e:
        logger.error(f"数据库连接失败: {e}", exc_info=True)
    finally:
        # 关闭连接
        if 'conn' in locals() and conn:
            conn.close()
            logger.info("数据库连接已关闭")


if __name__ == '__main__':
    import_data_to_mysql()