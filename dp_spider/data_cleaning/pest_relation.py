# -*- coding: utf-8 -*-
import json
import os
import pandas as pd
from datetime import datetime

# === 全局配置 ===
# 输入目录：存放原始 JSON 文件
INPUT_DIR = 'data/pest_relation'
# 输出目录：存放清洗后的 CSV 文件
OUTPUT_DIR = 'cleaned_data/pest_relation'

# 创建输出目录（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 主表字段映射关系（species_association）
ASSOCIATION_FIELDS = {
    'SC_GUID': 'species_guid',
    'TP_GUID': 'record_guid',
    'SSNameSci': 'scientific_name',
    'PBCharHostRange': 'host_range',
    'PotentialEcoDesc': 'potential_eco_desc',
    'Descrip': 'description',
    'ManagementInfo': 'management_info',
    'Remark': 'remark',
    'ICodeID': 'reference_id',
    'ICodeName': 'reference_name',
    'Page': 'page',
    'TP_AUTHOR': 'author',
    'TP_CREATED': 'created_time',
    'TP_EDITOR': 'editor',
    'TP_MODIFIED': 'update_time'
}

# 引用表字段映射关系（reference_relation）
REFERENCE_FIELDS = {
    'Icode': 'icode',
    'AuthorDisplay': 'author_display',
    'Title': 'title'
}


# === 数据处理函数 ===
def parse_datetime(date_str):
    """
    将日期字符串转换为 datetime 对象，支持多种格式。
    如果解析失败，返回 None。

    参数:
        date_str (str): 原始日期字符串
    返回:
        datetime 或 None: 解析后的日期时间对象
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


def process_association_record(record):
    """
    处理单个物种关联信息记录，映射到主表字段，并进行数据类型转换。

    参数:
        record (dict): JSON 中的单条记录
    返回:
        dict: 映射后的主表记录
    """
    # 根据字段映射提取数据，缺失字段填充为空字符串
    association_record = {
        ASSOCIATION_FIELDS.get(key, key): record.get(key, '')
        for key in ASSOCIATION_FIELDS
    }
    # 添加 id 字段，设为 None，由数据库自增
    association_record['id'] = None

    # 处理日期字段，确保符合 DATETIME 格式
    date_fields = ['created_time', 'update_time']
    for field in date_fields:
        if association_record[field]:
            association_record[field] = parse_datetime(association_record[field])
        else:
            association_record[field] = None

    return association_record


def process_reference_record(record):
    """
    处理物种关联信息记录中的引用信息 (cankao)，映射到引用表字段。

    参数:
        record (dict): JSON 中的单条记录
    返回:
        dict: 映射后的引用表记录
    """
    species_guid = record['SC_GUID']
    cankao = record.get('cankao', {})

    # 映射引用表字段，缺失字段填充为空字符串
    reference_record = {
        REFERENCE_FIELDS.get(key, key): cankao.get(key, '')
        for key in REFERENCE_FIELDS
    }
    # 添加 species_guid 用于关联主表
    reference_record['species_guid'] = species_guid
    # 添加 id 字段，设为 None，由数据库自增
    reference_record['id'] = None

    return reference_record


# === 主处理逻辑 ===
def clean_pest_relation_data():
    """
    主函数：清洗 pest_relation 目录下的 pest_relation_batch_1.json 文件，并保存为 CSV。
    """
    # 指定要处理的文件
    filename = 'pest_relation_batch_1.json'
    filepath = os.path.join(INPUT_DIR, filename)
    print(f"正在处理文件: {filename}")

    # 读取 JSON 文件
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"错误: 无法读取文件 {filename}: {e}")
        return

    # 初始化主表和引用表数据
    association_data = []
    reference_data = []

    # 处理每条记录
    for record in data:
        # 处理主表数据
        association_record = process_association_record(record)
        association_data.append(association_record)

        # 处理引用表数据（如果存在 cankao 字段）
        if 'cankao' in record and record['cankao']:
            reference_record = process_reference_record(record)
            reference_data.append(reference_record)

    # 将数据转换为 DataFrame
    association_df = pd.DataFrame(association_data)
    reference_df = pd.DataFrame(reference_data)

    # 提取批次编号
    batch_num = filename.split('_')[-1].split('.')[0]

    # 保存主表 CSV 文件
    association_df.to_csv(
        os.path.join(OUTPUT_DIR, f'species_association_batch_{batch_num}.csv'),
        index=False,
        encoding='utf-8-sig'  # 使用 utf-8-sig 避免中文乱码
    )

    # 保存引用表 CSV 文件（如果有数据）
    if not reference_df.empty:
        reference_df.to_csv(
            os.path.join(OUTPUT_DIR, f'reference_relation_batch_{batch_num}.csv'),
            index=False,
            encoding='utf-8-sig'
        )

    print(f"完成处理文件: {filename}，生成 CSV 文件: "
          f"species_association_batch_{batch_num}.csv 和 "
          f"reference_relation_batch_{batch_num}.csv（如果有引用数据）")


# === 脚本入口 ===
if __name__ == "__main__":
    clean_pest_relation_data()