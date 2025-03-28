# Scrapy settings for dp_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "dp_spider"

SPIDER_MODULES = ["dp_spider.spiders"]
NEWSPIDER_MODULE = "dp_spider.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# 设置浏览器的请求头标识
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"

# Obey robots.txt rules
# 关闭反爬虫协议
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 500  # 根据服务器承受能力调整

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0  # 基础延迟
# 优化下载超时
DOWNLOAD_TIMEOUT = 30  # 避免卡死
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 200
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "dp_spider.middlewares.DpSpiderSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "dp_spider.middlewares.InsecureRequestsMiddleware": 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # "dp_spider.pipelines.JsonBatchPipeline": 300, # 请求所有物种列表
    # "dp_spider.pipelines.MetaInfoJsonBatchPipeline": 300,  # 请求物种元信息
    # "dp_spider.pipelines.SpeciesDistributionPipeline": 300,  # 请求物种分布信息
    # "dp_spider.pipelines.SpeciesBasicInfoPipeline": 300,  # 请求物种基本信息
    # 'dp_spider.pipelines.SpeciesHostPipeline': 300, # 请求物种寄主信息
    # 'dp_spider.pipelines.SpeciesParentPipeline': 300, # 请求物种父级分类信息
    # 'dp_spider.pipelines.PestRelationPipeline': 300,
    # 'dp_spider.pipelines.PestHostPartPipeline': 300,
    # 'dp_spider.pipelines.CmDiffuseMediumPipeline': 300,
    # 'dp_spider.pipelines.IssueCodeDetailPipeline': 300,
    'dp_spider.pipelines.FilePipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# 提升Twisted线程池
REACTOR_THREADPOOL_MAXSIZE = 30  # 默认10

LOG_LEVEL = "ERROR"
