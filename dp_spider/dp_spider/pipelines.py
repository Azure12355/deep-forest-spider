import json
import os

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
