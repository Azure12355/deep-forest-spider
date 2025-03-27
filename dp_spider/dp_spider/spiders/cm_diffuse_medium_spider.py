import scrapy
import json
import os
from ..items import CmDiffuseMediumItem

class CmDiffuseMediumSpider(scrapy.Spider):
    name = 'cm_diffuse_medium'  # 爬虫名称
    allowed_domains = ['www.pestchina.com']  # 限制爬取域名
    start_urls = ['http://www.pestchina.com/webapi/nb/CmDiffuseMedium/list']  # 目标接口URL
    count = 0

    # 自定义设置，启用Pipeline
    custom_settings = {
        'ITEM_PIPELINES': {
            'dp_spider.pipelines.CmDiffuseMediumPipeline': 300,
        }
    }

    def __init__(self, *args, **kwargs):
        super(CmDiffuseMediumSpider, self).__init__(*args, **kwargs)
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
                'paging[pagecount]': '18',  # 每页记录数，固定为100
                'paging[pagenum]': '1',  # 初始页码
                'paging[totalpage]': '1'  # 初始总页数，实际值由响应动态调整
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
        content = data.get('content', [])  # 获取扩散媒介列表

        # 遍历每条记录，创建Item
        for item in content:
            cm_diffuse_medium_item = CmDiffuseMediumItem()
            cm_diffuse_medium_item['species_id'] = response.meta['species_id']  # 添加物种ID
            cm_diffuse_medium_item['rowid'] = item.get('rowid')  # 行ID
            cm_diffuse_medium_item['TP_GUID'] = item.get('TP_GUID')  # 扩散媒介GUID
            cm_diffuse_medium_item['SC_GUID'] = item.get('SC_GUID')  # 物种GUID
            cm_diffuse_medium_item['SSNameSci'] = item.get('SSNameSci')  # 物种学名
            cm_diffuse_medium_item['SpeciesType'] = item.get('SpeciesType')  # 物种类型
            cm_diffuse_medium_item['OB_GUID'] = item.get('OB_GUID')  # 媒介GUID
            cm_diffuse_medium_item['OB_SSNameSci'] = item.get('OB_SSNameSci')  # 媒介学名
            cm_diffuse_medium_item['Descrip'] = item.get('Descrip')  # 描述
            cm_diffuse_medium_item['MediumType'] = item.get('MediumType')  # 媒介类型
            cm_diffuse_medium_item['ICodeID'] = item.get('ICodeID')  # ICode ID
            cm_diffuse_medium_item['ICodeName'] = item.get('ICodeName')  # ICode名称
            cm_diffuse_medium_item['Page'] = item.get('Page')  # 页码
            cm_diffuse_medium_item['TP_AUTHOR'] = item.get('TP_AUTHOR')  # 作者
            cm_diffuse_medium_item['TP_CREATED'] = item.get('TP_CREATED')  # 创建时间
            cm_diffuse_medium_item['TP_EDITOR'] = item.get('TP_EDITOR')  # 编辑者
            cm_diffuse_medium_item['TP_MODIFIED'] = item.get('TP_MODIFIED')  # 修改时间
            cm_diffuse_medium_item['Tmp_GUID'] = item.get('Tmp_GUID')  # 临时GUID
            cm_diffuse_medium_item['Tmp_SSNameSci'] = item.get('Tmp_SSNameSci')  # 临时物种学名
            cm_diffuse_medium_item['NamedYear'] = item.get('NamedYear')  # 命名年份

            self.count += 1
            print(f'✅ 成功爬取数据第{self.count}条'
                  f'物种id：{response.meta["species_id"]} '
                  f'OB_SSNameSci={cm_diffuse_medium_item["OB_SSNameSci"]}')
            yield cm_diffuse_medium_item  # 提交Item到Pipeline

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