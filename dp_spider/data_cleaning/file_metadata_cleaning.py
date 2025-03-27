import json
import csv
import os

# 定义输入和输出目录
# 输入目录：原始 JSON 文件所在路径
input_dir = 'data/file_metadata_list'
# 输出目录：清洗后的 CSV 文件保存路径
output_dir = 'cleaned_data/file_metadata'

# 确保输出目录存在，如果不存在则创建
os.makedirs(output_dir, exist_ok=True)

# 处理的 JSON 文件名
json_file = 'file_metadata_batch_1.json'
json_path = os.path.join(input_dir, json_file)

# 对应的 CSV 输出文件名，保持与 JSON 文件名一致，仅更改扩展名
csv_file = json_file.replace('.json', '.csv')
csv_path = os.path.join(output_dir, csv_file)

# 数据库字段映射关系
# 原始字段 -> 数据库字段，基于提供的映射表
field_mapping = {
    'icode': 'icode',
    'name': 'name',
    'url': 'url'
}

# 数据库表字段列表，包含自增的 id 字段
db_fields = ['id', 'icode', 'name', 'url']

# 读取 JSON 数据
# 使用 utf-8 编码以支持中文字符
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 初始化自增 id，从 1 开始
current_id = 1

# 准备写入 CSV 文件
# 使用 utf-8 编码并添加 newline='' 参数，避免多余空行
with open(csv_path, 'w', encoding='utf-8', newline='') as csvfile:
    # 创建 CSV 写入器，指定字段名
    writer = csv.DictWriter(csvfile, fieldnames=db_fields)
    # 写入表头
    writer.writeheader()

    # 遍历 JSON 数据中的每条记录
    for item in data:
        # 创建新的记录字典，用于存储清洗后的数据
        record = {
            'id': current_id,              # 自增 id，作为主键
            'icode': item.get('icode'),    # 获取 icode 字段，确保类型为字符串
            'name': item.get('name'),      # 获取 name 字段，文件名
            'url': item.get('url')         # 获取 url 字段，文件路径
        }

        # 数据类型检查与转换
        # 确保 icode 为整数类型（BIGINT），如果缺失或无法转换则设为 None
        if record['icode'] is not None:
            try:
                record['icode'] = int(record['icode'])
            except (ValueError, TypeError):
                record['icode'] = None  # 如果转换失败，设为 None，避免程序崩溃

        # 确保 name 和 url 为字符串类型（VARCHAR），如果缺失则设为空字符串
        record['name'] = str(record['name']) if record['name'] is not None else ''
        record['url'] = str(record['url']) if record['url'] is not None else ''

        # 将清洗后的记录写入 CSV
        writer.writerow(record)
        # id 自增
        current_id += 1

# 打印完成信息，确认操作成功
print(f"数据清洗完成，保存为 {csv_path}")