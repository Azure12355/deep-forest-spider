# -*- coding: utf-8 -*-
import json
import os
import pandas as pd

# === 全局配置 ===
# 输入目录：存放原始 JSON 文件
INPUT_DIR = 'data/species_distribution'
# 输出目录：存放清洗后的 CSV 文件
OUTPUT_DIR = 'cleaned_data/species_distribution'

# 创建输出目录（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 主表字段映射关系
DISTRIBUTION_FIELDS = {
    'species_id': 'species_guid',
    'CCnameContinent': 'continent_name',
    'CCnameCountry': 'country_name',
    'CCnameProvince': 'province_name',
    'Descrip': 'description'
}

# 引用表字段映射关系
REFERENCE_FIELDS = {
    'ICodeID': 'icode',
    'AuthorDisplay': 'author_display',
    'Title': 'title'
}


# === 数据处理函数 ===
def process_distribution_record(record):
    """
    处理单个物种分布记录，映射到主表字段。

    参数:
        record (dict): JSON 中的单条记录
    返回:
        dict: 映射后的主表记录
    """
    # 根据字段映射提取数据，缺失字段填充为空字符串
    distribution_record = {
        DISTRIBUTION_FIELDS.get(key, key): record.get(key, '')
        for key in DISTRIBUTION_FIELDS
    }
    # 添加 id 字段，设为 None，由数据库自增
    distribution_record['id'] = None
    return distribution_record


def process_reference_records(record):
    """
    处理物种分布记录中的引用信息 (Icodes)，映射到引用表字段。

    参数:
        record (dict): JSON 中的单条记录
    返回:
        list: 包含所有引用记录的列表
    """
    species_guid = record['species_id']
    reference_data = []

    # 检查 Icodes 字段是否存在，若无则返回空列表
    icodes_list = record.get('Icodes', [])
    for icode in icodes_list:
        # 映射引用表字段，缺失字段填充为空字符串
        reference_record = {
            REFERENCE_FIELDS.get(key, key): icode.get(key, '')
            for key in REFERENCE_FIELDS
        }
        # 添加 species_guid 用于关联主表
        reference_record['species_guid'] = species_guid
        # 添加 id 字段，设为 None，由数据库自增
        reference_record['id'] = None
        reference_data.append(reference_record)

    return reference_data


# === 主处理逻辑 ===
def clean_species_distribution_data():
    """
    主函数：清洗 species_distribution 目录下的所有 JSON 文件，并保存为 CSV。
    """
    # 遍历输入目录下的所有 JSON 文件
    for filename in os.listdir(INPUT_DIR):
        if filename.startswith('species_distribution_batch_') and filename.endswith('.json'):
            filepath = os.path.join(INPUT_DIR, filename)
            print(f"正在处理文件: {filename}")

            # 读取 JSON 文件
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"错误: 无法读取文件 {filename}: {e}")
                continue

            # 初始化当前批次的主表和引用表数据
            distribution_data = []
            reference_data = []

            # 处理每条记录
            for record in data:
                # 处理主表数据
                distribution_record = process_distribution_record(record)
                distribution_data.append(distribution_record)

                # 处理引用表数据
                references = process_reference_records(record)
                reference_data.extend(references)

            # 将数据转换为 DataFrame
            distribution_df = pd.DataFrame(distribution_data)
            reference_df = pd.DataFrame(reference_data)

            # 提取批次编号
            batch_num = filename.split('_')[-1].split('.')[0]

            # 保存主表 CSV 文件
            distribution_df.to_csv(
                os.path.join(OUTPUT_DIR, f'species_distribution_batch_{batch_num}.csv'),
                index=False,
                encoding='utf-8-sig'  # 使用 utf-8-sig 避免中文乱码
            )

            # 保存引用表 CSV 文件
            reference_df.to_csv(
                os.path.join(OUTPUT_DIR, f'reference_relation_batch_{batch_num}.csv'),
                index=False,
                encoding='utf-8-sig'
            )

            print(f"完成处理文件: {filename}，生成 CSV 文件: "
                  f"species_distribution_batch_{batch_num}.csv 和 "
                  f"reference_relation_batch_{batch_num}.csv")

    print("所有文件处理完成！")


# === 脚本入口 ===
if __name__ == "__main__":
    clean_species_distribution_data()