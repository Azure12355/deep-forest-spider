# -*- coding: utf-8 -*-
import json
import os
import pandas as pd
from datetime import datetime

# === 全局配置 ===
# 定义输入和输出目录
INPUT_DIR = 'data/meta_info_list'  # 输入目录，存放 meta_batch_*.json 文件
OUTPUT_DIR = 'cleaned_data/meta_info_list'   # 输出目录，存放清洗后的 CSV 文件

# 创建输出目录（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 定义物种主表 (species) 的字段映射关系
SPECIES_FIELDS = {
    'TP_GUID': 'guid',
    'SSNameSci': 'scientific_name',
    'SSName': 'scientific_name_with_authors',
    'NamedYear': 'authorship',
    'SCName': 'chinese_name',
    'SEName': 'english_name',
    'SENameAbb': 'abbreviation',
    'SClass': 'classification',
    'ParentSsName': 'parent_genus',
    'SLevel': 'taxonomic_level',
    'Source': 'sources',
    'Status': 'confirmation_status',
    'Checker': 'reviewer',
    'CheckTime': 'review_time',
    'OrgRiskCode': 'original_risk_code',
    'IsSpecies': 'is_species',
    'TP_AUTHOR': 'author',
    'TP_CREATED': 'created_time',
    'TP_EDITOR': 'editor',
    'TP_MODIFIED': 'modified_time',
    'Temp_CREATED': 'temp_created_time'
}

# 定义物种别名表 (species_other_names) 的字段映射关系
OTHER_NAMES_FIELDS = {
    'SONType': 'other_name_type',
    'NamedYear': 'named_year',
    'SOtherNameSci': 'other_name'
}

# === 数据处理函数 ===
def parse_datetime(date_str):
    """
    将日期字符串转换为 datetime 对象，支持多种格式。
    如果解析失败，返回 None。
    """
    if not date_str:
        return None
    try:
        # 尝试解析带毫秒的格式：'YYYY-MM-DD HH:MM:SS.sss'
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError:
        try:
            # 尝试解析不带毫秒的格式：'YYYY-MM-DD HH:MM:SS'
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            print(f"警告: 无法解析日期字符串: {date_str}")
            return None

def process_species_record(record):
    """
    处理单个物种记录，映射到主表字段，并进行数据类型转换。
    """
    # 根据映射关系提取字段，缺失字段默认为空字符串
    species_record = {SPECIES_FIELDS[key]: record.get(key, '') for key in SPECIES_FIELDS}

    # 处理日期字段，确保符合 DATETIME 格式
    date_fields = ['review_time', 'created_time', 'modified_time', 'temp_created_time']
    for field in date_fields:
        species_record[field] = parse_datetime(species_record[field])

    # 处理布尔字段 is_species，将 1/0 转换为 True/False
    species_record['is_species'] = bool(species_record['is_species']) if species_record['is_species'] != '' else False

    return species_record

def process_other_names(record):
    """
    处理物种记录中的 'ym' 字段，提取别名信息并映射到别名表字段。
    """
    guid = record['TP_GUID']
    other_names_data = []

    # 如果 'ym' 字段不存在或为空，返回空列表
    ym_list = record.get('ym', [])
    for ym in ym_list:
        other_name_record = {OTHER_NAMES_FIELDS[key]: ym.get(key, '') for key in OTHER_NAMES_FIELDS}
        other_name_record['species_guid'] = guid  # 添加外键关联
        other_names_data.append(other_name_record)

    return other_names_data

# === 主处理逻辑 ===
def clean_meta_data():
    """
    主函数：遍历 meta_info_list 目录，清洗所有 meta_batch_*.json 文件。
    """
    # 用于存储所有批次的主表和别名表数据
    all_species_data = []
    all_other_names_data = []

    # 遍历输入目录下的所有 JSON 文件
    for filename in os.listdir(INPUT_DIR):
        if filename.startswith('meta_batch_') and filename.endswith('.json'):
            filepath = os.path.join(INPUT_DIR, filename)
            print(f"正在处理文件: {filename}")

            # 读取 JSON 文件
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"错误: 无法读取文件 {filename}: {e}")
                continue

            # 处理每个物种记录
            species_data = []
            other_names_data = []
            for record in data:
                # 处理主表数据
                species_record = process_species_record(record)
                species_data.append(species_record)

                # 处理别名表数据
                other_names = process_other_names(record)
                other_names_data.extend(other_names)

            # 将当前批次数据添加到总数据中
            all_species_data.extend(species_data)
            all_other_names_data.extend(other_names_data)

            # 将当前批次数据保存为 CSV 文件
            batch_num = filename.split('_')[-1].split('.')[0]
            species_df = pd.DataFrame(species_data)
            other_names_df = pd.DataFrame(other_names_data)

            species_df.to_csv(
                os.path.join(OUTPUT_DIR, f'species_batch_{batch_num}.csv'),
                index=False,
                encoding='utf-8-sig'  # 使用 utf-8-sig 避免中文乱码
            )
            other_names_df.to_csv(
                os.path.join(OUTPUT_DIR, f'other_names_batch_{batch_num}.csv'),
                index=False,
                encoding='utf-8-sig'
            )
            print(f"完成处理文件: {filename}，生成 species_batch_{batch_num}.csv 和 other_names_batch_{batch_num}.csv")

    print("所有文件处理完成！")

# === 脚本入口 ===
if __name__ == "__main__":
    clean_meta_data()