create table reference_file
(
    id             bigint auto_increment comment '自增主键ID'
        primary key,
    icode          bigint                                                             not null comment '关联文献的原始标识码',
    reference_guid char(36)                                                           null comment '关联文献GUID',
    name           varchar(512)                                                       not null comment '文件名称',
    url            varchar(512)                                                       not null comment '文件存储路径',
    file_type      varchar(20)                                                        null comment '文件类型(pdf/doc等)',
    file_size      bigint                                                             null comment '文件大小(字节)',
    upload_time    datetime                                 default CURRENT_TIMESTAMP null comment '上传时间',
    checksum       varchar(64)                                                        null comment '文件校验和',
    access_level   enum ('public', 'restricted', 'private') default 'restricted'      null comment '访问权限级别',
    created_time   datetime                                 default CURRENT_TIMESTAMP not null comment '创建时间',
    update_time    datetime                                 default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    is_delete      tinyint                                  default 0                 not null comment '逻辑删除（0：未删除，1：删除）'
)
    comment '参考文献关联文件表' collate = utf8mb4_unicode_ci;

create index idx_icode
    on reference_file (icode);

create index idx_reference_guid
    on reference_file (reference_guid);

create table reference_relation
(
    id             bigint auto_increment comment '自增主键ID'
        primary key,
    species_guid   char(36)                                                              not null comment '关联物种主表的GUID',
    icode          bigint                                                                not null comment '引用文献唯一标识码',
    author_display varchar(255)                                                          null comment '文献作者显示信息（含年份）',
    title          varchar(255)                                                          null comment '文献标题',
    reference_type enum ('distribution', 'biology', 'control') default 'distribution'    null comment '引用类型（分布/生物学/防治等）',
    url            varchar(512)                                                          null comment '文献在线链接（如有）',
    created_time   datetime                                    default CURRENT_TIMESTAMP not null comment '创建时间',
    update_time    datetime                                    default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    is_delete      tinyint                                     default 0                 null comment '是否删除（0：未删除，1：删除）',
    constraint reference_relation_pk
        unique (species_guid, icode)
)
    comment '物种相关文献引用表' collate = utf8mb4_unicode_ci;

create index idx_author
    on reference_relation (author_display(50));

create index idx_icode
    on reference_relation (icode);

create index idx_species_reference
    on reference_relation (species_guid, icode);

create table species
(
    guid                         char(36)                                  not null comment '物种全局唯一标识符（UUID）'
        primary key,
    scientific_name              varchar(512)                              null comment '物种学名（标准拉丁名）',
    scientific_name_with_authors varchar(512)                              null comment '含命名人的完整学名',
    authorship                   varchar(1024)                             null comment '学名命名信息（作者+年份）',
    chinese_name                 varchar(512)                              null comment '中文名称',
    english_name                 varchar(1024)                             null comment '英文名称',
    abbreviation                 varchar(512)                              null comment '英文缩写名',
    classification               varchar(50)                               null comment '物种分类（纲/门级）',
    parent_genus                 varchar(100)                              null comment '父级属名',
    taxonomic_level              varchar(50)                               null comment '分类层级（种/属/科等）',
    sources                      text                                      null comment '数据来源（多源用分号分隔）',
    confirmation_status          varchar(20) default '待审核'              null comment '物种状态（已确认/待审核等）',
    reviewer                     varchar(512)                              null comment '审核人',
    review_time                  datetime    default '1900-01-01 00:00:00' null comment '审核时间（1900-01-01表示未审核）',
    original_risk_code           varchar(50)                               null comment '原始风险等级编码',
    is_species                   char(50)    default 'TRUE'                null comment '是否物种级',
    author                       varchar(512)                              null comment '数据创建者',
    editor                       varchar(512)                              null comment '最后编辑人',
    temp_created_time            datetime    default (now())               null comment '临时创建时间（可能为数据迁移时间）',
    created_time                 datetime    default CURRENT_TIMESTAMP     not null on update CURRENT_TIMESTAMP comment '数据创建时间',
    update_time                  datetime    default CURRENT_TIMESTAMP     not null on update CURRENT_TIMESTAMP comment '数据最后修改时间',
    is_delete                    tinyint     default 0                     not null comment '是否删除（0：未删除，1：删除）'
)
    comment '物种基本信息主表' collate = utf8mb4_unicode_ci;

