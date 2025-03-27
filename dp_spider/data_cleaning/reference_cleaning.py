import os
import csv
from pathlib import Path

# 定义cleaned_data目录路径（相对于项目根目录）
CLEANED_DATA_DIR = Path('cleaned_data')

# 定义输出文件路径
OUTPUT_FILE = CLEANED_DATA_DIR / 'reference_relation.csv'


def collect_icodes():
    """
    收集所有以'reference'开头的CSV文件中的icode字段并去重
    返回值：去重后的icode集合
    """
    icodes = set()  # 使用集合自动去重

    # 递归遍历cleaned_data目录及其子目录
    for root, dirs, files in os.walk(CLEANED_DATA_DIR):
        for file in files:
            # 检查文件名是否以'reference'开头且以'.csv'结尾
            if file.startswith('reference') and file.endswith('.csv'):
                file_path = Path(root) / file
                try:
                    # 以utf-8编码打开CSV文件，防止中文字符乱码
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        # 检查文件是否包含'icode'字段
                        if 'icode' not in reader.fieldnames:
                            print(f"警告: 文件 {file_path} 不包含 'icode' 字段，已跳过")
                            continue
                        # 逐行读取并提取icode字段
                        for row in reader:
                            icode = row['icode'].strip()  # 去除首尾空白字符
                            if icode:  # 忽略空值
                                icodes.add(icode)
                except FileNotFoundError:
                    print(f"错误: 文件 {file_path} 不存在，已跳过")
                except PermissionError:
                    print(f"错误: 无权限访问文件 {file_path}，已跳过")
                except Exception as e:
                    print(f"错误: 读取文件 {file_path} 时出错，原因: {e}，已跳过")

    return icodes


def write_to_csv(icodes):
    """
    将去重后的icode写入到reference_relation.csv文件中
    参数：
        icodes: 去重后的icode集合
    """
    try:
        # 以utf-8编码写入CSV文件，添加newline=''以避免多余空行
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(['icode'])
            # 按字母顺序排序后写入数据
            for icode in sorted(icodes):
                writer.writerow([icode])
    except PermissionError:
        print(f"错误: 无权限写入文件 {OUTPUT_FILE}")
    except Exception as e:
        print(f"错误: 写入文件 {OUTPUT_FILE} 时出错，原因: {e}")


def main():
    """主函数，执行数据清洗操作"""
    print("开始收集icode数据...")
    icodes = collect_icodes()
    print(f"共收集到 {len(icodes)} 个唯一的icode")

    if icodes:
        print("开始写入CSV文件...")
        write_to_csv(icodes)
        print(f"数据已成功保存到 {OUTPUT_FILE}")
    else:
        print("未找到任何有效的icode数据，未生成输出文件")


if __name__ == "__main__":
    main()