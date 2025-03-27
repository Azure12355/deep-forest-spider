import json
import os
from pathlib import Path

from itemadapter import ItemAdapter
from scrapy.utils import spider

from .items import CankaoItem


class JsonBatchPipeline:
    def __init__(self):
        self.batch_size = 5000
        self.data_buffer = []
        self.file_counter = 1
        self.output_dir = 'data/pests_list'

    def open_spider(self, spider):
        os.makedirs(self.output_dir, exist_ok=True)

    def process_item(self, item, spider):
        self.data_buffer.append(dict(item))
        if len(self.data_buffer) >= self.batch_size:
            self._flush_buffer()
        return item

    def close_spider(self, spider):
        if self.data_buffer:
            self._flush_buffer()

    def _flush_buffer(self):
        filename = os.path.join(self.output_dir, f'pests_batch_{self.file_counter}.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data_buffer, f, ensure_ascii=False, indent=2)
        self.data_buffer = []
        self.file_counter += 1
        spider.logger.info(f'已保存批次文件：{filename}')


class MetaInfoJsonBatchPipeline:
    def __init__(self):
        self.batch_size = 5000
        self.data_buffer = []
        self.batch_count = 1

        # 创建输出目录
        output_dir = 'data/meta_info_list'
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def process_item(self, item, spider):
        self.data_buffer.append(ItemAdapter(item).asdict())
        if len(self.data_buffer) >= self.batch_size:
            self.flush_buffer()
        return item

    def close_spider(self, spider):
        if self.data_buffer:
            self.flush_buffer()

    def flush_buffer(self):
        """写入文件并清空缓冲区"""
        filename = os.path.join(self.output_dir, f'meta_batch_{self.batch_count}.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data_buffer, f, ensure_ascii=False, indent=2)

        spider.logger.info(f'✅ 成功写入批次 {self.batch_count}（{len(self.data_buffer)}条）')
        self.data_buffer = []
        self.batch_count += 1


class SpeciesDistributionPipeline:
    """物种分布数据存储管道"""

    def __init__(self):
        self.batch_size = 5000  # 每个文件存储量
        self.file_counter = 1  # 文件序号
        self.data_buffer = []  # 数据缓存
        self.output_dir = Path('data/species_distribution')  # 存储目录

        # 创建存储目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_item(self, item, spider):
        """处理每个Item"""
        if spider.name != 'species_distribution':
            return item

        # 转换嵌套的Item对象为字典
        item_dict = dict(item)
        if 'Icodes' in item_dict:
            item_dict['Icodes'] = [
                dict(icode) for icode in item_dict['Icodes']
            ]

        self.data_buffer.append(item_dict)

        # 达到批次数量时写入文件
        if len(self.data_buffer) >= self.batch_size:
            self.flush_buffer()

        return item

    def close_spider(self, spider):
        """爬虫关闭时处理剩余数据"""
        if spider.name == 'species_distribution' and self.data_buffer:
            self.flush_buffer()

    def flush_buffer(self):
        """将缓存数据写入文件"""
        filename = f'species_distribution_batch_{self.file_counter}.json'
        file_path = self.output_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data_buffer, f, ensure_ascii=False, indent=2)

        spider.logger.info(f'已写入 {len(self.data_buffer)} 条数据到 {file_path}')
        print(f'已写入 {len(self.data_buffer)} 条数据到 {file_path}')
        self.data_buffer = []
        self.file_counter += 1


class SpeciesBasicInfoPipeline:
    def __init__(self):
        self.items = []  # 存储Item的列表
        self.file_count = 0  # 文件编号
        self.item_count = 0  # 当前记录数
        self.max_items_per_file = 10  # 每个文件最大记录数
        self.output_dir = 'data/species_relationinfo'  # 输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def process_item(self, item, spider):
        """处理每个 item，将其转换为字典并处理嵌套的 cankao 字段"""
        # 将顶层 item 转换为字典
        item_dict = dict(item)

        # 检查 'cankao' 是否存在且不为空，然后将其转换为字典
        if 'cankao' in item_dict and item_dict['cankao']:
            item_dict['cankao'] = dict(item_dict['cankao'])

        # 将完全转换后的字典添加到 items 列表
        self.items.append(item_dict)


        self.item_count += 1
        if self.item_count >= self.max_items_per_file:
            self.save_to_json()
            self.items = []
            self.item_count = 0
            self.file_count += 1
        return item

    def close_spider(self, spider):
        """爬虫结束时保存剩余的Item"""
        if self.items:
            self.save_to_json()

    def save_to_json(self):
        """将Item列表保存到JSON文件"""
        filename = f'species_relationinfo_batch_{self.file_count}.json'
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=4)


