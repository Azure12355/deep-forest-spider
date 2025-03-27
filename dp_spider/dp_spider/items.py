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


# 物种的父级分类信息


class SpeciesParentItem(scrapy.Item):
    # 标识字段：原始物种的 TP_GUID，用于关联当前父级分类属于哪个物种
    species_TP_GUID = scrapy.Field()
    # 父级分类的名称（科学名），可能为 null，表示当前分类的上级
    ParentSsName = scrapy.Field()
    # 分类级别，例如 "界"、"门"、"纲"、"目"、"科"、"属"
    SLevel = scrapy.Field()
    # 当前分类的科学名，例如 "Animalia"、"Nematoda"
    SSNameSci = scrapy.Field()
    # 当前分类的唯一标识符 TP_GUID
    TP_GUID = scrapy.Field()
    # 分类的类别，例如 "线虫"、"真菌"，可能为 null
    SClass = scrapy.Field()
    # 分类的中文名，例如 "动物界"、"线虫动物门"
    SCName = scrapy.Field()

# 物种关联信息

class CankaoItem(scrapy.Item):
    # 参考文献的唯一标识符
    Icode = scrapy.Field()
    # 参考文献的标题
    Title = scrapy.Field()
    # 来源出版物的标题
    SourceTitle = scrapy.Field()
    # 负责发布参考文献的作者
    IssueAuthor = scrapy.Field()
    # 作者的显示格式
    AuthorDisplay = scrapy.Field()
    # 主类型分类（例如，植物检疫）
    ITypes1 = scrapy.Field()
    # 参考文献的通用类型（例如，参考文献）
    ITypes = scrapy.Field()
    # 次级类型分类（例如，网络资源，文章）
    ITypes2 = scrapy.Field()
    # 与参考文献相关的关键字
    KeyWord = scrapy.Field()
    # 国家/地区代码的名称
    CCname = scrapy.Field()
    # 参考文献的发布时间
    PubTime = scrapy.Field()
    # 参考文献的出版商
    Publisher = scrapy.Field()
    # 来源或派生的 URL/链接
    Derivation = scrapy.Field()
    # 表示参考文献类型的代码
    TypeCode = scrapy.Field()
    # 执行或生效日期
    ExecuteDate = scrapy.Field()
    # 额外的参考信息
    Reference = scrapy.Field()
    # 参考文献的摘要或描述
    AbstractDesc = scrapy.Field()
    # TP 系统中的作者
    TP_AUTHOR = scrapy.Field()
    # TP 系统中的创建时间戳
    TP_CREATED = scrapy.Field()
    # TP 系统中的编辑者
    TP_EDITOR = scrapy.Field()
    # TP 系统中的修改时间戳
    TP_MODIFIED = scrapy.Field()
    # 负责发布的人员
    PublishPerson = scrapy.Field()
    # 发布时间
    PublishTime = scrapy.Field()
    # 参考文献的状态（例如，已确认）
    Status = scrapy.Field()

class PestRelationInfoItem(scrapy.Item):
    # 唯一行标识符
    rowid = scrapy.Field()
    # TP 系统的全局唯一标识符
    TP_GUID = scrapy.Field()
    # 物种的全局唯一标识符（请求中的 SC_GUID）
    SC_GUID = scrapy.Field()
    # 物种的科学名称
    SSNameSci = scrapy.Field()
    # 寄主范围特征
    PBCharHostRange = scrapy.Field()
    # 潜在生态影响的描述
    PotentialEcoDesc = scrapy.Field()
    # 物种关系的通用描述
    Descrip = scrapy.Field()
    # 管理相关信息
    ManagementInfo = scrapy.Field()
    # 额外的备注或注释
    Remark = scrapy.Field()
    # 参考代码的标识符
    ICodeID = scrapy.Field()
    # 参考代码的名称
    ICodeName = scrapy.Field()
    # 页码（如适用）
    Page = scrapy.Field()
    # TP 系统中的作者
    TP_AUTHOR = scrapy.Field()
    # TP 系统中的创建时间戳
    TP_CREATED = scrapy.Field()
    # TP 系统中的编辑者
    TP_EDITOR = scrapy.Field()
    # TP 系统中的修改时间戳
    TP_MODIFIED = scrapy.Field()
    # 嵌套的参考信息
    cankao = scrapy.Field(serializer=CankaoItem)


# 定义主Item，用于存储害虫寄主部位关联信息
class PestHostPartItem(scrapy.Item):
    species_id = scrapy.Field()  # 物种ID，用于标识数据所属的物种，例如 "b6d5fa52-013e-479c-8fd9-ef61ac8eeaa1"
    rowid = scrapy.Field()  # 行的唯一标识符，例如 1
    PlantParts = scrapy.Field()  # 植物受害部位，例如 "种子" 或 "种苗;组培苗"
    Peststage = scrapy.Field()  # 害虫的生命周期阶段，例如 "卵/幼虫(线虫)/成虫(线虫)" 或空字符串
    VisibilityType = scrapy.Field()  # 可见性类型，例如 "光学显微镜可见" 或空字符串
    SpreadingWay = scrapy.Field()  # 传播方式，例如空字符串（数据样例中未提供具体值）
    Icodes = scrapy.Field()  # Icodes列表，包含多个ICodeItem对象，表示相关文献或来源