create index idx_chinese_name
    on species (chinese_name);

create index idx_scientific_name
    on species (scientific_name(30));

create index idx_taxonomic_level
    on species (taxonomic_level);

create table species_association
(
    id                 bigint auto_increment comment '自增主键ID'
        primary key,
    species_guid       char(36)                           not null comment '关联物种的全局唯一标识符(UUID格式)',
    record_guid        char(36)                           null comment '关联记录的全局唯一标识符(UUID格式)',
    scientific_name    varchar(512)                       null comment '物种标准学名(拉丁名)',
    host_range         text                               null comment '寄主范围详细描述',
    potential_eco_desc text                               null comment '潜在生态影响分析',
    description        text                               null comment '物种关联关系核心描述(传播途径/互作关系等)',
    management_info    text                               null comment '防控管理措施信息',
    remark             text                               null comment '备注补充信息(可包含URL链接)',
    reference_id       varchar(50)                        null comment '关联文献标识码',
    reference_name     varchar(512)                       null comment '关联文献名称',
    page               varchar(50)                        null comment '文献引用页码或章节',
    author             varchar(512)                       null comment '记录创建者',
    editor             varchar(512)                       null comment '最后修改者',
    created_time       datetime default CURRENT_TIMESTAMP null comment '记录创建时间',
    update_time        datetime default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '最后修改时间',
    is_delete          tinyint  default 0                 not null comment '是否删除（0：未删除，1：删除）'
)
    comment '物种生态关系及管理信息表' collate = utf8mb4_unicode_ci;

create fulltext index ft_description
    on species_association (description)
    comment '全文索引用于核心内容搜索';

create fulltext index ft_management
    on species_association (management_info)
    comment '全文索引用于管理措施搜索';

create index idx_reference
    on species_association (reference_id);

create index idx_scientific_name
    on species_association (scientific_name);

create index idx_species_guid
    on species_association (species_guid);

create table species_basic_info
(
    id                            bigint auto_increment comment '自增主键ID'
        primary key,
    species_guid                  char(36)                           not null comment '物种全局唯一标识符(UUID格式)',
    record_guid                   char(36)                           not null comment '记录全局唯一标识符(UUID格式)',
    scientific_name               varchar(512)                       null comment '物种学名(拉丁名)',
    english_name                  varchar(512)                       null comment '物种英文名称',
    biological_properties         text                               null comment '生物学特性详细描述',
    morphological_characteristics text                               null comment '形态学特征描述',
    detection_method              text                               null comment '物种检测方法描述',
    distribution_description      text                               null comment '物种分布描述文本',
    icode_id                      char(36)                           null comment '关联引用文献ID',
    icode_name                    varchar(255)                       null comment '引用文献名称',
    page                          varchar(512)                       null comment '引用文献页码信息',
    remark                        text                               null comment '备注信息',
    author                        varchar(512)                       null comment '数据创建者',
    editor                        varchar(512)                       null comment '最后修改者',
    update_time                   datetime default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '最后修改时间',
    temp_created_time             datetime                           null comment '临时创建时间(用途待定)',
    temp_morphological            text                               null comment '临时形态学信息(用途待定)',
    created_time                  datetime default CURRENT_TIMESTAMP not null comment '数据创建时间'
)
    comment '物种基本信息表' collate = utf8mb4_unicode_ci;

create index idx_created_time
    on species_basic_info (created_time);

create index idx_english_name
    on species_basic_info (english_name);

create index idx_scientific_name
    on species_basic_info (scientific_name);

