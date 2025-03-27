import json
import csv
import os
from uuid import UUID
from datetime import datetime

# 定义输入和输出路径
INPUT_DIR = 'data/cm_diffuse_medium_list'
OUTPUT_DIR = 'cleaned_data/cm_diffuse_medium'
JSON_FILE = os.path.join(INPUT_DIR, 'cm_diffuse_medium_batch_1.json')
CSV_FILE = os.path.join(OUTPUT_DIR, 'species_medium.csv')

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

def validate_uuid(uuid_str):
    """验证字符串是否为有效的UUID"""
    try:
        UUID(uuid_str)
        return True
    except ValueError:
        return False

def parse_datetime(date_str):
    """解析日期字符串为DATETIME格式，支持多种格式"""
    if not date_str:
        return None
    try:
        # 尝试解析常见的日期格式
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            print(f"警告: 无法解析日期格式 '{date_str}'，返回None")
            return None

def clean_data():
    """清洗cm_diffuse_medium数据并写入CSV文件"""
    # 读取JSON文件
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 定义CSV字段名，与数据库表一致
    fieldnames = [
        'species_guid', 'record_guid', 'scientific_name', 'species_type',
        'medium_guid', 'medium_scientific_name', 'description', 'medium_type',
        'reference_id', 'reference_name', 'page', 'author', 'created_time',
        'editor', 'update_time', 'temp_guid', 'temp_scientific_name', 'named_year'
    ]

    # 打开CSV文件并写入表头
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # 处理每条记录
        for record in data:
            # 映射并验证字段
            species_guid = record.get('species_id', '')
            if not validate_uuid(species_guid):
                print(f"警告: 无效的species_guid '{species_guid}' 在记录 rowid {record.get('rowid', '未知')}. 跳过此记录")
                continue

            record_guid = record.get('TP_GUID', '')
            if not validate_uuid(record_guid):
                print(f"警告: 无效的record_guid '{record_guid}' 在记录 rowid {record.get('rowid', '未知')}. 跳过此记录")
                continue

            scientific_name = record.get('SSNameSci', '')
            species_type = record.get('SpeciesType', '')
            medium_guid = record.get('OB_GUID', '')
            medium_scientific_name = record.get('OB_SSNameSci', '')
            description = record.get('Descrip', '')
            medium_type = record.get('MediumType', '')
            reference_id = record.get('ICodeID', '')
            reference_name = record.get('ICodeName', '')
            page = record.get('Page', '')
            author = record.get('TP_AUTHOR', '')
            created_time = parse_datetime(record.get('TP_CREATED'))
            editor = record.get('TP_EDITOR', '')
            update_time = parse_datetime(record.get('TP_MODIFIED'))
            temp_guid = record.get('Tmp_GUID', '')
            temp_scientific_name = record.get('Tmp_SSNameSci', '')
            named_year = record.get('NamedYear', '')

            # 检查必填字段
            required_fields = {
                'scientific_name': scientific_name,
                'species_type': species_type,
                'medium_guid': medium_guid,
                'medium_scientific_name': medium_scientific_name,
                'medium_type': medium_type
            }
            missing_fields = [k for k, v in required_fields.items() if not v]
            if missing_fields:
                print(f"警告: 记录 rowid {record.get('rowid', '未知')} 缺少必填字段 {missing_fields}. 跳过此记录")
                continue

            # 验证medium_guid
            if not validate_uuid(medium_guid):
                print(f"警告: 无效的medium_guid '{medium_guid}' 在记录 rowid {record.get('rowid', '未知')}. 跳过此记录")
                continue

            # 验证temp_guid（如果存在）
            if temp_guid and not validate_uuid(temp_guid):
                print(f"警告: 无效的temp_guid '{temp_guid}' 在记录 rowid {record.get('rowid', '未知')}. 设置为None")
                temp_guid = None

            # 格式化时间字段
            created_time_str = created_time.strftime('%Y-%m-%d %H:%M:%S') if created_time else None
            update_time_str = update_time.strftime('%Y-%m-%d %H:%M:%S') if update_time else None

            # 构建CSV行数据
            csv_row = {
                'species_guid': species_guid,
                'record_guid': record_guid,
                'scientific_name': scientific_name,
                'species_type': species_type,
                'medium_guid': medium_guid,
                'medium_scientific_name': medium_scientific_name,
                'description': description,
                'medium_type': medium_type,
                'reference_id': reference_id,
                'reference_name': reference_name,
                'page': page,
                'author': author,
                'created_time': created_time_str,
                'editor': editor,
                'update_time': update_time_str,
                'temp_guid': temp_guid,
                'temp_scientific_name': temp_scientific_name,
                'named_year': named_year
            }

            # 写入CSV
            writer.writerow(csv_row)

    print(f"数据清洗完成。输出文件: {CSV_FILE}")
    print(f"共处理 {len(data)} 条记录")

def main():
    """脚本主函数"""
    print(f"开始清洗文件: {JSON_FILE}")
    clean_data()

if __name__ == "__main__":
    main()