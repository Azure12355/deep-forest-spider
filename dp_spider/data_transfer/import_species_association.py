# data_transfer/species_association_import.py
import csv
import logging
import os

import pymysql
from tqdm import tqdm

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('log/import_species_association.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SpeciesAssociationImporter:
    def __init__(self):
        # 数据库连接配置
        self.db_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '12345678',
            'db': 'deep_forest',
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        self.conn = None
        self.cursor = None

        # 统计信息
        self.total_files = 0
        self.total_rows = 0
        self.success_rows = 0
        self.failed_rows = 0
        self.failed_files = 0

    def connect_db(self):
        """建立数据库连接"""
        try:
            self.conn = pymysql.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logger.info("数据库连接成功")
            return True
        except pymysql.Error as e:
            logger.error(f"数据库连接失败: {e}")
            return False

    def close_db(self):
        """关闭数据库连接"""
        if self.conn:
            try:
                self.conn.close()
                logger.info("数据库连接已关闭")
            except pymysql.Error as e:
                logger.error(f"关闭数据库连接时出错: {e}")

    def check_table_exists(self):
        """检查目标表是否存在"""
        try:
            self.cursor.execute("SHOW TABLES LIKE 'species_association'")
            result = self.cursor.fetchone()
            if result:
                logger.info("表 species_association 已确认存在")
                return True
            else:
                logger.error("表 species_association 不存在")
                return False
        except pymysql.Error as e:
            logger.error(f"检查表是否存在时出错: {e}")
            return False

    def find_csv_files(self, base_dir='../cleaned_data/pest_relation'):
        """查找所有species_association_batch开头的CSV文件"""
        csv_files = []
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.startswith('species_association_batch') and file.endswith('.csv'):
                    csv_files.append(os.path.join(root, file))

        self.total_files = len(csv_files)
        logger.info(f"找到 {self.total_files} 个数据文件准备导入...")
        return csv_files

    def process_csv_file(self, file_path):
        """处理单个CSV文件"""
        try:
            logger.info(f"正在处理文件: {os.path.basename(file_path)}")

            # 读取CSV文件
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)

                # 使用tqdm显示进度条
                for row in tqdm(rows, desc=f"处理 {os.path.basename(file_path)}"):
                    self.total_rows += 1
                    try:
                        # 准备插入数据
                        insert_data = {
                            'species_guid': row.get('species_guid'),
                            'record_guid': row.get('record_guid'),
                            'scientific_name': row.get('scientific_name'),
                            'host_range': row.get('host_range'),
                            'potential_eco_desc': row.get('potential_eco_desc'),
                            'description': row.get('description'),
                            'management_info': row.get('management_info'),
                            'remark': row.get('remark'),
                            'reference_id': row.get('reference_id'),
                            'reference_name': row.get('reference_name'),
                            'page': row.get('page'),
                            'author': row.get('author'),
                            'editor': row.get('editor'),
                        }

                        # 移除None值
                        insert_data = {k: v for k, v in insert_data.items() if v is not None}

                        # 构建SQL语句
                        columns = ', '.join(insert_data.keys())
                        placeholders = ', '.join(['%s'] * len(insert_data))
                        sql = f"INSERT INTO species_association ({columns}) VALUES ({placeholders})"

                        # 执行插入
                        self.cursor.execute(sql, tuple(insert_data.values()))
                        self.conn.commit()
                        self.success_rows += 1

                    except (pymysql.Error, ValueError) as e:
                        self.failed_rows += 1
                        logger.warning(f"行处理失败: {e} - 数据: {row}")
                        self.conn.rollback()

            logger.info(f"文件 {os.path.basename(file_path)} 处理完成")
            return True

        except Exception as e:
            self.failed_files += 1
            logger.error(f"处理文件 {os.path.basename(file_path)} 时出错: {e}")
            return False

    def print_summary(self):
        """打印导入统计信息"""
        logger.info("\n导入完成! 统计信息:")
        logger.info(f"处理文件总数: {self.total_files}")
        logger.info(f"总数据行数: {self.total_rows}")
        logger.info(f"成功导入行数: {self.success_rows}")
        logger.info(f"失败行数: {self.failed_rows}")
        logger.info(f"失败文件数: {self.failed_files}")

        if self.total_rows > 0:
            success_rate = (self.success_rows / self.total_rows) * 100
            logger.info(f"成功率: {success_rate:.2f}%")
        else:
            logger.info("成功率: 0.00%")

    def run_import(self):
        """执行导入流程"""
        try:
            if not self.connect_db():
                return False

            if not self.check_table_exists():
                return False

            csv_files = self.find_csv_files()
            if not csv_files:
                logger.warning("没有找到可导入的CSV文件")
                return False

            for file_path in csv_files:
                self.process_csv_file(file_path)

            self.print_summary()
            return True

        except Exception as e:
            logger.error(f"导入过程中发生错误: {e}")
            return False
        finally:
            self.close_db()


if __name__ == '__main__':
    importer = SpeciesAssociationImporter()
    importer.run_import()
