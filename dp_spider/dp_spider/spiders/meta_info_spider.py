import json
from pathlib import Path

import scrapy
from scrapy.utils import spider
from scrapy.spiders import CrawlSpider

from ..items import MetaInfoItem, YMMetaItem


class MetaInfoSpiderSpider(CrawlSpider):
    name = "meta_info_spider"
    allowed_domains = ['www.pestchina.com']
    custom_settings = {
        'DOWNLOAD_DELAY': 0,  # 礼貌爬取间隔
        'CONCURRENT_REQUESTS': 5000  # 并发数
    }
    count = 0

    def start_requests(self):
        # 计算pests_list目录绝对路径
        project_root = Path(__file__).parent.parent.parent.parent
        species_id_dir = project_root / 'dp_spider' / 'data' / 'species_id'

        # 遍历所有批次文件
        for batch_file in species_id_dir.glob('species_ids_*.json'):
            with open(batch_file, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
                for guid in batch_data:
                    yield self.build_request(guid)

    def build_request(self, guid):
        """构建带请求头的API请求"""
        url = f'http://www.pestchina.com/webapi/nb/home/code/detail/{guid}'
        headers = {
            'Accept': '/',
            'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7',
            'Referer': 'http://www.pestchina.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        return scrapy.Request(
            url,
            headers=headers,
            meta={'dont_verify_ssl': 1},  # 禁用SSL验证
            callback=self.parse_meta
        )

    def parse_meta(self, response):
        """解析元信息接口"""
        data = response.json()
        item = MetaInfoItem()

        # 直接映射字段
        direct_fields = [
            'TP_GUID', 'SSNameSci', 'SSName', 'NamedYear', 'SCName',
            'SEName', 'SENameAbb', 'SClass', 'ParentSsName', 'SLevel',
            'SLevel2', 'Source', 'Status', 'Checker', 'CheckTime',
            'OrgRiskCode', 'IsSpecies', 'TP_AUTHOR', 'TP_CREATED',
            'TP_EDITOR', 'TP_MODIFIED', 'Temp_CREATED'
        ]
        for field in direct_fields:
            item[field] = data.get(field)

        # 处理异名列表
        ym_list = []
        for ym_data in data.get('ym', []):
            ym_item = YMMetaItem()
            ym_item['SONType'] = ym_data.get('SONType')
            ym_item['NamedYear'] = ym_data.get('NamedYear')
            ym_item['SOtherNameSci'] = ym_data.get('SOtherNameSci')
            ym_list.append(dict(ym_item))
        item['ym'] = ym_list
        self.count += 1
        spider.logger.info(f'✅ 成功爬取数据第{self.count}条）')
        print(f'✅ 成功爬取数据第{self.count}条, SCName={item["SCName"]}')
        return item