create table species_distribution
(
    id             bigint auto_increment comment '自增主键ID'
        primary key,
    species_guid   char(36)                           not null comment '关联物种主表的GUID',
    continent_name varchar(512)                       null comment '大陆名称（地理一级分类）',
    country_name   varchar(512)                       null comment '国家名称（地理二级分类）',
    province_name  varchar(512)                       null comment '省份/州名称（地理三级分类）',
    description    text                               null comment '分布状态描述（如存在present/不存在absent等）',
    created_time   datetime default CURRENT_TIMESTAMP not null comment '记录创建时间',
    update_time    datetime default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '最后修改时间',
    is_delete      tinyint  default 0                 not null comment '逻辑删除(0: 未删除, 1: 删除)'
)
    comment '物种地理分布记录表' collate = utf8mb4_unicode_ci;

create table species_host
(
    id               bigint auto_increment comment '自增主键ID'
        primary key,
    species_guid     char(36)                                    not null comment '关联物种的全局唯一标识符(UUID格式)',
    host_guid        char(36)                                    not null comment '寄主记录的全局唯一标识符(UUID格式)',
    host_name        varchar(512)                                null comment '寄主学名(拉丁名)',
    host_name_cn     varchar(512)                                null comment '寄主中文名称',
    host_types       varchar(255)                                null comment '寄主类型(逗号分隔，如自然寄主/接种寄主等)',
    interaction_type enum ('primary', 'secondary', 'occasional') null comment '主要寄主类型(主要/次要/偶发)',
    created_time     datetime default CURRENT_TIMESTAMP          not null comment '记录创建时间',
    updated_time     datetime default (now())                    null on update CURRENT_TIMESTAMP comment '最后更新时间',
    is_delete        tinyint  default 0                          not null comment '是否删除（0：未删除，1：删除）'
)
    comment '物种与寄主植物关联信息表' collate = utf8mb4_unicode_ci;

create fulltext index ft_host_types
    on species_host (host_types)
    comment '全文索引用于寄主类型搜索';

create index idx_host_name
    on species_host (host_name);

create index idx_host_name_cn
    on species_host (host_name_cn);

create index idx_species_guid
    on species_host (species_guid);

create table species_host_part
(
    id                  bigint auto_increment comment '自增主键ID'
        primary key,
    species_guid        char(36)                           not null comment '关联物种的全局唯一标识符(UUID格式)',
    host_guid           char(36)                           null comment '关联寄主记录的GUID(可选)',
    plant_parts         varchar(512)                       null comment '寄主植物部位(多值用分隔符表示)',
    pest_stage          varchar(512)                       null comment '害虫发育阶段(如卵/幼虫/成虫等)',
    visibility_type     varchar(512)                       null comment '害虫可见性类型(如肉眼可见/显微镜可见等)',
    spreading_way       varchar(512)                       null comment '传播途径描述',
    infection_intensity enum ('low', 'medium', 'high')     null comment '侵染强度等级',
    created_time        datetime default CURRENT_TIMESTAMP not null comment '记录创建时间',
    update_time         datetime default (now())           null on update CURRENT_TIMESTAMP comment '最后更新时间',
    is_delete           tinyint  default 0                 not null comment '是否删除（0：未删除，1：删除）'
)
    comment '物种与寄主植物部位的关联信息表' collate = utf8mb4_unicode_ci;

create index idx_pest_stage
    on species_host_part (pest_stage(50));

create index idx_plant_parts
    on species_host_part (plant_parts(50));

create index idx_species_guid
    on species_host_part (species_guid);

