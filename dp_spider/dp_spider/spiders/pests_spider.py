import json

import scrapy
from scrapy.spiders import CrawlSpider

from ..items import PestchinaScraperItem


class PestsSpiderSpider(CrawlSpider):
    name = "pests_spider"
    allowed_domains = ['www.pestchina.com']
    start_url = 'http://www.pestchina.com/webapi/nb/SpeciesCode/list'

    custom_headers = {
        'Accept': '*/*',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,en-US;q=0.7',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'http://www.pestchina.com',
        'Referer': 'http://www.pestchina.com/',
        'X-Requested-With': 'XMLHttpRequest'
    }

    # rules = (Rule(LinkExtractor(allow=r"Items/"), callback="parse_item", follow=True),)

    def start_requests(self):
        form_data = {
            'key': '',
            'wzType': '有害生物',
            'filterType': '包含',
            'orderBy': 'TP_MODIFIED desc ,TP_CREATED desc',
            'paging[pagecount]': '5000',  # 每次请求的条数
            'paging[pagenum]': '1',
            'paging[totalpage]': '0'
        }
        yield scrapy.FormRequest(
            url=self.start_url,
            formdata=form_data,
            headers=self.custom_headers,
            meta={'dont_verify_ssl': True},
            callback=self.parse
        )

    def parse(self, response):
        try:
            data = json.loads(response.text)
            content = data.get('content', [])
            paging = data.get('paging', {})

            # Process items
            for item_data in content:
                item = PestchinaScraperItem()
                for field in item_data:
                    if field in item.fields:
                        item[field] = item_data.get(field)
                yield item

            # Handle pagination
            current_page = int(paging.get('pagenum', 1))
            total_page = int(paging.get('totalpage', 0))

            if current_page < total_page:
                next_page = current_page
                form_data = {
                    'key': '',
                    'wzType': '有害生物',
                    'filterType': '包含',
                    'orderBy': 'TP_MODIFIED desc ,TP_CREATED desc',
                    'paging[pagecount]': '5000',
                    'paging[pagenum]': str(next_page),
                    'paging[totalpage]': str(total_page)
                }
                yield scrapy.FormRequest(
                    url=self.start_url,
                    formdata=form_data,
                    headers=self.custom_headers,
                    meta={'dont_verify_ssl': True},
                    callback=self.parse
                )

        except json.JSONDecodeError:
            self.logger.error('JSON解析失败: %s', response.body)
