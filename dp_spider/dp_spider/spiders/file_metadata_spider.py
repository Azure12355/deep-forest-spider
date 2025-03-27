import scrapy
import csv
import json
import os

from ..items import FileMetadataItem


class FileMetadataSpider(scrapy.Spider):
    name = 'file_metadata'  # 爬虫名称，用于运行时指定
    allowed_domains = ['www.pestchina.com']  # 限制爬虫请求的域名
    count = 0

    def start_requests(self):
        """
        读取 cleaned_data/reference_relation.csv 文件，生成初始请求
        """
        # 构建 CSV 文件路径（相对于项目根目录）
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'cleaned_data',
                                'reference_relation.csv')

        # 读取 CSV 文件
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # 检查 CSV 文件是否包含 'icode' 列
            if 'icode' not in reader.fieldnames:
                self.logger.error("CSV 文件中缺少 'icode' 列")
                return

            # 遍历每一行，提取 icode 并构造请求
            for row in reader:
                icode = row['icode']
                url = f'http://www.pestchina.com/webapi/nb/common/files/{icode}'

                # 设置请求头，模拟浏览器请求
                headers = {
                    'Accept': '*/*',  # 接受所有类型响应
                    'Accept-Language': 'zh-CN,zh;q=0.9',  # 中文优先
                    'Cache-Control': 'no-cache',  # 禁用缓存
                    'Connection': 'keep-alive',  # 保持长连接
                    'Pragma': 'no-cache',  # 兼容 HTTP/1.0 缓存控制
                    'Referer': 'http://www.pestchina.com/',  # 来源页面
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                    # 浏览器标识
                    'X-Requested-With': 'XMLHttpRequest'  # 标识 AJAX 请求
                }

                # 发起 GET 请求，传递 icode 到 parse 方法
                yield scrapy.Request(url, headers=headers, callback=self.parse, meta={'icode': icode})

    def parse(self, response):
        """
        解析接口返回的 JSON 数据，生成 FileMetadataItem，并与 icode 关联
        """
        icode = response.meta['icode']  # 从 meta 中获取 icode
        try:
            # 将响应文本解析为 JSON
            data = json.loads(response.text)

            # 检查数据是否为列表
            if not isinstance(data, list):
                self.logger.error(f"响应数据不是列表: {response.url}")
                return

            # 遍历 JSON 数组中的每个文件元数据
            for item in data:
                file_item = FileMetadataItem()
                file_item['icode'] = icode  # 绑定 icode
                file_item['guid'] = item.get('guid')  # 获取 guid，若缺失则为 None
                file_item['name'] = item.get('name')  # 获取 name，若缺失则为 None
                file_item['url'] = item.get('url')  # 获取 url，若缺失则为 None

                # 提交 Item 给 Pipeline 处理
                self.count += 1
                print(f'✅ 成功爬取数据第{self.count}条 '
                      f'name={file_item["name"]}')
                yield file_item

        except json.JSONDecodeError:
            self.logger.error(f"JSON 解析失败: {response.url}")
        except Exception as e:
            self.logger.error(f"解析响应时出错: {response.url}, 错误: {str(e)}")