create table species_image
(
    id                    bigint auto_increment comment '自增主键ID'
        primary key,
    species_guid          char(36)                             not null comment '关联物种的全局唯一标识符(UUID格式)',
    image_guid            char(36)                             not null comment '图片资源的全局唯一标识符(UUID格式)',
    title                 varchar(255)                         null comment '图片标题(通常包含物种名和标识码)',
    content_description   text                                 null comment '图片内容详细描述',
    copyright_description text                                 null comment '版权声明信息',
    image_type            varchar(50)                          null comment '图片类型分类(如显微图/生态图/标本图等)',
    remark                text                                 null comment '备注补充信息',
    creator               varchar(512)                         null comment '图片记录创建者',
    editor                varchar(512)                         null comment '最后修改者',
    image_path            varchar(512)                         null comment '图片文件存储路径(相对路径)',
    image_size            bigint                               null comment '图片文件大小(字节)',
    image_mime_type       varchar(255)                         null comment '图片MIME类型(如image/jpeg)',
    order_by              int        default 0                 not null comment '展示排序权重(数字越小越靠前)',
    is_home_show          tinyint(1) default 0                 not null comment '首页展示标记(0:不展示 1:展示)',
    created_time          datetime   default CURRENT_TIMESTAMP not null comment '记录创建时间',
    update_time           datetime   default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '最后修改时间',
    is_delete             tinyint    default 0                 not null comment '是否删除（0：未删除，1：删除）'
)
    comment '物种相关图片资源信息表' collate = utf8mb4_unicode_ci;

create index idx_created_time
    on species_image (created_time);

create index idx_image_type
    on species_image (image_type);

create index idx_order_show
    on species_image (order_by, is_home_show);

create index idx_species_guid
    on species_image (species_guid);

create table species_medium
(
    id                     bigint auto_increment comment '自增主键ID'
        primary key,
    species_guid           char(36)                           not null comment '关联目标物种的全局唯一标识符(UUID格式)',
    record_guid            char(36)                           null comment '本记录的全局唯一标识符(UUID格式)',
    scientific_name        varchar(512)                       null comment '目标物种学名(拉丁名)',
    species_type           varchar(512)                       null comment '目标物种分类属性(如有害生物/媒介等)',
    medium_guid            char(36)                           null comment '媒介物种的全局唯一标识符(UUID格式)',
    medium_scientific_name varchar(512)                       null comment '媒介物种学名(拉丁名)',
    description            text                               null comment '物种与媒介的生态关系详细描述',
    medium_type            varchar(255)                       null comment '媒介功能类型(传播/携带/共生等)',
    transmission_method    varchar(512)                       null comment '具体传播方式(如虫媒/风媒等)',
    reference_id           varchar(50)                        null comment '关联文献标识码',
    reference_name         varchar(512)                       null comment '关联文献名称',
    page                   varchar(255)                       null comment '文献引用页码或章节',
    author                 varchar(512)                       null comment '记录创建者',
    editor                 varchar(512)                       null comment '最后修改者',
    temp_guid              char(36)                           null comment '临时GUID(迁移或处理中使用)',
    temp_scientific_name   varchar(512)                       null comment '临时学名(迁移或处理中使用)',
    named_year             varchar(512)                       null comment '媒介物种命名年份',
    created_time           datetime default (now())           not null comment '记录创建时间',
    update_time            datetime default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '最后修改时间',
    is_delete              tinyint  default 0                 not null comment '是否删除（0：未删除，1：删除）'
)
    comment '物种扩散传播媒介关系表' collate = utf8mb4_unicode_ci;

create fulltext index ft_description
    on species_medium (description)
    comment '全文索引用于关系描述检索';

create index idx_created_time
    on species_medium (created_time);

create index idx_medium_guid
    on species_medium (medium_guid);

create index idx_medium_name
    on species_medium (medium_scientific_name);

create index idx_medium_type
    on species_medium (medium_type);

create index idx_species_guid
    on species_medium (species_guid);

create table species_other_names
(
    id              int auto_increment comment '自增主键'
        primary key,
    species_guid    char(36)                           not null comment '关联主表的guid',
    other_name_type varchar(512)                       null comment '其他名称类型（拉丁名/英文名等）',
    named_year      varchar(100)                       null comment '命名年份',
    other_name      varchar(512)                       null comment '其他名称',
    created_time    datetime default CURRENT_TIMESTAMP not null comment '创建时间',
    update_time     datetime default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    is_delete       tinyint  default 0                 not null comment '是否删除（0：未删除，1：删除）'
)
    comment '物种别名信息表' collate = utf8mb4_unicode_ci;

create index idx_other_name
    on species_other_names (other_name(30));