# 定义CmDiffuseMediumItem，用于存储扩散媒介关联信息
class CmDiffuseMediumItem(scrapy.Item):
    species_id = scrapy.Field()  # 物种ID，用于标识数据所属的物种，例如 "b6d5fa52-013e-479c-8fd9-ef61ac8eeaa1"
    rowid = scrapy.Field()  # 行的唯一标识符，例如 1
    TP_GUID = scrapy.Field()  # 扩散媒介的唯一标识符，例如 "3e1af488-473c-4491-b90c-eaa539bf3dd4"
    SC_GUID = scrapy.Field()  # 物种全局唯一标识，与species_id相同，例如 "ec44406f-b6c9-41a3-ab4d-5d1eb9dd0b6e"
    SSNameSci = scrapy.Field()  # 物种的学名，例如 "Bursaphelenchus xylophilus"
    SpeciesType = scrapy.Field()  # 物种类型，例如 "有害生物"
    OB_GUID = scrapy.Field()  # 媒介的唯一标识符，例如 "91819c6c-5d94-4a55-92b6-41e303b71e9b"
    OB_SSNameSci = scrapy.Field()  # 媒介的学名，例如 "Monochamus"
    Descrip = scrapy.Field()  # 描述信息，详细说明物种与媒介的关系，例如松材线虫与其媒介的关系描述
    MediumType = scrapy.Field()  # 媒介类型，例如 "媒介"
    ICodeID = scrapy.Field()  # ICode的唯一标识符，例如 "15245837"
    ICodeName = scrapy.Field()  # ICode的名称，例如 "CPC2022"
    Page = scrapy.Field()  # 页码，数据样例中为null
    TP_AUTHOR = scrapy.Field()  # 作者，数据样例中为null
    TP_CREATED = scrapy.Field()  # 创建时间，例如 "2022-11-04 14:11:46.000"
    TP_EDITOR = scrapy.Field()  # 编辑者，例如 "孙珮珊"
    TP_MODIFIED = scrapy.Field()  # 修改时间，例如 "2022-11-07 15:42:20.000"
    Tmp_GUID = scrapy.Field()  # 临时GUID，数据样例中为null
    Tmp_SSNameSci = scrapy.Field()  # 临时物种学名，数据样例中为null
    NamedYear = scrapy.Field()  # 命名年份，例如 "Dejean, 1821"


# 定义IssueCodeDetailItem，用于存储参考文献详情信息
class IssueCodeDetailItem(scrapy.Item):
    species_id = scrapy.Field()  # 物种ID，用于标识数据所属的物种，例如 "b6d5fa52-013e-479c-8fd9-ef61ac8eeaa1"
    Icode = scrapy.Field()  # 参考文献的唯一标识符，例如 16104868
    Title = scrapy.Field()  # 文献标题，例如 "松材线虫病疫木生物除害技术研究"
    SourceTitle = scrapy.Field()  # 文献来源标题，数据样例中为null
    IssueAuthor = scrapy.Field()  # 文献作者，例如 "陈元生，李新远，于海萍，罗致迪"
    AuthorDisplay = scrapy.Field()  # 作者显示信息，例如 "陈元生等，2019"
    ITypes1 = scrapy.Field()  # 文献类型1，例如 "植物检疫"
    ITypes = scrapy.Field()  # 文献类型，例如 "参考文献"
    ITypes2 = scrapy.Field()  # 文献类型2，例如 "文章"
    KeyWord = scrapy.Field()  # 关键词，例如 "松材线虫病； 松褐天牛； 花绒寄甲； 疫木隔离； 茯苓种植"
    CCname = scrapy.Field()  # 国家名称，例如 "中国"
    PubTime = scrapy.Field()  # 出版时间，例如 "2019-02-28 00:00:00.000"
    Publisher = scrapy.Field()  # 出版商，数据样例中为null
    Derivation = scrapy.Field()  # 文献来源，例如 "中国植保导刊，2019 年 第 2 期"
    TypeCode = scrapy.Field()  # 类型代码，数据样例中为null
    ExecuteDate = scrapy.Field()  # 执行日期，数据样例中为null
    Reference = scrapy.Field()  # 参考文献，数据样例中为null
    AbstractDesc = scrapy.Field()  # 摘要描述，数据样例中为null
    TP_AUTHOR = scrapy.Field()  # 作者，数据样例中为 "张希玲"
    TP_CREATED = scrapy.Field()  # 创建时间，例如 "2024-03-30 16:10:48.000"
    TP_EDITOR = scrapy.Field()  # 编辑者，例如 "张希玲"
    TP_MODIFIED = scrapy.Field()  # 修改时间，例如 "2024-03-30 16:10:48.000"
    PublishPerson = scrapy.Field()  # 发布人，数据样例中为null
    PublishTime = scrapy.Field()  # 发布时间，数据样例中为null
    Status = scrapy.Field()  # 状态，例如 "已确认"