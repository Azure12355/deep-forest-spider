# data_transfer/species_import.py
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
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('log/import_species.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SpeciesImporter:
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
            self.cursor.execute("SHOW TABLES LIKE 'species'")
            result = self.cursor.fetchone()
            if result:
                logger.info("表 species 已确认存在")
                return True
            else:
                logger.error("表 species 不存在")
                return False
        except pymysql.Error as e:
            logger.error(f"检查表是否存在时出错: {e}")
            return False

    def find_csv_files(self, base_dir='../cleaned_data/meta_info_list'):
        """查找所有species_batch开头的CSV文件"""
        csv_files = []
        for file in os.listdir(base_dir):
            if file.startswith('species_batch') and file.endswith('.csv'):
                csv_files.append(os.path.join(base_dir, file))

        self.total_files = len(csv_files)
        logger.info(f"找到 {self.total_files} 个数据文件准备导入...")
        return csv_files

    def clean_fieldnames(self, fieldnames):
        """清洗字段名：去除BOM、空格和特殊字符"""
        return [fname.strip('\ufeff').strip().lower().replace(' ', '_')
                for fname in fieldnames]

    def parse_datetime(self, dt_str):
        """解析日期时间字符串"""
        if not dt_str or str(dt_str).strip() == '1900-01-01 00:00:00':
            return None

        try:
            # 尝试多种日期格式
            formats = [
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%Y/%m/%d %H:%M:%S',
                '%Y/%m/%d'
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(str(dt_str).strip(), fmt)
                except ValueError:
                    continue
            return None
        except Exception:
            return None

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
                    # 检查必填字段
                    if not row.get('guid'):
                        logger.warning(f"跳过缺失guid的行: {row}")
                        self.failed_rows += 1
                        continue

                    # 准备插入数据
                    insert_data = {
                        'guid': row['guid'],
                        'scientific_name': row.get('scientific_name'),
                        'scientific_name_with_authors': row.get('scientific_name_with_authors'),
                        'authorship': row.get('authorship'),
                        'chinese_name': row.get('chinese_name'),
                        'english_name': row.get('english_name'),
                        'abbreviation': row.get('abbreviation'),
                        'classification': row.get('classification'),
                        'parent_genus': row.get('parent_genus'),
                        'taxonomic_level': row.get('taxonomic_level'),
                        'sources': row.get('sources'),
                        'confirmation_status': row.get('confirmation_status', '待审核'),
                        'reviewer': row.get('reviewer'),
                        'review_time': self.parse_datetime(row.get('review_time')),
                        'original_risk_code': row.get('original_risk_code'),
                        'is_species': row.get('is_species'),
                        'author': row.get('author'),
                        'created_time': self.parse_datetime(row.get('created_time')) or datetime.now(),
                        'editor': row.get('editor'),
                        'update_time': self.parse_datetime(
                            row.get('modified_time') or row.get('update_time')) or datetime.now(),
                        'temp_created_time': self.parse_datetime(row.get('temp_created_time'))
                    }

                    # 移除None值
                    insert_data = {k: v for k, v in insert_data.items() if v is not None}

                    # 构建SQL语句
                    columns = ', '.join(insert_data.keys())
                    placeholders = ', '.join(['%s'] * len(insert_data))
                    sql = f"INSERT INTO species ({columns}) VALUES ({placeholders})"

                    # 执行插入
                    self.cursor.execute(sql, tuple(insert_data.values()))
                    self.conn.commit()
                    self.success_rows += 1

                except (pymysql.Error, ValueError) as e:
                    self.failed_rows += 1
                    logger.warning(f"行处理失败: {e}\n数据: {row}")
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
    importer = SpeciesImporter()
    importer.run_import()
