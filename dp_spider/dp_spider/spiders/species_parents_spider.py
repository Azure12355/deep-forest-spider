import scrapy
import json
import os

from ..items import SpeciesParentItem

class SpeciesParentsSpider(scrapy.Spider):
    name = 'species_parents'  # 爬虫名称
    allowed_domains = ['www.pestchina.com']  # 允许的域名
    # 构建meta_info_list目录路径
    meta_info_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'meta_info_list')
    count = 0
    num = 0
    cnt = 0
    temp = ''

    def start_requests(self):
        """
        起始请求方法：读取 meta_info_list 文件夹下的所有 JSON 文件，生成 API 请求。
        """
        # 遍历 meta_info_list 目录下的所有文件
        for filename in os.listdir(self.meta_info_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.meta_info_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    meta_info_list = json.load(f)  # 加载 JSON 文件内容
                    # 遍历每个物种的元信息
                    for meta_info in meta_info_list:
                        tp_guid = meta_info['TP_GUID']  # 提取物种的 TP_GUID
                        ss_name_sci = meta_info['SSNameSci']  # 提取物种的拉丁名
                        # 构造 API 请求 URL
                        url = f'http://www.pestchina.com/webapi/nb/SpeciesCode/ParentList/{ss_name_sci}'
                        # 发送 GET 请求，并将 tp_guid 传递给回调函数
                        yield scrapy.Request(
                            url=url,
                            callback=self.parse,
                            meta={'species_TP_GUID': tp_guid}
                        )

    def parse(self, response):
        """
        解析方法：处理 API 响应，生成 SpeciesParentItem。
        """
        # 解析 JSON 响应
        data = json.loads(response.text)
        species_TP_GUID = response.meta['species_TP_GUID']  # 获取传递的 TP_GUID
        # 遍历每个父级分类信息
        for item_data in data:
            item = SpeciesParentItem()
            item['species_TP_GUID'] = species_TP_GUID  # 设置标识字段
            item['ParentSsName'] = item_data.get('ParentSsName')  # 父级分类名称
            item['SLevel'] = item_data.get('SLevel')  # 分类级别
            item['SSNameSci'] = item_data.get('SSNameSci')  # 科学名
            item['TP_GUID'] = item_data.get('TP_GUID')  # 分类 TP_GUID
            item['SClass'] = item_data.get('SClass')  # 分类类别
            item['SCName'] = item_data.get('SCName')  # 中文名
            self.count += 1
            if self.temp != item['species_TP_GUID']:
                self.temp = item['species_TP_GUID']
                self.num += 1
                self.cnt = 1
            else:
                self.cnt += 1
            print(f'✅ 成功爬取数据第{self.count}条'
                  f' --- 第{self.num}个物种的第{self.cnt}个父级分类'
                  f'SCName={item["SCName"]}')
            yield item  # 提交 Item 到管道