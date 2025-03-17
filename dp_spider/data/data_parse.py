# data_parse.py
import json
from pathlib import Path
import traceback


def process_pest_files():
    # 路径配置
    BASE_DIR = Path(__file__).parent
    INPUT_DIR = BASE_DIR / "pests_list"
    OUTPUT_DIR = BASE_DIR / "species_id"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)  # 自动创建输出目录

    # 分块参数
    CHUNK_SIZE = 5000
    current_chunk = []
    file_counter = 1

    # 获取并排序输入文件 (自然排序处理 pests_batch_1 ~ pests_batch_20)
    input_files = sorted(
        INPUT_DIR.glob("pests_batch_*.json"),
        key=lambda x: int(x.stem.split("_")[-1])
    )

    # 处理每个输入文件
    for input_file in input_files:
        print(f"🔄 正在处理文件: {input_file.name}")

        try:
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)

                # 验证数据结构
                if not isinstance(data, list):
                    print(f"⚠️ 文件结构异常: {input_file.name} 顶层不是数组")
                    continue

                # 提取所有GUID
                for idx, item in enumerate(data, 1):
                    guid = item.get("TP_GUID")

                    if guid:
                        current_chunk.append(guid)
                        # 达到分块大小时写入文件
                        if len(current_chunk) >= CHUNK_SIZE:
                            save_chunk(current_chunk[:CHUNK_SIZE], file_counter, OUTPUT_DIR)
                            current_chunk = current_chunk[CHUNK_SIZE:]
                            file_counter += 1
                    else:
                        print(f"⏩ 跳过第 {idx} 条数据: 缺失 TP_GUID 字段")

        except json.JSONDecodeError:
            print(f"❌ JSON解析失败: {input_file.name}")
            traceback.print_exc()
        except Exception as e:
            print(f"‼️ 处理文件异常: {input_file.name}")
            traceback.print_exc()

    # 写入剩余数据
    if current_chunk:
        save_chunk(current_chunk, file_counter, OUTPUT_DIR)

    print(f"✅ 处理完成! 共生成 {file_counter} 个文件")


def save_chunk(data_chunk, counter, output_dir):
    """保存数据块到指定目录"""
    output_path = output_dir / f"species_ids_{counter}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data_chunk, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存: {output_path.name} ({len(data_chunk)} 条数据)")


if __name__ == "__main__":
    process_pest_files()
