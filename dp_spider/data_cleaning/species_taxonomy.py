# -*- coding: utf-8 -*-
import json
import os
import pandas as pd

# === 全局配置 ===
# 输入目录：存放原始 JSON 文件
INPUT_DIR = 'data/species_parent_list'
# 输出目录：存放清洗后的 CSV 文件
OUTPUT_DIR = 'cleaned_data/species_taxonomy'

# 创建输出目录（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 物种分类层级表字段映射关系（species_taxonomy）
TAXONOMY_FIELDS = {
    'species_TP_GUID': 'species_guid',
    'TP_GUID': 'taxonomy_guid',
    'SLevel': 'taxonomy_level',
    'SSNameSci': 'scientific_name',
    'SCName': 'chinese_name',
    'SClass': 'taxonomy_class',
    'ParentSsName': 'parent_scientific_name'
}


# === 数据处理函数 ===
def process_taxonomy_record(record):
    """
    处理单个物种分类层级记录，映射到数据库字段。

    参数:
        record (dict): JSON 中的单条记录
    返回:
        dict: 映射后的分类层级记录
    """
    # 根据字段映射提取数据，缺失字段填充为空字符串
    taxonomy_record = {
        TAXONOMY_FIELDS.get(key, key): record.get(key, '')
        for key in TAXONOMY_FIELDS
    }
    # 添加 id 字段，设为 None，由数据库自增
    taxonomy_record['id'] = None
    return taxonomy_record


# === 主处理逻辑 ===
def clean_species_taxonomy_data():
    """
    主函数：清洗 species_parent_list 目录下的所有 JSON 文件，并保存为 CSV。
    """
    # 遍历输入目录下的所有 JSON 文件
    for filename in os.listdir(INPUT_DIR):
        if filename.startswith('species_parent_batch_') and filename.endswith('.json'):
            filepath = os.path.join(INPUT_DIR, filename)
            print(f"正在处理文件: {filename}")

            # 读取 JSON 文件
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"错误: 无法读取文件 {filename}: {e}")
                continue

            # 初始化当前批次的分类层级数据
            taxonomy_data = []

            # 处理每条记录
            for record in data:
                taxonomy_record = process_taxonomy_record(record)
                taxonomy_data.append(taxonomy_record)

            # 将数据转换为 DataFrame
            taxonomy_df = pd.DataFrame(taxonomy_data)

            # 提取批次编号
            batch_num = filename.split('_')[-1].split('.')[0]

            # 保存 CSV 文件
            taxonomy_df.to_csv(
                os.path.join(OUTPUT_DIR, f'species_taxonomy_batch_{batch_num}.csv'),
                index=False,
                encoding='utf-8-sig'  # 使用 utf-8-sig 避免中文乱码
            )

            print(f"完成处理文件: {filename}，生成 CSV 文件: species_taxonomy_batch_{batch_num}.csv")

    print("所有文件处理完成！")


# === 脚本入口 ===
if __name__ == "__main__":
    clean_species_taxonomy_data()