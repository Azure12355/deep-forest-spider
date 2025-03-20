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


import scrapy


# 物种分布信息
class ICodeItem(scrapy.Item):
    """文献引用信息项"""
    # 文献唯一标识码 (如7000)
    ICodeID = scrapy.Field()
    # 作者显示信息 (如"CAB, 2006")
    AuthorDisplay = scrapy.Field()
    # 文献标题 (如"CPC2006")
    Title = scrapy.Field()


class SpeciesDistributionItem(scrapy.Item):
    """物种分布信息主项"""
    # 所属物种唯一标识（从species_id参数添加）
    species_id = scrapy.Field()
    # 记录行唯一标识 (如1)
    rowid = scrapy.Field()
    # 所属大洲名称 (如"北美洲")
    CCnameContinent = scrapy.Field()
    # 所属国家名称 (如"加拿大")
    CCnameCountry = scrapy.Field()
    # 所属省级行政区（可能为空） (如"艾伯塔省")
    CCnameProvince = scrapy.Field()
    # 分布描述文本 (如"存在 present")
    Descrip = scrapy.Field()
    # 关联的文献引用列表
    Icodes = scrapy.Field()


from scrapy import Item, Field


# 物种基本信息

class SpeciesBasicInfoItem(scrapy.Item):
    # 行ID，标识每条记录的唯一编号
    rowid = scrapy.Field()
    # 物种基本信息GUID，系统内的唯一标识符
    TP_GUID = scrapy.Field()
    # 物种GUID，用于关联具体的物种
    SC_GUID = scrapy.Field()
    # 物种学名，科学的拉丁文名称
    SSNameSci = scrapy.Field()
    # 英文名，物种的英文名称，可能为空
    SEName = scrapy.Field()
    # 生物学特性，描述物种的生物学行为和特性
    BiologicalProperties = scrapy.Field()
    # 形态学特征，描述物种的物理外观特征
    MorphologicalCharacteristics = scrapy.Field()
    # 检测方法，描述检测该物种的方法或技术
    DetectionMethod = scrapy.Field()
    # 分布描述，描述物种的地理分布情况
    DistributionDescription = scrapy.Field()
    # 参考文献ID，关联的文献编号
    ICodeID = scrapy.Field()
    # 参考文献名称，文献的标题或名称
    ICodeName = scrapy.Field()
    # 页码，文献中相关内容的页数
    Page = scrapy.Field()
    # 备注，额外的说明或注释
    Remark = scrapy.Field()
    # 作者，记录的创建者
    TP_AUTHOR = scrapy.Field()
    # 创建时间，记录的创建时间戳
    TP_CREATED = scrapy.Field()
    # 编辑者，记录的最后编辑者
    TP_EDITOR = scrapy.Field()
    # 修改时间，记录的最后修改时间戳
    TP_MODIFIED = scrapy.Field()
    # 临时创建时间，临时的创建时间戳
    Temp_CREATED = scrapy.Field()
    # 临时形态学特征，临时的形态学描述
    Temp_Morp = scrapy.Field()
    # 参考文献信息，嵌套字段，包含详细的文献数据
    cankao = scrapy.Field()

class CankaoItem(scrapy.Item):
    # 参考文献ID，文献的唯一标识符
    Icode = scrapy.Field()
    # 标题，文献的标题
    Title = scrapy.Field()
    # 来源标题，文献来源的标题（如期刊名）
    SourceTitle = scrapy.Field()
    # 发行作者，文献的作者列表
    IssueAuthor = scrapy.Field()
    # 作者显示，文献作者的显示格式
    AuthorDisplay = scrapy.Field()
    # 类型1，文献的分类类型1
    ITypes1 = scrapy.Field()
    # 类型，文献的主要类型
    ITypes = scrapy.Field()
    # 类型2，文献的分类类型2
    ITypes2 = scrapy.Field()
    # 关键词，文献的相关关键词
    KeyWord = scrapy.Field()
    # 国家/地区，文献发布国家或地区
    CCname = scrapy.Field()
    # 出版时间，文献的发布时间
    PubTime = scrapy.Field()
    # 出版商，文献的出版机构
    Publisher = scrapy.Field()
    # 衍生，文献的来源或引用信息
    Derivation = scrapy.Field()
    # 类型代码，文献的类型编码
    TypeCode = scrapy.Field()
    # 执行日期，文献的执行或生效日期
    ExecuteDate = scrapy.Field()
    # 参考，文献的参考信息
    Reference = scrapy.Field()
    # 摘要描述，文献的摘要内容
    AbstractDesc = scrapy.Field()
    # 作者，文献记录的创建者
    TP_AUTHOR = scrapy.Field()
    # 创建时间，文献记录的创建时间戳
    TP_CREATED = scrapy.Field()
    # 编辑者，文献记录的最后编辑者
    TP_EDITOR = scrapy.Field()
    # 修改时间，文献记录的最后修改时间戳
    TP_MODIFIED = scrapy.Field()
    # 发布人，文献的发布者
    PublishPerson = scrapy.Field()
    # 发布时间，文献的发布时间戳
    PublishTime = scrapy.Field()
    # 状态，文献的当前状态（如已确认）
    Status = scrapy.Field()


# 物种的寄主信息


class IcodeItem(scrapy.Item):
    """
    嵌套的Icodes字段的Item，用于存储文献引用信息
    """
    ICodeID = scrapy.Field()       # 文献引用ID，唯一标识文献
    AuthorDisplay = scrapy.Field() # 作者展示信息，显示文献的作者姓名

class SpeciesHostItem(scrapy.Item):
    """
    物种寄主关联列表的Item，用于存储物种与其寄主的关系信息
    """
    species_id = scrapy.Field()    # 物种的全局唯一标识 (SC_GUID)，用于关联原始物种ID
    rowid = scrapy.Field()         # 数据行号，标识当前记录的序号
    HOST_GUID = scrapy.Field()     # 寄主全局唯一标识，标识寄主的UUID
    HOST_NAME = scrapy.Field()     # 寄主英文名称，寄主的学名或英文名
    HOST_NAME_CN = scrapy.Field()  # 寄主中文名称，寄主的中文名
    HostType = scrapy.Field()      # 寄主类型，描述寄主与物种的关系（如自然寄主、为害植物等）
    Icodes = scrapy.Field()        # 关联的文献引用列表，嵌套的IcodeItem列表