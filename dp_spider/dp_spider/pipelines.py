import json
import os
from pathlib import Path

from itemadapter import ItemAdapter
from scrapy.utils import spider


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
