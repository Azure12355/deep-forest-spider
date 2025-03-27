from itertools import count

import scrapy
import json
import os
from ..items import SpeciesBasicInfoItem, CankaoItem


class SpeciesBasicInfoSpider(scrapy.Spider):
    name = 'species_basicinfo'
    allowed_domains = ['www.pestchina.com']
    start_url = 'http://www.pestchina.com/webapi/nb/SpeciesBasicInfo/list'
    count = 0

    def start_requests(self):
        """读取species_id文件夹下的所有JSON文件并发起请求"""
        species_id_dir = 'data/species_id'  # 物种ID文件夹路径
        species_ids = []

        # 遍历文件夹，读取所有JSON文件中的物种ID
        for filename in os.listdir(species_id_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(species_id_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    species_ids.extend(data)

        # 为每个物种ID生成初始请求
        for species_id in species_ids:
            form_data = {
                'SC_GUID': species_id,
                'needCk': 'true',
                'paging[pagecount]': '200',  # 每页20条记录
                'paging[pagenum]': '1',  # 从第1页开始
                'paging[totalpage]': '0'  # 初始总页数为0
            }
            yield scrapy.FormRequest(
                url=self.start_url,
                formdata=form_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                callback=self.parse,
                meta={'species_id': species_id, 'pagenum': 1}
            )

    def parse(self, response):
        """解析API响应，提取数据并处理分页"""
        data = json.loads(response.text)
        content = data.get('content', [])

        # 遍历content列表，提取每条记录
        for item_data in content:
            item = SpeciesBasicInfoItem()
            item['rowid'] = item_data.get('rowid')
            item['TP_GUID'] = item_data.get('TP_GUID')
            item['SC_GUID'] = item_data.get('SC_GUID')
            item['SSNameSci'] = item_data.get('SSNameSci')
            item['SEName'] = item_data.get('SEName')
            item['BiologicalProperties'] = item_data.get('BiologicalProperties')
            item['MorphologicalCharacteristics'] = item_data.get('MorphologicalCharacteristics')
            item['DetectionMethod'] = item_data.get('DetectionMethod')
            item['DistributionDescription'] = item_data.get('DistributionDescription')
            item['ICodeID'] = item_data.get('ICodeID')
            item['ICodeName'] = item_data.get('ICodeName')
            item['Page'] = item_data.get('Page')
            item['Remark'] = item_data.get('Remark')
            item['TP_AUTHOR'] = item_data.get('TP_AUTHOR')
            item['TP_CREATED'] = item_data.get('TP_CREATED')
            item['TP_EDITOR'] = item_data.get('TP_EDITOR')
            item['TP_MODIFIED'] = item_data.get('TP_MODIFIED')
            item['Temp_CREATED'] = item_data.get('Temp_CREATED')
            item['Temp_Morp'] = item_data.get('Temp_Morp')

            # 处理嵌套的cankao字段
            cankao_data = item_data.get('cankao')
            if cankao_data:
                cankao_item = CankaoItem()
                cankao_item['Icode'] = cankao_data.get('Icode')
                cankao_item['Title'] = cankao_data.get('Title')
                cankao_item['SourceTitle'] = cankao_data.get('SourceTitle')
                cankao_item['IssueAuthor'] = cankao_data.get('IssueAuthor')
                cankao_item['AuthorDisplay'] = cankao_data.get('AuthorDisplay')
                cankao_item['ITypes1'] = cankao_data.get('ITypes1')
                cankao_item['ITypes'] = cankao_data.get('ITypes')
                cankao_item['ITypes2'] = cankao_data.get('ITypes2')
                cankao_item['KeyWord'] = cankao_data.get('KeyWord')
                cankao_item['CCname'] = cankao_data.get('CCname')
                cankao_item['PubTime'] = cankao_data.get('PubTime')
                cankao_item['Publisher'] = cankao_data.get('Publisher')
                cankao_item['Derivation'] = cankao_data.get('Derivation')
                cankao_item['TypeCode'] = cankao_data.get('TypeCode')
                cankao_item['ExecuteDate'] = cankao_data.get('ExecuteDate')
                cankao_item['Reference'] = cankao_data.get('Reference')
                cankao_item['AbstractDesc'] = cankao_data.get('AbstractDesc')
                cankao_item['TP_AUTHOR'] = cankao_data.get('TP_AUTHOR')
                cankao_item['TP_CREATED'] = cankao_data.get('TP_CREATED')
                cankao_item['TP_EDITOR'] = cankao_data.get('TP_EDITOR')
                cankao_item['TP_MODIFIED'] = cankao_data.get('TP_MODIFIED')
                cankao_item['PublishPerson'] = cankao_data.get('PublishPerson')
                cankao_item['PublishTime'] = cankao_data.get('PublishTime')
                cankao_item['Status'] = cankao_data.get('Status')
                item['cankao'] = cankao_item

            self.count += 1
            print(f'✅ 成功爬取数据第{self.count}条, SSNameSci={item["SSNameSci"]}')
            yield item

        # 处理分页
        paging = data.get('paging', {})
        pagenum = int(paging.get('pagenum', 1))
        totalpage = int(paging.get('totalpage', 0))
        if pagenum < totalpage:
            next_pagenum = pagenum
            form_data = {
                'SC_GUID': response.meta['species_id'],
                'needCk': 'true',
                'paging[pagecount]': '20',
                'paging[pagenum]': str(next_pagenum),
                'paging[totalpage]': str(totalpage)
            }
            yield scrapy.FormRequest(
                url=self.start_url,
                formdata=form_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                callback=self.parse,
                meta={'species_id': response.meta['species_id'], 'pagenum': next_pagenum}
            )