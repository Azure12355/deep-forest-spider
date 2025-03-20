# dp_spider/spiders/species_host_spider.py
import scrapy
import json
import os
from ..items import SpeciesHostItem, IcodeItem

class SpeciesHostSpider(scrapy.Spider):
    name = 'species_host'  # 爬虫名称，用于运行时调用
    allowed_domains = ['www.pestchina.com']  # 限制爬取的域名
    base_url = 'http://www.pestchina.com/webapi/nb/SpeciesHost/list/concat'  # 请求的目标URL
    count = 0

    def start_requests(self):
        """
        读取species_id目录下的所有JSON文件，发起初始请求
        """
        # 构建species_id目录路径
        species_id_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data', 'species_id')
        # 遍历目录下的所有文件
        for filename in os.listdir(species_id_dir):
            if filename.startswith('species_ids_') and filename.endswith('.json'):
                filepath = os.path.join(species_id_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    species_ids = json.load(f)  # 加载物种ID列表
                for species_id in species_ids:
                    # 为每个物种ID发起第一页请求
                    yield self.make_request(species_id, 1)

    def make_request(self, species_id, page):
        """
        构造POST请求，包含分页参数和物种ID
        """
        form_data = {
            'needCk': 'true',             # 是否需要权限校验，固定为true
            'key': '',                    # 寄主名称关键词过滤，留空表示不过滤
            'SC_GUID': species_id,        # 物种全局唯一标识
            'paging[pagecount]': '5000',    # 每页返回的数据条数，固定为18
            'paging[pagenum]': str(page), # 当前请求的页码
            'paging[totalpage]': '86'     # 总页数初始值，后续由响应更新
        }
        return scrapy.FormRequest(
            url=self.base_url,
            formdata=form_data,
            headers={
                'Accept': '*/*',  # 接受所有类型响应
                'Accept-Language': 'zh-CN,zh;q=0.9',  # 中文优先
                'Cache-Control': 'no-cache',  # 禁用缓存
                'Connection': 'keep-alive',  # 保持长连接
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',  # 表单数据格式
                'Origin': 'http://www.pestchina.com',  # 请求来源域名
                'Pragma': 'no-cache',  # 兼容HTTP/1.0缓存控制
                'Referer': 'http://www.pestchina.com/',  # 来源页面
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',  # 浏览器标识
                'X-Requested-With': 'XMLHttpRequest'  # 标识AJAX请求
            },
            meta={'species_id': species_id, 'page': page},  # 传递物种ID和页码
            callback=self.parse  # 指定解析函数
        )

    def parse(self, response):
        """
        解析响应数据，提取寄主信息并处理分页
        """
        data = json.loads(response.text)  # 将响应文本解析为JSON
        content = data.get('content', [])  # 获取数据内容
        paging = data.get('paging', {})    # 获取分页信息

        # 解析当前页的每条数据
        for item_data in content:
            item = SpeciesHostItem()
            item['species_id'] = response.meta['species_id']  # 添加物种ID，响应中无此字段
            item['rowid'] = item_data.get('rowid')            # 数据行号
            item['HOST_GUID'] = item_data.get('HOST_GUID')    # 寄主全局唯一标识
            item['HOST_NAME'] = item_data.get('HOST_NAME')    # 寄主英文名称
            item['HOST_NAME_CN'] = item_data.get('HOST_NAME_CN')  # 寄主中文名称
            item['HostType'] = item_data.get('HostType')      # 寄主类型
            icodes = []
            # 处理嵌套的Icodes字段
            for icode_data in item_data.get('Icodes', []):
                icode_item = IcodeItem()
                icode_item['ICodeID'] = icode_data.get('ICodeID')         # 文献引用ID
                icode_item['AuthorDisplay'] = icode_data.get('AuthorDisplay')  # 作者展示信息
                icodes.append(icode_item)
            item['Icodes'] = icodes
            self.count += 1
            print(f'✅ 成功爬取数据第{self.count}条'
                  f'HOST_NAME_CN={item["HOST_NAME_CN"]}')
            yield item  # 提交Item到Pipeline

        # 检查是否有下一页
        current_page = int(paging.get('pagenum', 1))    # 当前页码
        total_pages = int(paging.get('totalpage', 86))  # 总页数
        if current_page < total_pages:
            next_page = current_page + 1
            # 请求下一页
            yield self.make_request(response.meta['species_id'], next_page)