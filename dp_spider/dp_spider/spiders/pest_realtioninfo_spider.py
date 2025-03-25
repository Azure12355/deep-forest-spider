# dp_spider/spiders/pest_relation_spider.py
import scrapy
import json
import os
from ..items import PestRelationInfoItem, CankaoItem

class PestRelationSpider(scrapy.Spider):
    name = 'pest_relation'
    allowed_domains = ['www.pestchina.com']
    start_urls = ['http://www.pestchina.com/']
    count = 0

    def __init__(self, *args, **kwargs):
        super(PestRelationSpider, self).__init__(*args, **kwargs)
        self.species_ids = self.load_species_ids()

    def load_species_ids(self):
        """从 species_id 目录中的 JSON 文件加载所有物种 ID。"""
        species_ids = []
        species_id_dir = os.path.join(os.path.dirname(__file__), '../../data/species_id')
        for filename in os.listdir(species_id_dir):
            if filename.endswith('.json'):
                with open(os.path.join(species_id_dir, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    species_ids.extend(data)
        return species_ids

    def start_requests(self):
        """为每个物种 ID 生成初始 POST 请求。"""
        for species_id in self.species_ids:
            form_data = {
                'SC_GUID': species_id,
                'needCk': 'true',
                'paging[pagecount]': '20',
                'paging[pagenum]': '1',
                'paging[totalpage]': '0'
            }
            yield scrapy.FormRequest(
                url='http://www.pestchina.com/webapi/nb/PestRelationInfo/list',
                formdata=form_data,
                method='POST',
                headers={
                    'Accept': '*/*',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Origin': 'http://www.pestchina.com',
                    'Pragma': 'no-cache',
                    'Referer': 'http://www.pestchina.com/',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                callback=self.parse,
                meta={'species_id': species_id, 'pagenum': 1}
            )

    def parse(self, response):
        """解析 API 响应，生成项目，并处理分页。"""
        data = json.loads(response.text)
        content = data.get('content', [])
        paging = data.get('paging', {})

        for item_data in content:
            pest_item = PestRelationInfoItem()
            pest_item['rowid'] = item_data.get('rowid')
            pest_item['TP_GUID'] = item_data.get('TP_GUID')
            pest_item['SC_GUID'] = item_data.get('SC_GUID')
            pest_item['SSNameSci'] = item_data.get('SSNameSci')
            pest_item['PBCharHostRange'] = item_data.get('PBCharHostRange')
            pest_item['PotentialEcoDesc'] = item_data.get('PotentialEcoDesc')
            pest_item['Descrip'] = item_data.get('Descrip')
            pest_item['ManagementInfo'] = item_data.get('ManagementInfo')
            pest_item['Remark'] = item_data.get('Remark')
            pest_item['ICodeID'] = item_data.get('ICodeID')
            pest_item['ICodeName'] = item_data.get('ICodeName')
            pest_item['Page'] = item_data.get('Page')
            pest_item['TP_AUTHOR'] = item_data.get('TP_AUTHOR')
            pest_item['TP_CREATED'] = item_data.get('TP_CREATED')
            pest_item['TP_EDITOR'] = item_data.get('TP_EDITOR')
            pest_item['TP_MODIFIED'] = item_data.get('TP_MODIFIED')

            cankao_data = item_data.get('cankao', {})
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

            pest_item['cankao'] = cankao_item

            self.count += 1
            print(f'✅ 成功爬取数据第{self.count}条'
                  f'SCName={pest_item["SSNameSci"]}')
            yield pest_item

        # 处理分页
        totalpage = int(paging.get('totalpage', 0))
        pagenum = int(paging.get('pagenum', 1))
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
                url='http://www.pestchina.com/webapi/nb/PestRelationInfo/list',
                formdata=form_data,
                method='POST',
                headers={
                    'Accept': '*/*',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Origin': 'http://www.pestchina.com',
                    'Pragma': 'no-cache',
                    'Referer': 'http://www.pestchina.com/',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                callback=self.parse,
                meta={'species_id': response.meta['species_id'], 'pagenum': next_pagenum}
            )