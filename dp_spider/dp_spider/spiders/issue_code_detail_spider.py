import scrapy
import json
import os
from ..items import IssueCodeDetailItem

class IssueCodeDetailSpider(scrapy.Spider):
    name = 'issue_code_detail'  # 爬虫名称
    allowed_domains = ['www.pestchina.com']  # 限制爬取域名
    base_url = 'http://www.pestchina.com/webapi/nb/IssueCode/detail/'  # 目标接口URL
    count = 0

    # 自定义设置，启用Pipeline
    custom_settings = {
        'ITEM_PIPELINES': {
            'dp_spider.pipelines.IssueCodeDetailPipeline': 300,
        }
    }

    def __init__(self, *args, **kwargs):
        super(IssueCodeDetailSpider, self).__init__(*args, **kwargs)
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
        """为每个物种ID发起GET请求"""
        for species_id in self.species_ids:
            # 假设issueCode与species_id相关联，此处简化为直接使用species_id，实际需根据接口调整
            # todo 这里后续要改为真实的issue_code而不是species_id
            issue_code = species_id  # 假设issueCode与species_id相同
            url = self.base_url + issue_code
            yield scrapy.Request(
                url=url,
                meta={'species_id': species_id},  # 传递物种ID
                callback=self.parse
            )

    def parse(self, response):
        """解析响应，提取数据"""
        data = json.loads(response.text)

        # 创建Item
        issue_code_detail_item = IssueCodeDetailItem()
        issue_code_detail_item['species_id'] = response.meta['species_id']  # 添加物种ID
        issue_code_detail_item['Icode'] = data.get('Icode')  # 参考文献ID
        issue_code_detail_item['Title'] = data.get('Title')  # 标题
        issue_code_detail_item['SourceTitle'] = data.get('SourceTitle')  # 来源标题
        issue_code_detail_item['IssueAuthor'] = data.get('IssueAuthor')  # 作者
        issue_code_detail_item['AuthorDisplay'] = data.get('AuthorDisplay')  # 作者显示
        issue_code_detail_item['ITypes1'] = data.get('ITypes1')  # 类型1
        issue_code_detail_item['ITypes'] = data.get('ITypes')  # 类型
        issue_code_detail_item['ITypes2'] = data.get('ITypes2')  # 类型2
        issue_code_detail_item['KeyWord'] = data.get('KeyWord')  # 关键词
        issue_code_detail_item['CCname'] = data.get('CCname')  # 国家名称
        issue_code_detail_item['PubTime'] = data.get('PubTime')  # 出版时间
        issue_code_detail_item['Publisher'] = data.get('Publisher')  # 出版商
        issue_code_detail_item['Derivation'] = data.get('Derivation')  # 来源
        issue_code_detail_item['TypeCode'] = data.get('TypeCode')  # 类型代码
        issue_code_detail_item['ExecuteDate'] = data.get('ExecuteDate')  # 执行日期
        issue_code_detail_item['Reference'] = data.get('Reference')  # 参考文献
        issue_code_detail_item['AbstractDesc'] = data.get('AbstractDesc')  # 摘要
        issue_code_detail_item['TP_AUTHOR'] = data.get('TP_AUTHOR')  # 作者
        issue_code_detail_item['TP_CREATED'] = data.get('TP_CREATED')  # 创建时间
        issue_code_detail_item['TP_EDITOR'] = data.get('TP_EDITOR')  # 编辑者
        issue_code_detail_item['TP_MODIFIED'] = data.get('TP_MODIFIED')  # 修改时间
        issue_code_detail_item['PublishPerson'] = data.get('PublishPerson')  # 发布人
        issue_code_detail_item['PublishTime'] = data.get('PublishTime')  # 发布时间
        issue_code_detail_item['Status'] = data.get('Status')  # 状态

        self.count += 1
        print(f'✅ 成功爬取数据第{self.count}条参考文献 '
              f'Title={issue_code_detail_item["Title"]}')
        yield issue_code_detail_item  # 提交Item到Pipeline