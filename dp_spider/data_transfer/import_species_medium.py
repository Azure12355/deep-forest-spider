# data_transfer/species_medium_import.py
import os
import csv
import logging
from datetime import datetime
import pymysql
from tqdm import tqdm

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class SpeciesMediumImporter:
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
            self.cursor.execute("SHOW TABLES LIKE 'species_medium'")
            result = self.cursor.fetchone()
            if result:
                logger.info("表 species_medium 已确认存在")
                return True
            else:
                logger.error("表 species_medium 不存在")
                return False
        except pymysql.Error as e:
            logger.error(f"检查表是否存在时出错: {e}")
            return False

    def find_csv_files(self, base_dir='../cleaned_data/cm_diffuse_medium'):
        """查找所有species_medium开头的CSV文件"""
        csv_files = []
        for file in os.listdir(base_dir):
            if file.startswith('species_medium') and file.endswith('.csv'):
                csv_files.append(os.path.join(base_dir, file))

        self.total_files = len(csv_files)
        logger.info(f"找到 {self.total_files} 个数据文件准备导入...")
        return csv_files

    def clean_fieldnames(self, fieldnames):
        """清洗字段名：去除BOM、空格和特殊字符"""
        return [fname.strip('\ufeff').strip().lower().replace(' ', '_')
                for fname in fieldnames]

    def validate_data(self, row):
        """验证并清洗数据"""
        # 处理空字符串转为None
        cleaned = {k: v if v != '' else None for k, v in row.items()}

        # 处理时间字段
        time_fields = ['created_time', 'update_time']
        for field in time_fields:
            if cleaned.get(field) and isinstance(cleaned[field], str):
                try:
                    # 尝试解析时间字符串
                    cleaned[field] = datetime.strptime(cleaned[field], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    cleaned[field] = None

        return cleaned

    def process_csv_file(self, file_path):
        """处理单个CSV文件"""
        try:
            logger.info(f"正在处理文件: {os.path.basename(file_path)}")

            # 尝试多种编码方式读取文件
            encodings = ['utf-8-sig', 'utf-8', 'gbk']
            rows = []

            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as csvfile:
                        reader = csv.DictReader(csvfile)
                        # 标准化字段名
                        reader.fieldnames = self.clean_fieldnames(reader.fieldnames)
                        rows = [row for row in reader if any(row.values())]
                        break
                except UnicodeDecodeError:
                    continue

            if not rows:
                logger.error(f"无法读取文件 {file_path}")
                self.failed_files += 1
                return False

            # 处理数据
            for row in tqdm(rows, desc=f"处理 {os.path.basename(file_path)}"):
                self.total_rows += 1
                try:
                    # 验证并清洗数据
                    cleaned_row = self.validate_data(row)

                    # 检查必填字段
                    if not cleaned_row.get('species_guid'):
                        logger.warning(f"跳过缺失species_guid的行: {cleaned_row}")
                        self.failed_rows += 1
                        continue

                    # 准备插入数据
                    insert_data = {
                        'species_guid': cleaned_row['species_guid'],
                        'record_guid': cleaned_row.get('record_guid'),
                        'scientific_name': cleaned_row.get('scientific_name'),
                        'species_type': cleaned_row.get('species_type'),
                        'medium_guid': cleaned_row.get('medium_guid'),
                        'medium_scientific_name': cleaned_row.get('medium_scientific_name'),
                        'description': cleaned_row.get('description'),
                        'medium_type': cleaned_row.get('medium_type'),
                        'transmission_method': cleaned_row.get('transmission_method'),
                        'reference_id': cleaned_row.get('reference_id'),
                        'reference_name': cleaned_row.get('reference_name'),
                        'page': cleaned_row.get('page'),
                        'author': cleaned_row.get('author'),
                        'created_time': cleaned_row.get('created_time', datetime.now()),
                        'editor': cleaned_row.get('editor'),
                        'update_time': cleaned_row.get('update_time', datetime.now()),
                        'temp_guid': cleaned_row.get('temp_guid'),
                        'temp_scientific_name': cleaned_row.get('temp_scientific_name'),
                        'named_year': cleaned_row.get('named_year')
                    }

                    # 移除None值
                    insert_data = {k: v for k, v in insert_data.items() if v is not None}

                    # 构建SQL语句
                    columns = ', '.join(insert_data.keys())
                    placeholders = ', '.join(['%s'] * len(insert_data))
                    sql = f"INSERT INTO species_medium ({columns}) VALUES ({placeholders})"

                    # 执行插入
                    self.cursor.execute(sql, tuple(insert_data.values()))
                    self.conn.commit()
                    self.success_rows += 1

                except (pymysql.Error, ValueError) as e:
                    self.failed_rows += 1
                    logger.warning(f"行处理失败: {e}\n数据: {cleaned_row}")
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
    importer = SpeciesMediumImporter()
    importer.run_import()