class SpeciesHostPipeline:
    def __init__(self):
        """
        初始化Pipeline，设置存储参数
        """
        self.items = []  # 暂存Item的列表
        self.batch_size = 5000  # 每批保存5000条数据
        self.batch_count = 1  # 文件批次编号
        # 输出目录路径
        self.output_dir = 'data/species_host_list'  # 输出目录
        os.makedirs(self.output_dir, exist_ok=True)  # 创建目录（如果不存在）

    def process_item(self, item, spider):
        """
        处理每个Item，添加到列表并检查是否需要保存
        """
        # 将Item转换为字典
        item_dict = dict(item)
        # 处理嵌套的Icodes字段，转换为字典列表
        if 'Icodes' in item_dict:
            item_dict['Icodes'] = [dict(icode) for icode in item_dict['Icodes']]
        self.items.append(item_dict)
        # 如果达到批次大小，保存数据
        if len(self.items) >= self.batch_size:
            self.save_batch()
        return item

    def save_batch(self):
        """
        将当前批次数据保存为JSON文件
        """
        filename = f'species_host_batch_{self.batch_count}.json'  # 文件名
        filepath = os.path.join(self.output_dir, filename)  # 文件路径
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)  # 保存为JSON
        self.items = []  # 清空列表
        self.batch_count += 1  # 增加批次编号

    def close_spider(self, spider):
        """
        爬虫关闭时，保存剩余数据
        """
        if self.items:
            self.save_batch()


class SpeciesParentPipeline:
    def __init__(self):
        """初始化管道，设置批次大小和输出目录"""
        self.items = []  # 存储 Item 的列表
        self.batch_size = 100  # 每批保存 5000 条数据
        self.batch_num = 1  # 当前批次编号
        self.output_dir = 'data/species_parent_list'  # 输出目录
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def process_item(self, item, spider):
        """处理每个 Item，添加到列表并在达到批次大小时保存"""
        self.items.append(dict(item))  # 将 Item 转换为字典
        if len(self.items) >= self.batch_size:
            self.save_to_json()
        return item

    def close_spider(self, spider):
        """爬虫关闭时保存剩余的 Item"""
        if self.items:
            self.save_to_json()

    def save_to_json(self):
        """将当前批次的 Item 保存到 JSON 文件"""
        filename = f'species_parent_batch_{self.batch_num}.json'
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)  # 保存为 JSON 文件
        self.items = []  # 清空列表
        self.batch_num += 1  # 增加批次编号


class PestRelationPipeline:
    def __init__(self):
        self.items = []
        self.file_count = 1
        self.item_count = 0
        self.max_items_per_file = 5000
        self.output_dir = 'data/pest_relation'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def process_item(self, item, spider):
        """处理每个项目，并在达到 5000 个项目时保存到文件。"""
        # 将 item 转换为字典，并处理嵌套的 cankao 字段
        item_dict = dict(item)
        if 'cankao' in item_dict and item_dict['cankao'] is not None:
            item_dict['cankao'] = dict(item_dict['cankao'])  # 将 CankaoItem 转换为普通字典

        self.items.append(item_dict)
        self.item_count += 1
        if self.item_count >= self.max_items_per_file:
            self.save_to_file()
            self.items = []
            self.item_count = 0
            self.file_count += 1
        return item

    def close_spider(self, spider):
        """在爬虫关闭时保存剩余的项目。"""
        if self.items:
            self.save_to_file()

    def save_to_file(self):
        """将收集的项目保存到 JSON 文件。"""
        filename = f'pest_relation_batch_{self.file_count}.json'
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=4)



class PestHostPartPipeline:
    def __init__(self):
        self.items = []  # 存储爬取的Item
        self.batch_size = 2000  # 每批保存的记录数
        self.batch_num = 1  # 批次编号
        self.output_dir = os.path.join('data', 'pest_host_part_list')  # 输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)  # 创建目录如果不存在

    def process_item(self, item, spider):
        """处理每个Item，转换为可序列化的字典并累积到列表中"""
        # 将Item转换为字典，并处理嵌套的Icodes字段
        item_dict = dict(item)
        item_dict['Icodes'] = [dict(icode) for icode in item['Icodes']]  # 将每个ICodeItem转换为字典
        self.items.append(item_dict)  # 添加到列表
        if len(self.items) >= self.batch_size:
            self.save_batch()  # 达到5000条时保存
        return item

    def close_spider(self, spider):
        """爬虫关闭时保存剩余数据"""
        if self.items:
            self.save_batch()

    def save_batch(self):
        """保存当前批次数据到JSON文件"""
        filename = f'pest_host_part_batch_{self.batch_num}.json'
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=4)  # 保存为格式化的JSON
        self.items = []  # 清空列表
        self.batch_num += 1  # 增加批次编号


class CmDiffuseMediumPipeline:
    def __init__(self):
        self.items = []  # 存储爬取的Item
        self.batch_size = 200  # 每批保存的记录数
        self.batch_num = 1  # 批次编号
        self.output_dir = os.path.join('data', 'cm_diffuse_medium_list')  # 输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)  # 创建目录如果不存在

    def process_item(self, item, spider):
        """处理每个Item，转换为字典并累积到列表中"""
        self.items.append(dict(item))  # 将Item转换为字典并添加
        if len(self.items) >= self.batch_size:
            self.save_batch()  # 达到5000条时保存
        return item

    def close_spider(self, spider):
        """爬虫关闭时保存剩余数据"""
        if self.items:
            self.save_batch()

    def save_batch(self):
        """保存当前批次数据到JSON文件"""
        filename = f'cm_diffuse_medium_batch_{self.batch_num}.json'
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=4)  # 保存为格式化的JSON
        self.items = []  # 清空列表
        self.batch_num += 1  # 增加批次编号