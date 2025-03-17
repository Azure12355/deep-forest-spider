# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DpSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


"""物种信息"""


class PestchinaScraperItem(scrapy.Item):
    rowid = scrapy.Field()
    TP_GUID = scrapy.Field()
    SSNameSci = scrapy.Field()
    SSName = scrapy.Field()
    NamedYear = scrapy.Field()
    SCName = scrapy.Field()
    SEName = scrapy.Field()
    SENameAbb = scrapy.Field()
    SClass = scrapy.Field()
    ParentSsName = scrapy.Field()
    SLevel = scrapy.Field()
    SLevel2 = scrapy.Field()
    Source = scrapy.Field()
    Status = scrapy.Field()
    Checker = scrapy.Field()
    CheckTime = scrapy.Field()
    OrgRiskCode = scrapy.Field()
    IsSpecies = scrapy.Field()
    TP_AUTHOR = scrapy.Field()
    TP_CREATED = scrapy.Field()
    TP_EDITOR = scrapy.Field()
    TP_MODIFIED = scrapy.Field()
    Temp_CREATED = scrapy.Field()
    CHECKER_ID = scrapy.Field()
    CHECKER_NAME = scrapy.Field()
    ScType = scrapy.Field()


"""物种元信息"""


class YMMetaItem(scrapy.Item):
    """异名信息嵌套字段"""
    SONType = scrapy.Field()  # 异名类型（如拉丁名、英文名）
    NamedYear = scrapy.Field()  # 命名年份
    SOtherNameSci = scrapy.Field()  # 异名学名


class MetaInfoItem(scrapy.Item):
    """元信息主字段"""
    # 基础信息
    TP_GUID = scrapy.Field()  # 有害生物唯一ID（接口请求参数）
    SSNameSci = scrapy.Field()  # 学名（拉丁文）
    SSName = scrapy.Field()  # 含命名人的完整学名
    NamedYear = scrapy.Field()  # 命名年份及命名人
    SCName = scrapy.Field()  # 中文名
    SEName = scrapy.Field()  # 英文名
    SENameAbb = scrapy.Field()  # 英文名缩写

    # 分类信息
    SClass = scrapy.Field()  # 生物分类（如真菌、线虫）
    ParentSsName = scrapy.Field()  # 属名
    SLevel = scrapy.Field()  # 分类级别（种/属）
    SLevel2 = scrapy.Field()  # 次级分类级别

    # 状态信息
    Source = scrapy.Field()  # 数据来源（如GBIF）
    Status = scrapy.Field()  # 审核状态
    Checker = scrapy.Field()  # 审核人
    CheckTime = scrapy.Field()  # 审核时间

    # 系统字段
    OrgRiskCode = scrapy.Field()  # 原始风险代码
    IsSpecies = scrapy.Field()  # 是否物种级
    TP_AUTHOR = scrapy.Field()  # 数据创建者
    TP_CREATED = scrapy.Field()  # 创建时间
    TP_EDITOR = scrapy.Field()  # 最后编辑人
    TP_MODIFIED = scrapy.Field()  # 最后修改时间
    Temp_CREATED = scrapy.Field()  # 临时创建时间

    # 异名列表
    ym = scrapy.Field()  # 异名信息列表（包含YMMetaItem的字典）
