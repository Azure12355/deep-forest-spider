"""
species_basic_info表数据导入脚本
功能：将cleaned_data/species_basicinfo目录下所有species_basic_info_batch开头的CSV文件数据导入到MySQL的species_basic_info表中
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
        logging.FileHandler('log/import_species_basic_info.log'),
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
CSV_DIR = os.path.join('..', 'cleaned_data', 'species_basicinfo')

# 表结构定义
TABLE_COLUMNS = [
    'id', 'species_guid', 'record_guid', 'scientific_name', 'english_name',
    'biological_properties', 'morphological_characteristics', 'detection_method',
    'distribution_description', 'icode_id', 'icode_name', 'page', 'remark',
    'author', 'created_time', 'editor', 'update_time', 'temp_created_time',
    'temp_morphological'
]


def get_all_batch_files():
    """
    获取所有species_basic_info_batch开头的CSV文件
    :return: 按文件名排序的文件路径列表
    """
    files = []
    for filename in os.listdir(CSV_DIR):
        if filename.startswith('species_basic_info_batch') and filename.endswith('.csv'):
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


def clean_text_field(value):
    """
    清理文本字段
    :param value: 原始值
    :return: 清理后的值或None
    """
    if pd.isna(value) or value is None:
        return None
    value = str(value).strip()
    return value if value else None


def clean_datetime_field(value):
    """
    清理日期时间字段
    :param value: 原始值
    :return: 格式化后的日期时间字符串或None
    """
    if pd.isna(value) or value is None:
        return None
    try:
        # 尝试解析各种可能的日期时间格式
        dt = pd.to_datetime(value)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return None


def validate_and_clean_row(row):
    """
    验证和清洗单行数据
    :param row: 原始数据行
    :return: 清洗后的数据字典或None(如果数据无效)
    """
    # 验证必填字段
    species_guid = validate_uuid(row.get('species_guid'))
    record_guid = validate_uuid(row.get('record_guid'))

    if not species_guid or not record_guid:
        logger.warning(f"无效的GUID: species_guid={row.get('species_guid')}, record_guid={row.get('record_guid')}")
        return None

    # 构建清洗后的数据字典
    cleaned_data = {
        'species_guid': species_guid,
        'record_guid': record_guid,
        'scientific_name': clean_text_field(row.get('scientific_name')),
        'english_name': clean_text_field(row.get('english_name')),
        'biological_properties': clean_text_field(row.get('biological_properties')),
        'morphological_characteristics': clean_text_field(row.get('morphological_characteristics')),
        'detection_method': clean_text_field(row.get('detection_method')),
        'distribution_description': clean_text_field(row.get('distribution_description')),
        'icode_id': clean_text_field(row.get('icode_id')),
        'icode_name': clean_text_field(row.get('icode_name')),
        'page': clean_text_field(row.get('page')),
        'remark': clean_text_field(row.get('remark')),
        'author': clean_text_field(row.get('author')),
        'created_time': clean_datetime_field(row.get('created_time')) or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'editor': clean_text_field(row.get('editor')),
        'update_time': clean_datetime_field(row.get('update_time')),
        'temp_created_time': clean_datetime_field(row.get('temp_created_time')),
        'temp_morphological': clean_text_field(row.get('temp_morphological'))
    }

    return cleaned_data


def create_table_if_not_exists(conn):
    """
    检查表是否存在，不存在则创建
    :param conn: 数据库连接
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS species_basic_info (
        id BIGINT AUTO_INCREMENT COMMENT '自增主键ID' PRIMARY KEY,
        species_guid CHAR(36) NOT NULL COMMENT '物种全局唯一标识符(UUID格式)',
        record_guid CHAR(36) NOT NULL COMMENT '记录全局唯一标识符(UUID格式)',
        scientific_name VARCHAR(512) NULL COMMENT '物种学名(拉丁名)',
        english_name VARCHAR(512) NULL COMMENT '物种英文名称',
        biological_properties TEXT NULL COMMENT '生物学特性详细描述',
        morphological_characteristics TEXT NULL COMMENT '形态学特征描述',
        detection_method TEXT NULL COMMENT '物种检测方法描述',
        distribution_description TEXT NULL COMMENT '物种分布描述文本',
        icode_id CHAR(36) NULL COMMENT '关联引用文献ID',
        icode_name VARCHAR(255) NULL COMMENT '引用文献名称',
        page VARCHAR(50) NULL COMMENT '引用文献页码信息',
        remark TEXT NULL COMMENT '备注信息',
        author VARCHAR(512) NULL COMMENT '数据创建者',
        created_time DATETIME NOT NULL COMMENT '数据创建时间',
        editor VARCHAR(512) NULL COMMENT '最后修改者',
        update_time DATETIME NULL COMMENT '最后修改时间',
        temp_created_time DATETIME NULL COMMENT '临时创建时间(用途待定)',
        temp_morphological TEXT NULL COMMENT '临时形态学信息(用途待定)',
        UNIQUE KEY uk_record_guid (record_guid),
        INDEX idx_created_time (created_time),
        INDEX idx_english_name (english_name),
        INDEX idx_scientific_name (scientific_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='物种基本信息表';
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(create_table_sql)
        conn.commit()
        logger.info("表 species_basic_info 已确认存在")
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
        logger.warning("没有找到任何species_basic_info_batch开头的CSV文件")
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
        INSERT INTO species_basic_info (
            species_guid, record_guid, scientific_name, english_name,
            biological_properties, morphological_characteristics, detection_method,
            distribution_description, icode_id, icode_name, page, remark,
            author, created_time, editor, update_time, temp_created_time,
            temp_morphological
        ) VALUES (
            %(species_guid)s, %(record_guid)s, %(scientific_name)s, %(english_name)s,
            %(biological_properties)s, %(morphological_characteristics)s, %(detection_method)s,
            %(distribution_description)s, %(icode_id)s, %(icode_name)s, %(page)s, %(remark)s,
            %(author)s, %(created_time)s, %(editor)s, %(update_time)s, %(temp_created_time)s,
            %(temp_morphological)s
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