create table species_reference_info
(
    id                  bigint auto_increment comment '自增主键ID'
        primary key,
    reference_guid      char(36)                              null comment '参考文献全局唯一标识符(UUID格式)',
    icode               bigint                                not null comment '文献原始标识码',
    title               varchar(512)                          not null comment '文献标题',
    source_title        varchar(512)                          null comment '来源出版物/期刊名称',
    authors             varchar(512)                          null comment '作者列表(逗号分隔)',
    author_display      varchar(512)                          null comment '作者显示格式(如"等"形式)',
    primary_category    varchar(512)                          null comment '主要分类(研究领域)',
    reference_type      varchar(512)                          null comment '文献类型(参考文献/数据源等)',
    content_type        varchar(512)                          null comment '内容形式(文章/报告等)',
    keywords            varchar(512)                          null comment '关键词(分号分隔)',
    country             varchar(512)                          null comment '出版国家/地区',
    publish_time        datetime                              null comment '文献发布时间',
    publisher           varchar(512)                          null comment '出版商名称',
    source_detail       varchar(512)                          null comment '来源详细信息(期刊卷期等)',
    type_code           varchar(50)                           null comment '类型编码',
    execute_date        datetime                              null comment '执行/处理日期',
    reference_text      text                                  null comment '完整参考文献文本',
    abstract            text                                  null comment '文献摘要',
    creator             varchar(512)                          null comment '数据创建者',
    editor              varchar(512)                          null comment '最后修改者',
    publish_person      varchar(512)                          null comment '出版负责人',
    publish_record_time datetime                              null comment '出版记录时间',
    status              varchar(20) default '待审核'          not null comment '数据状态(已确认/待审核等)',
    doi                 varchar(100)                          null comment '数字对象标识符(DOI)',
    isbn_issn           varchar(20)                           null comment 'ISBN/ISSN标识码',
    created_time        datetime    default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '记录创建时间',
    update_time         datetime    default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '最后修改时间',
    is_delete           tinyint     default 0                 not null comment '是否删除（0：未删除，1：删除）'
)
    comment '物种相关参考文献信息表' collate = utf8mb4_unicode_ci;

create fulltext index ft_abstract
    on species_reference_info (abstract)
    comment '摘要全文索引';

create fulltext index ft_keywords
    on species_reference_info (keywords)
    comment '关键词全文索引';

create fulltext index ft_title
    on species_reference_info (title)
    comment '标题全文索引';

create index idx_authors
    on species_reference_info (authors(50));

create index idx_publish_time
    on species_reference_info (publish_time);

create table species_taxonomy
(
    id                     bigint auto_increment comment '自增主键ID'
        primary key,
    species_guid           char(36)                           not null comment '关联物种的全局唯一标识符(UUID格式)',
    taxonomy_guid          char(36)                           null comment '分类层级节点的全局唯一标识符(UUID格式)',
    taxonomy_level         varchar(20)                        null comment '分类级别(如界/门/纲/目/科/属/种)',
    scientific_name        varchar(512)                       null comment '分类单元的拉丁学名',
    chinese_name           varchar(512)                       null comment '分类单元的中文名称',
    taxonomy_class         varchar(512)                       null comment '分类类别/通用名(如线虫/昆虫等)',
    parent_scientific_name varchar(512)                       null comment '父级分类单元的学名(顶级分类为NULL)',
    rank_order             int                                null comment '分类层级排序序号(可选项)',
    created_time           datetime default CURRENT_TIMESTAMP not null comment '记录创建时间',
    update_time            datetime default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '最后更新时间',
    is_delete              tinyint  default 0                 not null comment '逻辑删除(0: 未删除, 1: 删除)'
)
    comment '物种分类层级信息表' collate = utf8mb4_unicode_ci;

create index idx_parent_name
    on species_taxonomy (parent_scientific_name);

create index idx_scientific_name
    on species_taxonomy (scientific_name);

create index idx_species_guid
    on species_taxonomy (species_guid);

create index idx_taxonomy_level
    on species_taxonomy (taxonomy_level);

