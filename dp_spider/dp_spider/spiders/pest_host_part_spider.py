from importlib.metadata import metadata

import scrapy
import json
import os
from ..items import PestHostPartItem, ICodeItem

class PestHostPartSpider(scrapy.Spider):
    name = 'pest_host_part'  # 爬虫名称
    allowed_domains = ['www.pestchina.com']  # 限制爬取域名
    start_urls = ['http://www.pestchina.com/webapi/nb/PestHostPart/list/concat']  # 目标接口URL
    count = 0

    # 自定义设置，启用Pipeline
    custom_settings = {
        'ITEM_PIPELINES': {
            'dp_spider.pipelines.PestHostPartPipeline': 300,
        }
    }

    def __init__(self, *args, **kwargs):
        super(PestHostPartSpider, self).__init__(*args, **kwargs)
        self.species_ids = self.load_species_ids()  # 初始化时加载所有物种ID

    def load_species_ids(self):
        """读取species_id文件夹下的所有JSON文件，获取物种ID列表"""
        species_ids = []
        species_id_dir = os.path.join('data', 'species_id')  # 物种ID目录
        for filename in os.listdir(species_id_dir):
            if filename.endswith('.json'):
                with open(os.path.join(species_id_dir, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    species_ids.extend(data)  # 将每个文件中的ID添加到列表
        return species_ids

    def start_requests(self):
        """为每个物种ID发起初始POST请求"""
        for species_id in self.species_ids:
            form_data = {
                'SC_GUID': species_id,  # 物种ID
                'paging[pagecount]': '18',  # 每页记录数，固定为18
                'paging[pagenum]': '1',  # 初始页码
                'paging[totalpage]': '86'  # 初始总页数，实际值由响应动态调整
            }
            yield scrapy.FormRequest(
                url=self.start_urls[0],
                formdata=form_data,
                meta={'species_id': species_id, 'pagenum': 1},  # 传递物种ID和当前页码
                callback=self.parse
            )

    def parse(self, response):
        """解析响应，提取数据并处理分页"""
        data = json.loads(response.text)
        content = data.get('content', [])  # 获取害虫寄主部位列表

        # 遍历每条记录，创建Item
        for item in content:
            pest_host_part_item = PestHostPartItem()
            pest_host_part_item['species_id'] = response.meta['species_id']  # 添加物种ID
            pest_host_part_item['rowid'] = item.get('rowid')  # 行ID
            pest_host_part_item['PlantParts'] = item.get('PlantParts')  # 植物部位
            pest_host_part_item['Peststage'] = item.get('Peststage')  # 害虫阶段
            pest_host_part_item['VisibilityType'] = item.get('VisibilityType')  # 可见性类型
            pest_host_part_item['SpreadingWay'] = item.get('SpreadingWay')  # 传播方式

            # 处理嵌套的Icodes字段
            icodes = item.get('Icodes', [])
            pest_host_part_item['Icodes'] = [
                ICodeItem(
                    ICodeID=icode.get('ICodeID'),  # ICode标识符
                    AuthorDisplay=icode.get('AuthorDisplay')  # 作者信息
                ) for icode in icodes
            ]
            self.count += 1
            print(f'✅ 成功爬取数据第{self.count}条'
                  f'物种id：{response.meta["species_id"]}'
                  f'PlantParts={pest_host_part_item["PlantParts"]}')
            yield pest_host_part_item  # 提交Item到Pipeline

        # 处理分页
        paging = data.get('paging', {})
        totalpage = int(paging.get('totalpage', 0))  # 总页数
        pagenum = int(paging.get('pagenum', 0))  # 当前页码
        if pagenum < totalpage:
            next_pagenum = pagenum
            form_data = {
                'SC_GUID': response.meta['species_id'],
                'paging[pagecount]': '18',
                'paging[pagenum]': str(next_pagenum),
                'paging[totalpage]': str(totalpage)
            }
            yield scrapy.FormRequest(
                url=self.start_urls[0],
                formdata=form_data,
                meta={'species_id': response.meta['species_id'], 'pagenum': next_pagenum},
                callback=self.parse
            )