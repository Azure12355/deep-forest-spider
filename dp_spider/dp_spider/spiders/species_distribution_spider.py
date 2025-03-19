import json
import os
import scrapy
from scrapy import FormRequest
from ..items import SpeciesDistributionItem, ICodeItem


class SpeciesDistributionSpider(scrapy.Spider):
    name = 'species_distribution'
    allowed_domains = ['www.pestchina.com']
    base_url = 'http://www.pestchina.com/webapi/nb/SpeciesDistribution/list/concat'
    custom_settings = {
        'DOWNLOAD_DELAY': 0,  # 礼貌爬取间隔
        'CONCURRENT_REQUESTS': 200  # 并发数
    }

    count = 0

    # 配置物种ID文件路径
    species_id_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        '..', 'data', 'species_id'
    )

    def start_requests(self):
        """生成初始请求，读取所有物种ID文件"""
        for filename in os.listdir(self.species_id_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.species_id_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    species_ids = json.load(f)
                    for species_id in species_ids:
                        yield self.build_form_request(
                            species_id=species_id,
                            page_num=1,
                            total_page=0  # 初始总页设为0，由服务器返回实际值
                        )

    def build_form_request(self, species_id, page_num, total_page):
        """构建表单请求对象"""
        formdata = {
            'needCk': 'true',
            'selectContinent[country]': '',
            'yb': species_id,
            'SC_GUID': species_id,
            'continent': '',
            'paging[pagecount]': '5000',  # 每页固定18条
            'paging[pagenum]': str(page_num),  # 当前页码
            'paging[totalpage]': str(total_page)  # 总页数（首次请求设为0）
        }

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'http://www.pestchina.com',
            'Pragma': 'no-cache',
            'Referer': 'http://www.pestchina.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        return FormRequest(
            url=self.base_url,
            formdata=formdata,
            headers=headers,
            meta={
                'species_id': species_id,
                'current_page': page_num,
                'total_page': total_page
            },
            callback=self.parse_response,
            dont_filter=True
        )

    def parse_response(self, response):
        """解析API响应数据"""
        meta = response.meta
        species_id = meta['species_id']
        current_page = meta['current_page']

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f'JSON解析失败，URL: {response.url}')
            return

        # 处理分页数据
        paging = data.get('paging', {})
        actual_total = int(paging.get('totalpage', 0))

        # 如果服务器返回的totalpage有效，更新总页数
        if actual_total > meta['total_page']:
            total_page = actual_total
        else:
            total_page = meta['total_page']

        # 处理分布数据
        for item in data.get('content', []):
            distribution_item = self.parse_distribution_item(item, species_id)
            self.count += 1
            print(f'✅ 成功爬取数据第{self.count}条, '
                  f'distribution={distribution_item["CCnameContinent"]}-{distribution_item["CCnameCountry"]}-{distribution_item["CCnameProvince"]}')
            yield distribution_item

        # 生成下一页请求（如果存在）
        if current_page < total_page:
            next_page = current_page
            yield self.build_form_request(
                species_id=species_id,
                page_num=next_page,
                total_page=total_page
            )

    def parse_distribution_item(self, item_data, species_id):
        """解析单个分布条目"""
        distribution_item = SpeciesDistributionItem()

        # 基础字段
        distribution_item['species_id'] = species_id
        distribution_item['rowid'] = item_data.get('rowid')
        distribution_item['CCnameContinent'] = item_data.get('CCnameContinent')
        distribution_item['CCnameCountry'] = item_data.get('CCnameCountry')
        distribution_item['CCnameProvince'] = item_data.get('CCnameProvince')
        distribution_item['Descrip'] = item_data.get('Descrip')

        # 处理嵌套文献信息
        icodes = []
        for icode_data in item_data.get('Icodes', []):
            icode_item = ICodeItem()
            icode_item['ICodeID'] = icode_data.get('ICodeID')
            icode_item['AuthorDisplay'] = icode_data.get('AuthorDisplay')
            icode_item['Title'] = icode_data.get('Title')
            icodes.append(icode_item)

        distribution_item['Icodes'] = icodes
        return distribution_item