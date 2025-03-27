# -*- coding: utf-8 -*-
import json
import os
import pandas as pd

# === 全局配置 ===
# 输入目录：存放原始 JSON 文件的路径
INPUT_DIR = 'data/species_host_list'
# 输出目录：存放清洗后 CSV 文件的路径
OUTPUT_DIR = 'cleaned_data/species_host'

# 创建输出目录（如果不存在）
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 主表字段映射关系（species_host）
HOST_FIELDS = {
    'species_id': 'species_guid',  # CHAR(36), 物种全局唯一标识符
    'HOST_GUID': 'host_guid',  # CHAR(36), 寄主全局唯一标识符
    'HOST_NAME': 'host_name',  # VARCHAR(100), 寄主学名
    'HOST_NAME_CN': 'host_name_cn',  # VARCHAR(100), 寄主中文名
    'HostType': 'host_types'  # VARCHAR(255), 寄主类型
}

# 引用表字段映射关系（reference_relation）
REFERENCE_FIELDS = {
    'species_id': 'species_guid',  # CHAR(36), 物种全局唯一标识符
    'ICodeID': 'icode',  # BIGINT, 引用ID
    'AuthorDisplay': 'author_display',  # VARCHAR(255), 显示的作者
    'title': 'title'  # VARCHAR(255), 引用文献标题
}


# === 数据处理函数 ===
def process_host_record(record):
    """
    处理单条物种寄主记录，映射到 species_host 表字段。

    参数:
        record (dict): JSON 中的单条记录
    返回:
        dict: 映射后的主表记录
    """
    # 初始化主表记录，id 留空由数据库自增
    host_record = {
        'id': None,  # BIGINT, 自增主键，留空
        'species_guid': record.get('species_id', ''),  # 从 species_id 获取
        'host_guid': record.get('HOST_GUID', ''),  # 从 HOST_GUID 获取
        'host_name': record.get('HOST_NAME', ''),  # 从 HOST_NAME 获取
        'host_name_cn': record.get('HOST_NAME_CN', ''),  # 从 HOST_NAME_CN 获取
        'host_types': record.get('HostType', '')  # 从 HostType 获取
    }
    return host_record


def process_reference_records(record):
    """
    处理物种寄主记录中的引用信息 (Icodes)，映射到 reference_relation 表字段。

    参数:
        record (dict): JSON 中的单条记录
    返回:
        list: 包含所有引用记录的列表
    """
    species_guid = record.get('species_id', '')
    reference_data = []

    # 检查 Icodes 字段是否存在，若无则返回空列表
    icodes_list = record.get('Icodes', [])
    for icode in icodes_list:
        # 初始化引用表记录，id 留空由数据库自增
        reference_record = {
            'id': None,  # BIGINT, 自增主键，留空
            'species_guid': species_guid,  # 继承自主表的 species_id
            'icode': icode.get('ICodeID', ''),  # 从 ICodeID 获取，BIGINT 类型
            'author_display': icode.get('AuthorDisplay', ''),  # 从 AuthorDisplay 获取
            'title': icode.get('Title', '')  # 从 Title 获取，若无则为空
        }
        reference_data.append(reference_record)

    return reference_data


# === 主处理逻辑 ===
def clean_species_host_data():
    """
    主函数：清洗 species_host_list 目录下的所有 JSON 文件，并保存为 CSV。
    """
    # 遍历输入目录下的所有 JSON 文件
    for filename in os.listdir(INPUT_DIR):
        if filename.startswith('species_host_batch_') and filename.endswith('.json'):
            filepath = os.path.join(INPUT_DIR, filename)
            print(f"正在处理文件: {filename}")

            # 读取 JSON 文件并处理异常
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"错误: JSON 解析失败 {filename}: {e}")
                continue
            except Exception as e:
                print(f"错误: 无法读取文件 {filename}: {e}")
                continue

            # 初始化当前批次的主表和引用表数据
            host_data = []
            reference_data = []

            # 处理每条记录
            for record in data:
                # 处理主表数据
                host_record = process_host_record(record)
                host_data.append(host_record)

                # 处理引用表数据
                references = process_reference_records(record)
                reference_data.extend(references)

            # 将数据转换为 DataFrame
            host_df = pd.DataFrame(host_data)
            reference_df = pd.DataFrame(reference_data)

            # 提取批次编号（如 species_host_batch_1.json 中的 "1"）
            batch_num = filename.split('_')[-1].split('.')[0]

            # 保存主表 CSV 文件
            host_output_path = os.path.join(OUTPUT_DIR, f'species_host_batch_{batch_num}.csv')
            host_df.to_csv(
                host_output_path,
                index=False,
                encoding='utf-8-sig'  # 使用 utf-8-sig 避免中文乱码
            )

            # 保存引用表 CSV 文件
            reference_output_path = os.path.join(OUTPUT_DIR, f'reference_relation_batch_{batch_num}.csv')
            reference_df.to_csv(
                reference_output_path,
                index=False,
                encoding='utf-8-sig'
            )

            print(f"完成处理文件: {filename}，生成 CSV 文件: "
                  f"species_host_batch_{batch_num}.csv 和 "
                  f"reference_relation_batch_{batch_num}.csv")

    print("所有文件处理完成！")


# === 脚本入口 ===
if __name__ == "__main__":
    clean_species_host_data()