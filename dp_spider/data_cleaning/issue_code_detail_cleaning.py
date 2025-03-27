import json
import csv
import os
import uuid
from datetime import datetime

# 定义输入和输出路径
INPUT_DIR = 'data/issue_code_detail_list'
OUTPUT_DIR = 'cleaned_data/issue_code_detail'
JSON_FILE = os.path.join(INPUT_DIR, 'issue_code_detail_batch_1.json')
CSV_FILE = os.path.join(OUTPUT_DIR, 'species_reference_info.csv')

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_datetime(date_str):
    """解析日期字符串为DATETIME格式，支持多种常见格式"""
    if not date_str:
        return None
    try:
        # 尝试解析带毫秒的格式，如 '2024-12-20 10:00:31.000'
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            # 尝试解析标准格式，如 '2024-12-20 00:00:00'
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            print(f"警告: 无法解析日期格式 '{date_str}'，返回None")
            return None

def clean_data():
    """清洗issue_code_detail数据并写入CSV文件"""
    # 读取JSON文件
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 定义CSV字段名，与数据库表species_reference_info一致
    fieldnames = [
        'reference_guid', 'icode', 'title', 'source_title', 'authors',
        'author_display', 'primary_category', 'reference_type', 'content_type',
        'keywords', 'country', 'publish_time', 'publisher', 'source_detail',
        'type_code', 'execute_date', 'reference_text', 'abstract', 'creator',
        'created_time', 'editor', 'update_time', 'publish_person',
        'publish_record_time', 'status'
    ]

    # 打开CSV文件并写入表头
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # 处理每条记录
        for record in data:
            # 生成唯一���reference_guid，使用UUID格式
            reference_guid = str(uuid.uuid4())

            # 映射并验证字段
            icode = record.get('Icode', '')
            if not icode:
                print(f"警告: 记录缺少'Icode'字段。跳过此记录")
                continue

            title = record.get('Title', '')
            if not title:
                print(f"警告: 记录缺少'Title'字段。跳过此记录")
                continue

            authors = record.get('IssueAuthor', '')
            if not authors:
                print(f"警告: 记录缺少'IssueAuthor'字段。跳过此记录")
                continue

            creator = record.get('TP_AUTHOR', '')
            if not creator:
                print(f"警告: 记录缺少'TP_AUTHOR'字段。跳过此记录")
                continue

            created_time = parse_datetime(record.get('TP_CREATED'))
            if not created_time:
                print(f"警告: 记录缺少'TP_CREATED'字段或格式错误。跳过此记录")
                continue

            # 其他字段映射，可能为空的字段使用get方法提供默认值
            source_title = record.get('SourceTitle', '')
            author_display = record.get('AuthorDisplay', '')
            primary_category = record.get('ITypes1', '')
            reference_type = record.get('ITypes', '')
            content_type = record.get('ITypes2', '')
            keywords = record.get('KeyWord', '')
            country = record.get('CCname', '')
            publish_time = parse_datetime(record.get('PubTime'))
            publisher = record.get('Publisher', '')
            source_detail = record.get('Derivation', '')
            type_code = record.get('TypeCode', '')
            execute_date = parse_datetime(record.get('ExecuteDate'))
            reference_text = record.get('Reference', '')
            abstract = record.get('AbstractDesc', '')
            editor = record.get('TP_EDITOR', '')
            update_time = parse_datetime(record.get('TP_MODIFIED'))
            publish_person = record.get('PublishPerson', '')
            publish_record_time = parse_datetime(record.get('PublishTime'))
            status = record.get('Status', '')

            # 格式化时间字段为数据库要求的DATETIME格式
            created_time_str = created_time.strftime('%Y-%m-%d %H:%M:%S') if created_time else None
            publish_time_str = publish_time.strftime('%Y-%m-%d %H:%M:%S') if publish_time else None
            execute_date_str = execute_date.strftime('%Y-%m-%d %H:%M:%S') if execute_date else None
            update_time_str = update_time.strftime('%Y-%m-%d %H:%M:%S') if update_time else None
            publish_record_time_str = publish_record_time.strftime('%Y-%m-%d %H:%M:%S') if publish_record_time else None

            # 构建CSV行数据
            csv_row = {
                'reference_guid': reference_guid,
                'icode': icode,
                'title': title,
                'source_title': source_title,
                'authors': authors,
                'author_display': author_display,
                'primary_category': primary_category,
                'reference_type': reference_type,
                'content_type': content_type,
                'keywords': keywords,
                'country': country,
                'publish_time': publish_time_str,
                'publisher': publisher,
                'source_detail': source_detail,
                'type_code': type_code,
                'execute_date': execute_date_str,
                'reference_text': reference_text,
                'abstract': abstract,
                'creator': creator,
                'created_time': created_time_str,
                'editor': editor,
                'update_time': update_time_str,
                'publish_person': publish_person,
                'publish_record_time': publish_record_time_str,
                'status': status
            }

            # 写入CSV文件
            writer.writerow(csv_row)

    print(f"数据清洗完成。输出文件: {CSV_FILE}")
    print(f"共处理 {len(data)} 条记录")

def main():
    """脚本主函数"""
    print(f"开始清洗文件: {JSON_FILE}")
    clean_data()

if __name__ == "__main__":
    main()