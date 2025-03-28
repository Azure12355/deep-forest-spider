<p align="center">
    <a href="" target="_blank">
      <img src="https://image.weilanx.com/718839D7-82FF-4E67-BACA-552843BDF07C.png!q60_h512" width="280" />
    </a>
</p>

<h1 align="center">Deep-Forest-Spider</h1>
<p align="center"><strong>一个基于Scrapy和Redis的分布式林业病虫害数据爬虫模块。致力于为林业病虫害智能问答系统提供高质量的数据支持。<br>支持多源数据采集、分布式任务调度和高效数据存储，<em>持续优化 ing～</em></strong></p>

<div align="center">
    <a href="https://www.weilanx.com"><img src="https://img.shields.io/badge/个人网站-蔚蓝-blue.svg?style=plasticr"></a>
    <a href="https://github.com/Azure12355/deep-forest-spider"><img src="https://img.shields.io/badge/github-项目地址-yellow.svg?style=plasticr"></a>
    <a href="https://gitee.com/Azure12355/deep-forest-spider"><img src="https://img.shields.io/badge/码云-项目地址-orange.svg?style=plasticr"></a> 
    <a href="https://github.com/Azure12355/deep-forest-spider/blob/master/LICENSE" target="_blank">
        <img alt="License: MIT-3.0" src="https://img.shields.io/badge/License-MIT--3.0-blue.svg">
    </a> 
    <a href="https://github.com/Azure12355/deep-forest-spider/stargazers" target="_blank">
        <img alt="Stars" src="https://img.shields.io/github/stars/Azure12355/deep-forest-spider.svg?style=social">
    </a> 
</div>

## 项目导航

- **项目仓库**：[deep-forest-spider](https://github.com/Azure12355/deep-forest-spider)
- **码云仓库**：[Gitee](https://gitee.com/Azure12355/deep-forest-spider)（国内访问速度更快）
- **项目文档**：详细的开发指南、部署步骤和爬虫配置说明，可点击[Deep-Forest-Spider文档](#项目文档)查看。

## 项目介绍

`deep-forest-spider` 是一个基于 Python Scrapy 框架开发的分布式爬虫模块，专为林业病虫害智能问答系统设计。通过集成 Redis
实现分布式任务调度和去重，支持从多个林业相关网站高效采集病虫害数据。项目旨在为后续的知识图谱构建和 RAG（Retrieval-Augmented
Generation）提供可靠的数据基础。

### 项目功能

- **多源数据采集**：支持林业病虫害相关网站的数据爬取，如学术文章、新闻和政府公告。
- **分布式爬虫**：通过 Redis 实现任务分发和数据去重，提升爬取效率。
- **数据清洗与存储**：提供数据清洗管道，支持输出到文件或数据库。
- **可扩展性**：支持新增爬虫目标，易于维护和扩展。

### 项目演示

#### 爬虫运行示例

![p92nKne.png](./docs/image/爬虫运行截图.png)

### 技术选型

#### 核心技术

|      技术       | 说明                   | 官网                                                                                               |
|:-------------:|----------------------|--------------------------------------------------------------------------------------------------|
|    Scrapy     | 高性能爬虫框架              | [https://scrapy.org](https://scrapy.org)                                                         |
|     Redis     | 分布式任务调度和数据去重         | [https://redis.io](https://redis.io)                                                             |
| Scrapy-Redis  | Scrapy 的 Redis 分布式扩展 | [https://github.com体会/spiders/scrapy-redis](https://github.com/rmax/scrapy-redis)                |
|   Requests    | HTTP 请求库，用于辅助数据抓取    | [https://requests.readthedocs.io](https://requests.readthedocs.io)                               |
| BeautifulSoup | HTML/XML 解析库         | [https://www.crummy.com/software/BeautifulSoup](https://www.crummy.com/software/BeautifulSoup)   |
|    Python     | 编程语言                 | [https://www.python.org](https://www.python.org)                                                 |
|    Logging    | 日志记录工具               | [https://docs.python.org/3/library/logging.html](https://docs.python.org/3/library/logging.html) |

### 环境搭建

1. **安装依赖**  
   在项目根目录下运行：
   ```bash
   pip install -r requirements.txt
   ```
~~2. **配置 Redis**_(暂未实现)_~~  
   确保 Redis 服务已启动，并在 `settings.py` 中配置 Redis 连接信息：
   ```python
   REDIS_HOST = 'localhost'
   REDIS_PORT = 6379
   ```
3. **运行爬虫**  
   在项目根目录下执行：
   ```bash
   scrapy crawl forest_spider
   ```

详细步骤请参考[项目文档](#项目文档)。

### 项目文档

包含环境搭建、爬虫配置、任务调度和数据存储的详细说明，持续更新中～  
查看[Deep-Forest-Spider文档](#项目文档)

## 贡献

**贡献之前请先阅读[行为准则](CODE_OF_CONDUCT.md) 和 [贡献指南](CONTRIBUTING.md)。感谢所有为 deep-forest-spider
做过贡献的人!**

## License

[MIT License 3.0](./LICENSE)