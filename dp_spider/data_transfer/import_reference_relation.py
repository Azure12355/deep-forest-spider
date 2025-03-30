"""
reference_relation表数据导入脚本（改进版）
功能：将cleaned_data目录下所有reference_relation开头的CSV文件导入到MySQL
改进点：处理species_guid和icode组成的唯一键冲突，跳过重复记录而不回滚
"""

import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text, exc
from tqdm import tqdm
from datetime import datetime

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('log/import_reference_relation.log'),
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
    'charset': 'utf8mb4'
}

# CSV文件与数据库表字段映射
FIELD_MAPPING = {
    'icode': 'icode',
    'author_display': 'author_display',
    'title': 'title',
    'species_guid': 'species_guid',
    'reference_type': 'reference_type',
    'url': 'url'
}

def get_all_reference_relation_files():
    """
    获取cleaned_data目录下所有reference_relation开头的CSV文件
    :return: 文件路径列表
    """
    file_paths = []
    base_dir = os.path.join(os.getcwd(), '../cleaned_data')

    # 遍历cleaned_data目录及其子目录
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.startswith('reference_relation') and file.endswith('.csv'):
                file_paths.append(os.path.join(root, file))

    return file_paths

def validate_table_exists(engine):
    """
    验证目标表是否存在
    :param engine: SQLAlchemy引擎
    :return: 存在返回True，否则返回False
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES LIKE 'reference_relation'"))
            return result.rowcount > 0
    except Exception as e:
        logger.error(f"验证表是否存在时出错: {str(e)}")
        return False

def check_duplicate_records(conn, species_guid, icode):
    """
    检查记录是否已存在（基于species_guid和icode组合）
    :param conn: 数据库连接
    :param species_guid: 物种GUID
    :param icode: 文献标识码
    :return: 存在返回True，否则返回False
    """
    try:
        query = text("""
            SELECT COUNT(*) FROM reference_relation 
            WHERE species_guid = :species_guid AND icode = :icode
        """)
        result = conn.execute(query, {'species_guid': species_guid, 'icode': icode})
        return result.scalar() > 0
    except Exception as e:
        logger.error(f"检查重复记录时出错: {str(e)}")
        return False  # 假设出错时不跳过，让数据库决定是否允许插入

def insert_record(conn, record):
    """
    插入单条记录，处理可能的唯一键冲突
    :param conn: 数据库连接
    :param record: 要插入的记录(dict)
    :return: (是否成功, 是否重复)
    """
    try:
        # 构建INSERT语句（忽略重复键错误）
        columns = ', '.join(record.keys())
        values = ', '.join([f':{key}' for key in record.keys()])
        sql = text(f"""
            INSERT IGNORE INTO reference_relation ({columns}) 
            VALUES ({values})
        """)

        conn.execute(sql, record)
        return True, False
    except exc.IntegrityError as e:
        # 如果是唯一键冲突，则跳过
        if 'Duplicate entry' in str(e):
            return False, True
        raise  # 其他完整性错误继续抛出

def process_csv_file(file_path, engine):
    """
    处理单个CSV文件并将其数据导入数据库
    :param file_path: CSV文件路径
    :param engine: SQLAlchemy引擎
    :return: (成功行数, 失败行数, 跳过行数)
    """
    success_rows = 0
    fail_rows = 0
    skip_rows = 0

    try:
        # 读取CSV文件
        df = pd.read_csv(file_path, encoding='utf-8')

        # 检查必要的字段是否存在
        required_fields = ['icode', 'species_guid']
        for field in required_fields:
            if field not in df.columns:
                raise ValueError(f"CSV文件缺少必要字段: {field}")

        # 只保留映射表中存在的字段
        columns_to_keep = [col for col in df.columns if col in FIELD_MAPPING]
        df = df[columns_to_keep]

        # 重命名列以匹配数据库字段名
        df.rename(columns=FIELD_MAPPING, inplace=True)

        # 添加默认字段
        if 'reference_type' not in df.columns:
            df['reference_type'] = 'distribution'

        # 处理数据：去除字符串字段两端的空格
        str_columns = ['author_display', 'title', 'species_guid', 'reference_type', 'url']
        for col in str_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        # 处理空值
        df.replace('nan', None, inplace=True)
        df.replace('', None, inplace=True)

        # 转换为字典列表
        records = df.to_dict('records')
        total_rows = len(records)

        logger.info(f"正在处理文件: {os.path.basename(file_path)}")

        with engine.connect() as conn:
            with tqdm(total=total_rows, desc=f"处理 {os.path.basename(file_path)}") as pbar:
                for record in records:
                    try:
                        # 检查必填字段
                        if not record.get('species_guid') or not record.get('icode'):
                            fail_rows += 1
                            pbar.update(1)
                            continue

                        # 插入记录
                        success, is_duplicate = insert_record(conn, record)

                        if success:
                            success_rows += 1
                        elif is_duplicate:
                            skip_rows += 1
                        else:
                            fail_rows += 1

                    except Exception as e:
                        logger.error(f"处理记录时出错: {str(e)}")
                        fail_rows += 1

                    pbar.update(1)

                # 提交事务
                conn.commit()

        logger.info(f"文件 {os.path.basename(file_path)} 处理完成")
        return success_rows, fail_rows, skip_rows

    except Exception as e:
        logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
        return 0, len(df) if 'df' in locals() else 0, 0

def main():
    """
    主函数：执行数据导入流程
    """
    start_time = datetime.now()
    logger.info("开始导入 reference_relation 表数据")

    # 初始化统计变量
    total_files = 0
    total_rows = 0
    total_success = 0
    total_fail = 0
    total_skip = 0
    failed_files = []

    try:
        # 创建数据库连接
        engine = create_engine(
            f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
            f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
        )

        # 检查表是否存在
        if not validate_table_exists(engine):
            logger.error("错误: reference_relation 表不存在!")
            return

        # 获取所有需要处理的文件
        csv_files = get_all_reference_relation_files()
        total_files = len(csv_files)

        if not csv_files:
            logger.info("没有找到任何 reference_relation 开头的CSV文件")
            return

        logger.info(f"找到 {total_files} 个数据文件准备导入...")

        # 逐个处理文件
        for file_path in csv_files:
            success, fail, skip = process_csv_file(file_path, engine)
            total_rows += (success + fail + skip)
            total_success += success
            total_fail += fail
            total_skip += skip

            if fail > 0:
                failed_files.append(os.path.basename(file_path))

        # 输出统计信息
        logger.info("\n导入完成! 统计信息:")
        logger.info(f"处理文件总数: {total_files}")
        logger.info(f"总数据行数: {total_rows}")
        logger.info(f"成功导入行数: {total_success}")
        logger.info(f"失败行数: {total_fail}")
        logger.info(f"跳过行数(重复记录): {total_skip}")
        logger.info(f"失败文件数: {len(failed_files)}")

        if total_rows > 0:
            success_rate = (total_success / total_rows) * 100
            logger.info(f"成功率: {success_rate:.2f}%")

        if failed_files:
            logger.info("失败文件列表:")
            for file in failed_files:
                logger.info(f"- {file}")

    except Exception as e:
        logger.error(f"导入过程中发生错误: {str(e)}", exc_info=True)
    finally:
        if 'engine' in locals():
            engine.dispose()
            logger.info("数据库连接已关闭")

        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"导入过程耗时: {duration}")

if __name__ == '__main__':
    main()