"""
species_taxonomy表数据导入脚本
功能：将cleaned_data/species_taxonomy目录下所有species_taxonomy_batch开头的CSV文件数据导入到MySQL的species_taxonomy表中
"""

import os
import pandas as pd
import pymysql
from pymysql import MySQLError
from datetime import datetime
import uuid
import logging
from tqdm import tqdm

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log/import_species_taxonomy.log'),
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
CSV_DIR = os.path.join('..', 'cleaned_data', 'species_taxonomy')

# 有效的分类级别
VALID_TAXONOMY_LEVELS = {'界', '门', '纲', '目', '科', '属', '种'}


def get_all_batch_files():
    """
    获取所有species_taxonomy_batch开头的CSV文件
    :return: 按文件名排序的文件路径列表
    """
    files = []
    for filename in os.listdir(CSV_DIR):
        if filename.startswith('species_taxonomy_batch') and filename.endswith('.csv'):
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


def validate_taxonomy_level(level):
    """
    验证分类级别是否有效
    :param level: 分类级别字符串
    :return: 验证后的分类级别或None
    """
    if not level or pd.isna(level):
        return None
    level = str(level).strip()
    return level if level in VALID_TAXONOMY_LEVELS else None


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


def validate_and_clean_row(row):
    """
    验证和清洗单行数据
    :param row: 原始数据行
    :return: 清洗后的数据字典或None(如果数据无效)
    """
    # 验证必填字段
    species_guid = validate_uuid(row.get('species_guid'))
    taxonomy_guid = validate_uuid(row.get('taxonomy_guid'))
    taxonomy_level = validate_taxonomy_level(row.get('taxonomy_level'))
    scientific_name = clean_text_field(row.get('scientific_name'), max_length=512)

    if not all([species_guid, taxonomy_guid, taxonomy_level, scientific_name]):
        logger.warning(f"缺少必填字段或字段无效: species_guid={species_guid}, "
                       f"taxonomy_guid={taxonomy_guid}, taxonomy_level={taxonomy_level}, "
                       f"scientific_name={scientific_name}")
        return None

    # 构建清洗后的数据字典
    cleaned_data = {
        'species_guid': species_guid,
        'taxonomy_guid': taxonomy_guid,
        'taxonomy_level': taxonomy_level,
        'scientific_name': scientific_name,
        'chinese_name': clean_text_field(row.get('chinese_name'), max_length=512),
        'taxonomy_class': clean_text_field(row.get('taxonomy_class'), max_length=255),
        'parent_scientific_name': clean_text_field(row.get('parent_scientific_name'), max_length=512),
        'rank_order': int(row['rank_order']) if 'rank_order' in row and pd.notna(row['rank_order']) else None
    }

    return cleaned_data


def create_table_if_not_exists(conn):
    """
    检查表是否存在，不存在则创建
    :param conn: 数据库连接
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS species_taxonomy (
        id BIGINT AUTO_INCREMENT COMMENT '自增主键ID' PRIMARY KEY,
        species_guid CHAR(36) NOT NULL COMMENT '关联物种的全局唯一标识符(UUID格式)',
        taxonomy_guid CHAR(36) NOT NULL COMMENT '分类层级节点的全局唯一标识符(UUID格式)',
        taxonomy_level VARCHAR(20) NOT NULL COMMENT '分类级别(如界/门/纲/目/科/属/种)',
        scientific_name VARCHAR(512) NOT NULL COMMENT '分类单元的拉丁学名',
        chinese_name VARCHAR(512) NULL COMMENT '分类单元的中文名称',
        taxonomy_class VARCHAR(255) NULL COMMENT '分类类别/通用名(如线虫/昆虫等)',
        parent_scientific_name VARCHAR(512) NULL COMMENT '父级分类单元的学名(顶级分类为NULL)',
        rank_order INT NULL COMMENT '分类层级排序序号(可选项)',
        created_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL COMMENT '记录创建时间',
        updated_time DATETIME DEFAULT (now()) NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
        INDEX idx_parent_name (parent_scientific_name),
        INDEX idx_scientific_name (scientific_name),
        INDEX idx_species_guid (species_guid),
        INDEX idx_taxonomy_level (taxonomy_level)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='物种分类层级信息表';
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(create_table_sql)
        conn.commit()
        logger.info("表 species_taxonomy 已确认存在")
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
        logger.warning("没有找到任何species_taxonomy_batch开头的CSV文件")
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
        INSERT INTO species_taxonomy (
            species_guid, taxonomy_guid, taxonomy_level, scientific_name,
            chinese_name, taxonomy_class, parent_scientific_name, rank_order
        ) VALUES (
            %(species_guid)s, %(taxonomy_guid)s, %(taxonomy_level)s, %(scientific_name)s,
            %(chinese_name)s, %(taxonomy_class)s, %(parent_scientific_name)s, %(rank_order)s
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