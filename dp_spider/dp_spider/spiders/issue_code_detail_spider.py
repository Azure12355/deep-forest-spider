import scrapy
import json
import os
import csv
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
        self.icodes = self.load_icodes()  # 初始化时加载icode列表

    def load_icodes(self):
        """从cleaned_data/reference_relation.csv文件中读取icode列表"""
        icodes = []
        csv_file = os.path.join('cleaned_data', 'reference_relation.csv')
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    icode = row['icode'].strip()  # 去除首尾空白
                    if icode:  # 确保不添加空值
                        icodes.append(icode)
        except FileNotFoundError:
            self.logger.error(f"文件 {csv_file} 不存在")
        except Exception as e:
            self.logger.error(f"读取文件 {csv_file} 时出错: {e}")
        return icodes

    def start_requests(self):
        """为每个icode发起GET请求"""
        for icode in self.icodes:
            url = self.base_url + icode
            yield scrapy.Request(
                url=url,
                meta={'icode': icode},  # 传递icode到meta
                callback=self.parse
            )

    def parse(self, response):
        """解析响应，提取数据"""
        data = json.loads(response.text)

        # 创建Item
        issue_code_detail_item = IssueCodeDetailItem()
        issue_code_detail_item['Icode'] = response.meta['icode']  # 使用传递的icode
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