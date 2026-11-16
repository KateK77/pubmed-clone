# MedResearch V3 最终独立规格测试（100例）

唯一需求依据：`outputs/medresearch/experiments/round-03/description.md`。V3覆盖账号冲突项，其嵌入基线继续有效。本文件是尚未执行的测试设计，不能据此报告通过率。

分布：Easy 30（T001–T030）、Medium 40（T031–T070）、Hard 20（T071–T090）、Expert 10（T091–T100）。每例独立重置，由原生CUA执行实际浏览器工作流。

父代理审查后冻结本文件及JSON并登记SHA256；冻结后不依执行结果修改任务或预期。具体真实元数据manifest须在任何应用执行前按下述固定算法生成并冻结。

判定：PASS须所有判据有证据；必需产品功能缺失为FAIL；必需前置数据/邮件/故障注入/独立oracle缺失为BLOCKED；CUA或运行基础设施错误为ERROR；未执行为NOT_RUN。禁止把BLOCKED或代理误操作当作产品PASS/FAIL。

## 全局前置与测试数据契约

### G0

冻结测试后、应用执行前，在隔离实例配置合成账户/库；所有浏览器操作由原生CUA观察截图后点击/输入/按键完成。脚本可重置fixture、只读oracle、抓包和故障注入，不可代替UI工作流。每例独立重置，记录原始截图/动作和验证证据。缺必需测试环境→BLOCKED；所需产品功能缺失→FAIL；CUA误操作/工具故障→ERROR，不据此改预期或静默重试。

### AUTH

固定合成用户名 eva_a / eva_b；邮箱 eva_a@medresearch.test / eva_b@medresearch.test；初始密码 AlphaResearch8；新密码 87654321。注册用 eva_tNNN 序号账号及同名@medresearch.test地址。均指向隔离捕获邮箱，不投递真人。执行日志/仓库证据屏蔽凭证、会话和完整验证令牌。

### MAIL

通用验证流程使用隔离捕获邮箱/只读本地邮件查看UI与测试域名；允许开发filemail或SMTP捕获，但消息必须由应用实际账号流程生成，不能由测试器伪造。CUA读取验证码或链接，按应用机制填写或打开验证信息；独立记录消息生成时间/收件地址。消息捕获不可用则依赖邮件的用例BLOCKED。filemail只证明验证流程，不证明实际SMTP传输；真实传输由MAIL_SMTP与T031单独验证。

### MAIL_SMTP

T031单独要求已配置且获准使用的隔离SMTP捕获服务及本地收件箱UI。必须观察应用实际SMTP传输，不投递真人。只有filemail/控制台消息时T031为BLOCKED，不得声称实际SMTP可用；其他通用MAIL流程仍可评估。

### LIVE

每例主检索直接用真实NCBI，不注入成功假响应。预先抓取官方ESearch/ESummary/EFetch/ELink原始响应并记录URL参数、UTC时间、PMID列表与SHA256供oracle。基础记录固定PMID31452104，先验证存在；需要词/作者/期刊/DOI时只从冻结清单的真实元数据派生。动态结果比较以相邻时间窗口或同次后端外部响应为准，不能写死不断变化的总数。

### M1

在任何应用执行结果出现前冻结真实元数据manifest。候选分别用 PubMed 固定查询 cancer、diabetes、clinical trial、journal article、"Jr"[Author]、"III"[Author]、"electronic publication"、"preprint"[Publication Type]；每条查询最多前200条，sort=pub date，retmax=200。只抓真实官方元数据；各谓词选择候选中数值最小PMID，同分按查询固定顺序。未找到则该条件测试BLOCKED，不在看见应用结果后换有利文献。所需槽位：BASE=31452104；META=可用metadata字段覆盖的确定性最小记录集合；DOI=具有DOI；ABSENT_ABSTRACT=无摘要；ABSENT_FIELDS=分别无DOI/issue/pages的最小集合；SUFFIX=结构化Suffix非空；LONG=作者至少20人；UNICODE=作者或标题含非ASCII字母；EDATE=明确电子发表日期；FREE=官方有免费全文链接；PUBLISHER=出版商链接且不标免费；ABSTRACT_ONLY=有摘要但无全文链接；RELATED=ELink有相关记录；NO_RELATED=无相关关系；REFERENCES=官方提供参考文献关系；CITED_BY=官方提供被引关系；PREPRINT=官方确认为预印本。manifest每槽记录PMID、原始元数据和选中谓词。

### LEGACY

合成legacy_eva账号有6位合法历史密码246810、原先first_name/last_name值、保存文献/集合/历史，历史SUFFIX记录来自冻结官方元数据。只在独立测试DB预置，按被测版本支持的原有数据迁移导入历史fixture，不修改应用代码或把未来结构冒充旧结构；若无可信旧数据兼容fixture，本历史迁移部分BLOCKED。

### FAULT

代理/隔离网络层仅对指定请求注入timeout/429/503/截断/非法XML或把原始浏览器提交变为负向输入；不改应用源码，不替换正常主检索成功响应。预先固定触发序号、持续时间、恢复条件与日志。CUA仍执行用户输入和提交。验证服务器的独立oracle可读DB、抓包、下载文件/剪贴板/DOM；针对API确认、CSRF、对象授权的负向请求由CUA提交后代理只改指定字段，不是脚本代替UI任务。

### VERIFY

引用oracle只读冻结真实元数据并核查各格式对应的作者/后缀/标题/刊名/日期/标识及结构，不固定规格未指定的版本或标点风格。安全属性不能凭UI推断：哈希/权限/持久化/cache需独立只读DB或后端审计日志证据；oracle不可用→相关测试BLOCKED。验证器不读取实现来更改期望。

### VIEWPORT

桌面1440×900；手机390×844；可访问性用CUA Tab/Shift+Tab/Enter/Escape及读屏/DOM独立语义核查。截图证据包含控件当前焦点。

## 需求映射

| ID | 最终规格来源 | 要求 | 用例 |
|---|---|---|---|
| R001 | V3 / Account requirements | 注册及修改密码前，在密码输入框正下方可见规则。 | T031, T032, T037 |
| R002 | V3 / Account requirements | 新密码长度含边界8–128；不得附加大小写、数字、符号或常见密码、纯数字、用户名相似度限制。 | T031, T032, T033, T034, T037 |
| R003 | V3 / Account requirements | 注册及修改密码均有确认密码；浏览器和API都严格匹配，并提供明确纠正信息；登录不需确认或按新规则重新验证旧密码。 | T021, T031, T032, T033, T035, T037, T079, T096 |
| R004 | V3 / Account requirements | 移除账号UI姓、名，不要求完善资料；保存现有数据库记录及登录凭证。 | T023, T079, T096 |
| R005 | V3 / Account requirements | 账号页仅保留用户名、邮箱、修改密码及退出相关内容。 | T023, T036 |
| R006 | V3 / Account requirements | 普通注册/登录直达搜索；研究页触发认证则返回该已知内部页并保留查询/筛选；禁止任意外部回跳。 | T021, T031, T039, T077, T078, T091, T093, T100 |
| R007 | V3 / Account requirements | 仍开着的账号页会话过期后，同一用户重新登录应恢复未保存邮箱编辑。 | T040, T093, T094 |
| R008 | Round 2 / Required revisions | 不改密码时允许保存账号字段；清除冲突陈旧成功信息，字段错误明确；刷新及重新登录后保存值持久化。 | T036, T037, T093 |
| R009 | Round 2 / Required revisions | 一致处理会话丢失；本应用cookie与其他本地应用隔离。 | T040, T076, T077, T093, T094 |
| R010 | Round 2 / Required revisions | 展示与所有引用格式保留作者后缀，包括Round 1保存的元数据。 | T065, T079, T096 |
| R011 | Round 2 / Required revisions | 注册支持可配置真实邮件验证；既有账号继续访问保存研究；无邮件服务时提供明确本地开发行为。 | T031, T038, T079, T091, T096 |
| R012 | V3 / Account requirements | 未提供托管/外部SMTP时不得声称已开通公网或真人邮件投递。 | T038 |
| R013 | Master §3 Product Objective | 主搜索使用官方真实PubMed数据，不能虚构出版物。 | T002, T003, T084, T095, T097 |
| R014 | Master §4 Technology Stack | 保留React、TypeScript、Vite、Tailwind CSS、React Router、TanStack Query及Python、Django、DRF；生产PostgreSQL、本地SQLite；测试栈pytest/pytest-django、Vitest、React Testing Library、Playwright；模块边界与栈需独立工件审计。 | T098 |
| R015 | Master §5 Visual Design | 提供Home/Search/Advanced Search/Saved Articles/Collections/Search History/Profile及手机响应式导航；白底、深蓝主导航、浅灰次级表面、清晰字体、可访问表单/按钮、少干扰且一致的原创界面。 | T001, T030, T100 |
| R016 | Master §5 Visual Design | 有加载、空态、错误、校验、分页、筛选标记及适用确认对话框。 | T019, T020, T056, T059, T068, T070 |
| R017 | Master §6 Home Page | 首页有主搜索、搜索按钮、高级搜索、介绍、真实精选/热门文献、登录用户最近搜索、主题快捷链接、研究集合入口。 | T001, T008 |
| R018 | Master §7 Core Literature Search | 支持关键词、标题、作者、期刊、PMID、DOI、疾病、主题、医学术语及常见PubMed语法搜索。 | T002, T003, T004, T005, T006, T007, T008, T091, T097 |
| R019 | Master §7 Core Literature Search | 结果页显示总数、查询、当前筛选、排序、分页；文献卡片有标题、作者、期刊、年份、PMID、可用DOI、摘要预览、可用文献类型、全文可用性，并可进入详情。 | T002, T003, T009, T067 |
| R020 | Master §7 Core Literature Search | 支持10/20/50每页及服务端分页；不得把小子集误当全部结果。 | T018, T063, T069, T090, T092, T097 |
| R021 | Master §8 Sorting | 支持三个真实PubMed语义排序模式，明确显示当前模式，通过API参数或有文档依据的检索行为作用于实际全集。 | T015, T016, T017, T097 |
| R022 | Master §9 Publication Date | 支持近1/5/10年及自定义日期范围筛选。 | T041, T042, T091, T097 |
| R023 | Master §9 Article Type | 支持Clinical Trial、Randomized Controlled Trial、Review、Systematic Review、Meta-Analysis、Case Report六种文章类型。 | T043, T091, T097 |
| R024 | Master §9 Text Availability | 支持摘要、免费全文及全文可用性筛选。 | T044 |
| R025 | Master §9 Additional Filters | 支持语言、人类、其他动物、MEDLINE，及上游支持时排除预印本。 | T045, T046, T047, T097 |
| R026 | Master §9 Requirements | 多个筛选可组合，单独移除与全部清空，显示状态并更新全集搜索；有效PubMed查询，不只筛当前页。 | T041, T043, T044, T045, T046, T047, T048, T067, T069, T097 |
| R027 | Master §9 Requirements | 筛选写入URL，刷新/复制URL及浏览器前进后退保持对应搜索状态。 | T039, T048, T049, T055, T093, T097, T100 |
| R028 | Master §10 Advanced Search Builder | 高级搜索页可增删条件、选字段、选AND/OR/NOT、填词、预览、执行及保存搜索。 | T050, T051, T052, T054, T092, T100 |
| R029 | Master §10 Advanced Search Builder | 高级搜索支持七种指定字段；生成兼容PubMed查询。 | T051 |
| R030 | Master §10 Advanced Search Builder | 维护括号和逻辑运算优先级；可行时支持嵌套/分组；畸形表达式有清晰校验反馈。 | T050, T052, T053, T092, T100 |
| R031 | Master §11 Publication Detail Page | 详情显示可用标题、作者、单位、期刊、日期、卷、期、页、PMID、PMCID、DOI、摘要、关键词、MeSH、类型、全文、相关文献、可用参考文献及被引信息；不编造缺失字段。 | T009, T010, T011, T065, T067, T081, T091, T096 |
| R032 | Master §11 Publication Detail Page | 详情提供保存、复制引用、导出、打开PubMed及全文；区分免费全文、出版商链接、仅摘要，不绕付费墙。 | T013, T014, T025, T099 |
| R033 | Master §12 Related Articles | 用ELink等真实关系显示相关文献的标题、作者、年份、期刊、PMID、关系类型及可访问详情；无关系空态，不伪造相似度或被引次数。 | T012, T081 |
| R034 | Master §13 Citation Management | 支持五种引用格式，复制/导出单篇、导出多选及完整集合，以核实元数据生成。 | T029, T058, T061, T062, T063, T064, T065, T080, T091, T092, T095, T096, T099, T100 |
| R035 | Master §13 Citation Management | 引用能处理缺DOI/期/页、长作者名单、特殊字符、电子发表日期，不虚构字段。 | T064, T080 |
| R036 | Master §14 Saved Articles | 支持保存、移除、查看、搜索、排序、详情及导出；跨会话持久化，同一用户PMID不重复。 | T025, T026, T057, T058, T071, T077, T091, T095, T096, T098, T100 |
| R037 | Master §15 Research Collections | 支持集合创建、改名、删除、加/删文献、查看、集合内搜索、完整集合引用导出。 | T027, T059, T060, T086, T091, T092, T095, T096, T098, T099, T100 |
| R038 | Master §15 Research Collections | 集合属于用户；不得访问其他用户私有集合。 | T072, T073, T074, T094 |
| R039 | Master §16 Search History | 登录用户搜索历史持久化、按时间顺序显示查询/时间/筛选/排序/结果数；可重执行、删单条、清空、保存常用查询。 | T028, T054, T055, T056, T072, T091, T092, T093, T095, T098 |
| R040 | Master §17 User Accounts | 提供注册登录退出和账号管理，保护私人保存文献、集合及历史。 | T021, T022, T031, T072, T088, T094 |
| R041 | Master §17 Security | 密码哈希、会话安全、CSRF保护、输入验证、用户授权、对象级访问控制，不暴露私人数据。 | T022, T035, T037, T058, T072, T073, T074, T075, T076, T077, T078, T088, T094 |
| R042 | Master §17 User Accounts | 提供清楚标为本地演示的账号。 | T024 |
| R043 | Master §18 PubMed API Integration | 以官方E-utilities执行搜索/统计、元数据、详情/摘要及可用相关关系；保留后端服务边界。 | T012, T069, T089, T097, T099 |
| R044 | Master §18 PubMed API Integration | 适当批量获取元数据，限流/重试/缓存，不产生不必要逐篇请求；遵守执行时官方NCBI限额。 | T082, T083, T087, T089, T097 |
| R045 | Master §18 PubMed API Integration | 可选API密钥仅服务器持有，不出现在浏览器资源、请求或错误中。 | T076, T088 |
| R046 | Master §18 Important | 主搜索失败不能用虚构数据补位；只有明确标注离线模式可用核实的fixture。 | T082, T084, T095 |
| R047 | Master §19 Data Models | PMID为规范标识，避免不必要重复出版物，规范化常查字段；数据实体清单为建议而非强制表结构。 | T071, T096 |
| R048 | Master §20 REST API | 提供认证、搜索、详情、相关、高级搜索、收藏、集合、历史、引用、账号、健康检查API与生成文档；响应一致，校验查询参数、PMID和畸形检索。 | T066, T090, T099 |
| R049 | Master §21 Caching and Performance | 服务端缓存规范化请求，过期可配置并适当失效；安全处理不完整响应、批量和高效分页，避免重复网络调用，支持大结果集。 | T069, T085, T087, T092, T095, T097, T098 |
| R050 | Master §22 Error Handling | 友好处理空搜索、无结果、非法PMID、非法DOI和畸形高级检索。 | T019, T020, T042, T053, T066, T090 |
| R051 | Master §22 Error Handling | 友好处理超时、429限流及外部服务不可用，重试/恢复不伪造结果。 | T070, T082, T083, T084, T089, T095 |
| R052 | Master §22 Error Handling | 安全处理缺字段和部分外部响应，错误不导致虚构元数据或缓存污染。 | T011, T081, T085, T089 |
| R053 | Master §22 Error Handling | 处理重复收藏、越权及数据库错误，前端不暴露敏感服务器详情。 | T071, T073, T074, T086, T088, T090 |
| R054 | Master §23 Accessibility and Responsive Design | 键盘可操作、语义HTML、标签、可见焦点、适当对比度、读屏导航、可访问对话框/分页；桌面和手机响应式。 | T030, T067, T068, T100 |
| R055 | Round 2 / Required revisions | 准备可公开部署的持久PostgreSQL及服务端配置；存在真实部署URL时才添加GitHub入口。 | T098 |
| R056 | V3 / Account requirements | 更新代码、测试、设置文档、变更日志、轮次工件并发布现有私有仓库及v3.0.0-r3；保留旧发布历史。本次仅独立审计，不执行历史开发/发布指令。 | 独立工件审计，不占100个CUA用例 |
| R057 | Master §24 Automated Tests | 开发工件应包含单元/集成/e2e、确定性模拟外部服务测试及独立live smoke；不可混称最终独立评估结果。 | 独立工件审计，不占100个CUA用例 |
| R058 | Master §25–27 GitHub / README / Deliverables | 具备规定项目结构、README运行/配置/迁移/架构/测试/演示/限制及独立原型声明、轮次与版本工件；最终声称须有证据。 | T024, T098, T099 |
| R059 | Master §1 Project Identity | 品牌为MedResearch，独立教育研究原型，不冒用PubMed/NCBI/NIH/NLM官方身份或logo。 | T001 |

## 设计边界与已解析冲突

架构/依赖、所有开发测试、私有仓库发布与版本历史、全套文档/轮次工件不可能由100个用户端e2e完整证明。R012/R014/R056/R057/R058含工件审计义务；关联用例只证明其明确列出的局部，不把未审计部分宣称PASS。需在最终报告单列审计范围；不得据此前置擅自修改应用/发布版本。

- 账号页面移除姓名、密码简单规则、登录不重校验、回跳与草稿规则按V3覆盖旧基线。
- where available/where supported以执行前真实官方元数据或官方能力证据判断；缺记录前置BLOCKED，不能把产品缺失改称不适用。
- 高级分组的特定UI仅where feasible，但最终传给PubMed的括号/优先级必须保持；不强制某种树形编辑器。
- 普通注册完成（含应用需要的验证）后直达搜索；不限定验证码或链接机制。T031单独检验真实隔离SMTP，其他MAIL流程可用实际生成的本地filemail；不强制未在规格写明的验证前权限限制/令牌具体有效期。
- Most Recent与Publication Date必须按官方支持行为区分，不凭日期展示表面排序替代API验证。
- 未指定排序选项细节、引用版本标点、日期时区边界、错误文案和具体端点路径不额外强制。
- 没有公共托管/外部SMTP账号是既定范围限制；独立评估只用隔离本地捕获邮件，不要求真人投递或公网服务。

## Easy（30例）

### 导航与首页

#### T001 — 从首页访问所有主导航并确认研究入口及原创身份。

难度：Easy；类别：导航与首页；需求：R015, R017, R059

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 匿名；桌面视口；首页主数据真实可用。

**测试数据**

```json
{
  "start": "首页",
  "navigation": [
    "Home",
    "Search",
    "Advanced Search",
    "Saved Articles",
    "Collections",
    "Search History",
    "Profile"
  ]
}
```

**原生CUA工作流**

1. 打开首页
2. 查看介绍、主搜索、高级入口、主题快捷入口、精选文献和集合入口
3. 逐个访问主导航；需登录项可显示认证入口后返回首页

**预期结果**

每个规定入口可发现可达；首页内容完整，精选为真实文献，品牌/说明不冒充官方。

**客观通过判据（全部满足）**

- 七个导航目的可达或合理请求登录
- 首页列明内容均存在
- 白底、深蓝主导航、浅灰次级表面，界面清楚一致
- 精选PMID可由官方核实
- 无官方logo冒用、无虚假隶属声明

**独立验证证据**

截图、导航URL；精选PMID与官方清单核对。

#### T008 — 使用首页研究主题快捷入口发起查询。

难度：Easy；类别：导航与首页；需求：R017, R018

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 首页；实时检索可用。

**测试数据**

```json
{
  "topic": "按页面顺序第一个与医学研究相关的主题快捷链接；文本在执行前截图固定"
}
```

**原生CUA工作流**

1. 查看首页主题入口
2. 点击第一个主题
3. 核对搜索框、结果标题及官方查询

**预期结果**

快捷链接执行其标注主题搜索。

**客观通过判据（全部满足）**

- 至少有一个主题快捷入口
- 落地查询与所点主题一致
- 结果来自同次真实PubMed查询

**独立验证证据**

首页截图记录选中入口，实际出站查询及结果。

### 基础检索

#### T002 — 用首页关键词检索并核对第一页结果。

难度：Easy；类别：基础检索；需求：R013, R018, R019

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 匿名；正常实时PubMed。

**测试数据**

```json
{
  "query": "type 2 diabetes"
}
```

**原生CUA工作流**

1. 在首页输入查询
2. 点击搜索
3. 等待加载结束并观察结果总数、查询和文献卡片

**预期结果**

显示真实匹配文献、当前查询、总数、筛选/排序/分页入口和规定卡片信息。

**客观通过判据（全部满足）**

- 查询为所输入文本
- 显示总数与可用卡片字段
- 返回PMID与同次官方响应一致
- 没有演示数据替代

**独立验证证据**

截图、同次官方ESearch/元数据记录。

#### T003 — 以固定PMID找到准确文献。

难度：Easy；类别：基础检索；需求：R013, R018, R019

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 基础记录已通过LIVE预检。

**测试数据**

```json
{
  "pmid": "31452104"
}
```

**原生CUA工作流**

1. 打开搜索
2. 输入31452104并提交
3. 打开匹配文献

**预期结果**

准确返回并打开PMID31452104对应真实记录。

**客观通过判据（全部满足）**

- 结果包含准确PMID
- 详情URL或详情标识为31452104
- 标题与官方记录一致

**独立验证证据**

官方BASE元数据与截图。

#### T004 — 通过真实DOI检索已知文献。

难度：Easy；类别：基础检索；需求：R018

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- M1的DOI槽位已冻结。

**测试数据**

```json
{
  "query": "manifest.DOI.doi"
}
```

**原生CUA工作流**

1. 复制冻结清单DOI到搜索框
2. 执行搜索
3. 打开对应结果

**预期结果**

真实DOI能够定位对应PubMed文献。

**客观通过判据（全部满足）**

- 结果包含manifest.DOI.pmid
- 打开详情的DOI等于输入DOI

**独立验证证据**

官方manifest与搜索响应。

#### T005 — 通过完整文章标题定位真实文献。

难度：Easy；类别：基础检索；需求：R018

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- BASE标题在清单固定。

**测试数据**

```json
{
  "query": "manifest.BASE.title"
}
```

**原生CUA工作流**

1. 输入完整标题
2. 提交
3. 打开对应结果

**预期结果**

返回与完整标题相符的记录。

**客观通过判据（全部满足）**

- 结果含BASE的PMID
- 标题文本与官方记录一致，允许仅HTML实体/空白规范化

**独立验证证据**

同次官方检索与BASE元数据。

#### T006 — 检索指定作者的文献。

难度：Easy；类别：基础检索；需求：R018

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- BASE作者列表存在；取首位个人作者，无个人作者则前置阻塞。

**测试数据**

```json
{
  "query": "manifest.BASE.first_personal_author + [Author]"
}
```

**原生CUA工作流**

1. 在搜索框输入带Author字段的冻结作者查询
2. 搜索
3. 查看至少两条结果，若总数仅一则查看该条

**预期结果**

Author语法被支持并返回官方匹配文献。

**客观通过判据（全部满足）**

- 查询没有丢失字段限定
- 可见PMID与官方Author查询响应一致

**独立验证证据**

官方同查询结果及作者元数据。

#### T007 — 用期刊字段搜索出版物。

难度：Easy；类别：基础检索；需求：R018

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- BASE期刊字段已核实。

**测试数据**

```json
{
  "query": "manifest.BASE.journal + [Journal]"
}
```

**原生CUA工作流**

1. 输入带Journal限定的期刊查询
2. 提交
3. 打开一篇结果

**预期结果**

期刊字段检索正确。

**客观通过判据（全部满足）**

- 结果非空且属于官方查询返回集合
- 打开记录期刊与输入的官方期刊对应

**独立验证证据**

官方查询响应和截图。

#### T009 — 从结果卡片打开出版物详情并保持文献身份。

难度：Easy；类别：基础检索；需求：R019, R031

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 实时查询可返回结果。

**测试数据**

```json
{
  "query": "electronic health records"
}
```

**原生CUA工作流**

1. 搜索查询
2. 记录首张卡片PMID、标题、作者、年份
3. 点击标题
4. 核对详情身份

**预期结果**

卡片正确链接同篇出版物详情。

**客观通过判据（全部满足）**

- 卡片有全部可用规定字段
- 详情PMID与点击卡片一致
- 共有字段不矛盾

**独立验证证据**

卡片、详情截图与官方元数据。

### 文献详情

#### T010 — 检查有可用元数据的真实文献详情，包括关系型信息。

难度：Easy；类别：文献详情；需求：R031

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- M1的META最小覆盖集合及REFERENCES/CITED_BY已冻结；找不到某条件时对应检查BLOCKED，不判不存在功能通过。

**测试数据**

```json
{
  "records": "manifest.META + REFERENCES + CITED_BY"
}
```

**原生CUA工作流**

1. 逐一打开清单详情
2. 展开可用摘要、作者信息与术语区域
3. 查看参考文献和被引信息

**预期结果**

对所选官方已提供字段完整展示，所有关系与官方数据相符。

**客观通过判据（全部满足）**

- 19种详情字段中每个在oracle存在的字段均可见或可展开
- 引用/被引可用前提下能看到真实信息
- 缺失值没有被编造

**独立验证证据**

官方EFetch及ELink清单与截图逐字段核对。

#### T011 — 打开没有摘要的文献并继续使用详情。

难度：Easy；类别：文献详情；需求：R031, R052

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- M1的ABSENT_ABSTRACT固定。

**测试数据**

```json
{
  "pmid": "manifest.ABSENT_ABSTRACT.pmid"
}
```

**原生CUA工作流**

1. 打开该PMID详情
2. 查看摘要区域
3. 使用Open in PubMed

**预期结果**

缺摘要被如实表达，其他详情和外链仍正常。

**客观通过判据（全部满足）**

- 无伪造摘要或undefined/null错误文本
- PMID和标题正确
- PubMed入口可用

**独立验证证据**

官方无摘要证据与截图。

#### T013 — 打开文献的官方PubMed原始页面。

难度：Easy；类别：文献详情；需求：R032

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- BASE记录可用。

**测试数据**

```json
{
  "pmid": "31452104"
}
```

**原生CUA工作流**

1. 打开BASE详情
2. 点击Open in PubMed
3. 检查外部页面地址与文献身份

**预期结果**

进入官方PubMed该记录。

**客观通过判据（全部满足）**

- 目标主机为pubmed.ncbi.nlm.nih.gov
- 目标PMID31452104
- 未误导为MedResearch官方隶属

**独立验证证据**

原生浏览器地址及截图；不依赖外站反爬页面是否可加载判应用错误。

#### T014 — 区分免费全文、出版商链接及仅摘要记录。

难度：Easy；类别：文献详情；需求：R032

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- M1的FREE/PUBLISHER/ABSTRACT_ONLY槽位可用。

**测试数据**

```json
{
  "records": [
    "FREE",
    "PUBLISHER",
    "ABSTRACT_ONLY"
  ]
}
```

**原生CUA工作流**

1. 分别打开三类详情
2. 检查全文状态标签
3. 对有链接的记录点击Open Full Text并观察目标域名
4. 返回查看仅摘要记录

**预期结果**

正确标注可用性并指向真实授权全文来源，缺链接不伪造全文。

**客观通过判据（全部满足）**

- 免费和出版商状态清晰区分
- 目标链接与官方元数据相符
- 仅摘要记录不谎称全文免费
- 没有绕付费墙的应用流程

**独立验证证据**

官方全文链接与浏览器目标；不要求外部出版商允许免费访问。

### 相关文献

#### T012 — 从真实相关文献进入另一篇详情。

难度：Easy；类别：相关文献；需求：R033, R043

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- M1的RELATED以及其ELink结果冻结。

**测试数据**

```json
{
  "pmid": "manifest.RELATED.pmid"
}
```

**原生CUA工作流**

1. 打开详情
2. 找到相关文献区域
3. 记录首条相关记录身份与关系标签
4. 点击其标题

**预期结果**

相关项身份、标签和可用元数据正确，打开对应详情。

**客观通过判据（全部满足）**

- 相关项有标题、作者、年份、期刊、PMID的可用字段
- 关系类型明确
- 目标PMID属于官方关系集且详情一致

**独立验证证据**

ELink证据及目标元数据。

### 排序与分页

#### T015 — 使用Best Match进行真实检索。

难度：Easy；类别：排序与分页；需求：R021

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 正常PubMed；外部请求可观察。

**测试数据**

```json
{
  "query": "cancer immunotherapy",
  "sort": "Best Match"
}
```

**原生CUA工作流**

1. 执行查询
2. 选择Best Match
3. 查看当前排序指示和首个结果页

**预期结果**

以PubMed支持的相关性行为检索并指示Best Match。

**客观通过判据（全部满足）**

- 活动排序正确
- 出站参数或预先登记的检索行为符合Best Match
- 可见PMID/顺序与同次官方响应一致

**独立验证证据**

出站请求日志与ESearch结果；只看标签不足以通过。

#### T016 — 切换Most Recent排序并核实实际检索行为。

难度：Easy；类别：排序与分页；需求：R021

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 正常PubMed；查询已执行。

**测试数据**

```json
{
  "query": "cancer immunotherapy",
  "sort": "Most Recent"
}
```

**原生CUA工作流**

1. 搜索
2. 改为Most Recent
3. 查看当前模式与结果

**预期结果**

对真实匹配全集执行最近记录的PubMed排序。

**客观通过判据（全部满足）**

- 活动模式明确
- 请求或文档行为支持Most Recent
- 第一页顺序与同次官方响应一致

**独立验证证据**

请求与响应oracle；不自行把Most Recent等同出版日期。

#### T017 — 切换Publication Date排序。

难度：Easy；类别：排序与分页；需求：R021

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 正常PubMed。

**测试数据**

```json
{
  "query": "cancer immunotherapy",
  "sort": "Publication Date"
}
```

**原生CUA工作流**

1. 执行查询
2. 选择Publication Date
3. 核对结果更新

**预期结果**

使用PubMed出版日期排序并明确当前模式。

**客观通过判据（全部满足）**

- 模式与出站检索语义一致
- 真实返回顺序与官方本次响应一致

**独立验证证据**

同次ESearch顺序与元数据。

#### T018 — 在10、20、50条每页之间切换。

难度：Easy；类别：排序与分页；需求：R020

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- query官方匹配总数大于100。

**测试数据**

```json
{
  "query": "diabetes",
  "page_sizes": [
    10,
    20,
    50
  ]
}
```

**原生CUA工作流**

1. 搜索diabetes
2. 依次选择10、20、50每页
3. 每次记录可见卡片数和总数

**预期结果**

每页设置生效，显示正确数量且总数保持真实全集统计。

**客观通过判据（全部满足）**

- 各档第一页分别有10/20/50篇
- 总数非当前页长度
- 后端请求使用对应分页而非加载全部库

**独立验证证据**

截图卡片计数和出站分页记录。

### 搜索校验

#### T019 — 提交空字符串和仅空格的检索。

难度：Easy；类别：搜索校验；需求：R016, R050

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 匿名；搜索框初始为空。

**测试数据**

```json
{
  "queries": [
    "",
    "   "
  ]
}
```

**原生CUA工作流**

1. 清空搜索框提交
2. 输入三个空格再次提交

**预期结果**

友好说明需输入查询，不出现无意义错误或伪造结果。

**客观通过判据（全部满足）**

- 两种输入都安全处理
- 有可理解的输入反馈
- 无堆栈或服务器秘密泄露

**独立验证证据**

截图与出站日志；规范未要求特定错误文案。

#### T020 — 执行没有匹配文献的精确查询。

难度：Easy；类别：搜索校验；需求：R016, R050

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 预检官方查询为0；若非0则前置BLOCKED，不临场改词。

**测试数据**

```json
{
  "query": "\"medresearch_evaluation_20261115_zero_7f4d99\"[Title]"
}
```

**原生CUA工作流**

1. 输入固定查询
2. 执行并等待
3. 查看结果空态

**预期结果**

显示0结果及清晰空态，保留查询可继续修改。

**客观通过判据（全部满足）**

- 总数0
- 没有虚构记录
- 可修改查询重新使用搜索

**独立验证证据**

官方0结果与截图。

### 账号与认证

#### T021 — 正常登录后直接进入搜索。

难度：Easy；类别：账号与认证；需求：R003, R006, R040

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a存在且已验证；匿名启动。

**测试数据**

```json
{
  "username": "eva_a",
  "password_ref": "AUTH.initial"
}
```

**原生CUA工作流**

1. 从普通登录入口进入
2. 观察登录字段
3. 输入凭证并提交

**预期结果**

登录成功直达搜索，不要求确认密码或完善姓名资料。

**客观通过判据（全部满足）**

- 登录只有所需凭证，无确认密码要求
- 落地为搜索页
- 无额外资料完成阻挡

**独立验证证据**

登录前后截图/URL及只读用户会话状态。

#### T022 — 退出登录后验证私人研究访问被保护。

难度：Easy；类别：账号与认证；需求：R040, R041

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a登录且有一篇保存文献。

**测试数据**

```json
{
  "account": "eva_a"
}
```

**原生CUA工作流**

1. 从账号页退出
2. 返回Saved Articles
3. 尝试浏览器后退并刷新私人页面

**预期结果**

会话退出，私人页面不会继续提供已退出用户研究数据。

**客观通过判据（全部满足）**

- 服务端会话不可用于新请求
- 受保护入口要求登录
- 刷新不暴露旧用户私人列表

**独立验证证据**

截图及只读会话/响应状态；不把浏览器瞬间旧画面当作服务端泄露。

#### T023 — 检查精简账号页面。

难度：Easy；类别：账号与认证；需求：R004, R005

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a登录。

**测试数据**

```json
{
  "account": "eva_a"
}
```

**原生CUA工作流**

1. 打开Profile/账号页
2. 查看所有账号可编辑区域

**预期结果**

账号管理仅提供用户名、邮箱、修改密码、退出，不要求姓名或资料补全。

**客观通过判据（全部满足）**

- 不存在First name/Last name输入或必填项
- 所列四类管理能力可发现
- 可直接返回搜索

**独立验证证据**

完整账号页截图及独立DOM字段清单。

#### T024 — 使用明确标注的本地演示账号访问应用。

难度：Easy；类别：账号与认证；需求：R042, R058

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 隔离本地实例；从交付说明获取演示账号，不从真实用户获取。

**测试数据**

```json
{
  "credentials": "本地演示说明中提供的账号，执行证据脱敏"
}
```

**原生CUA工作流**

1. 打开本地演示账号说明
2. 按说明在UI登录
3. 进入搜索和自己的库

**预期结果**

演示账号被清楚标注并可登录，不指向真实用户资料。

**客观通过判据（全部满足）**

- 说明明确为本地demo
- 所示凭证可登录隔离实例
- 可到达研究功能

**独立验证证据**

说明截图、登录与库截图，脱敏。

### 保存文献

#### T025 — 从详情保存一篇文献。

难度：Easy；类别：保存文献；需求：R032, R036

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a已登录，BASE未保存。

**测试数据**

```json
{
  "pmid": "31452104"
}
```

**原生CUA工作流**

1. 打开BASE详情
2. 点击Save Article
3. 进入Saved Articles

**预期结果**

文献成功加入该用户持久书签。

**客观通过判据（全部满足）**

- 列表出现准确PMID
- 打开保存项仍是同篇
- 独立DB仅eva_a新增长该书签

**独立验证证据**

截图与只读书签记录。

#### T026 — 移除一篇已保存文献。

难度：Easy；类别：保存文献；需求：R036

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a库中仅有BASE；其他用户无关记录预置。

**测试数据**

```json
{
  "pmid": "31452104"
}
```

**原生CUA工作流**

1. 打开Saved Articles
2. 移除BASE；若有确认则确认
3. 刷新列表

**预期结果**

该用户的书签被移除且其他用户数据不受影响。

**客观通过判据（全部满足）**

- 刷新不再有该书签
- 只删除eva_a对应关系，不误删其他用户数据

**独立验证证据**

截图与只读书签/出版物身份核查。

### 研究集合

#### T027 — 创建一个空研究集合。

难度：Easy；类别：研究集合；需求：R037

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a登录；无同名集合。

**测试数据**

```json
{
  "name": "EVA Cardiology"
}
```

**原生CUA工作流**

1. 打开Collections
2. 创建EVA Cardiology
3. 打开新集合

**预期结果**

新集合归当前用户，名称正确并有清楚空态。

**客观通过判据（全部满足）**

- 集合存在且名称准确
- 可打开空集合
- 拥有者eva_a

**独立验证证据**

截图与只读集合记录。

### 搜索历史

#### T028 — 完成一次搜索后查看历史记录。

难度：Easy；类别：搜索历史；需求：R039

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a登录；历史为空。

**测试数据**

```json
{
  "query": "cardiovascular disease"
}
```

**原生CUA工作流**

1. 搜索固定查询
2. 打开Search History
3. 查看新条目
4. 返回首页检查登录用户最近搜索入口

**预期结果**

记录该搜索查询、时间、筛选、排序及结果数；首页能看到最近搜索。

**客观通过判据（全部满足）**

- 条目查询正确
- 时间落在本次操作窗口
- 默认/当前筛选与排序可解释
- 结果数与原搜索一致
- 首页最近搜索包含刚完成的query

**独立验证证据**

截图、出站搜索响应及只读历史。

### 引用与导出

#### T029 — 复制单篇APA引用。

难度：Easy；类别：引用与导出；需求：R034

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- BASE元数据固定；系统允许读取本地剪贴板oracle。

**测试数据**

```json
{
  "pmid": "31452104",
  "format": "APA"
}
```

**原生CUA工作流**

1. 打开BASE详情
2. 选择APA
3. 点击Copy Citation
4. 将剪贴板粘贴至隔离纯文本查看区

**预期结果**

剪贴板包含该篇的APA结构引用及真实元数据。

**客观通过判据（全部满足）**

- 复制成功且非空
- 作者、标题、发表年、刊名/可用标识与官方一致
- 没有拼入另一篇文献

**独立验证证据**

剪贴板文本与冻结元数据；不凭成功提示认定复制完成。

### 响应式与可访问性

#### T030 — 在手机视口使用主要导航。

难度：Easy；类别：响应式与可访问性；需求：R015, R054

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- VIEWPORT手机390×844；匿名。

**测试数据**

```json
{
  "viewport": "390x844"
}
```

**原生CUA工作流**

1. 打开首页
2. 展开手机导航
3. 依次进入搜索和高级搜索
4. 关闭导航并输入查询

**预期结果**

手机导航可发现可操作，页面主体没有阻挡输入的横向溢出。

**客观通过判据（全部满足）**

- 导航能展开/收起并到达目标
- 关键搜索控件可见可点
- 不存在导致任务不可完成的重叠或裁切

**独立验证证据**

手机全页截图与原生触控/鼠标动作。

## Medium（40例）

### 账号与认证

#### T031 — 注册新用户并通过实际SMTP捕获邮件完成验证。

难度：Medium；类别：账号与认证；需求：R001, R002, R003, R006, R011, R040

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- MAIL_SMTP可用；eva_t031不存在；匿名；普通注册入口无return参数。

**测试数据**

```json
{
  "username": "eva_t031",
  "email": "eva_t031@medresearch.test",
  "password": "abcdefgh"
}
```

**原生CUA工作流**

1. 打开注册页并在未提交前查看密码说明及确认字段
2. 输入用户名、邮箱、abcdefgh及同样确认密码
3. 提交注册并记录流程状态
4. 在隔离邮箱UI读取实际收到的验证码或链接，按应用机制完成验证
5. 普通注册完成后记录落地页面与账户状态，再退出并登录

**预期结果**

8位无复杂字符密码可注册；普通注册完成（含应用所需验证）后直达搜索；邮件验证真实完成且账号可登录。

**客观通过判据（全部满足）**

- 密码规则在输入框正下方且提交前显示
- 注册无姓名或资料补全要求
- 普通注册完成后直达搜索
- SMTP捕获到该次应用实际发出的对应收件地址邮件
- 验证完成的服务端状态有独立证据
- 再次登录成功

**独立验证证据**

截图、隔离邮箱邮件原始记录、只读用户/验证状态；邮箱基础设施不可用则BLOCKED，不能只用控制台链接判PASS。

#### T032 — 验证密码下界：7字符拒绝，8字符接受。

难度：Medium；类别：账号与认证；需求：R001, R002, R003

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- MAIL开发/捕获配置明确；eva_t032未存在；不需要声称实际投递。

**测试数据**

```json
{
  "username": "eva_t032",
  "email": "eva_t032@medresearch.test",
  "invalid_password": "aaaaaaa",
  "valid_password": "aaaaaaaa"
}
```

**原生CUA工作流**

1. 注册页查看规则
2. 输入7字符密码及相同确认并提交
3. 记录字段错误和未创建账户
4. 改为8字符及相同确认再提交

**预期结果**

7字符有明确长度提示且不创建用户；8字符按正常注册流程接受。

**客观通过判据（全部满足）**

- 规则明确8–128
- 7字符拒绝且没有用户记录
- 8字符不是因复杂度被拒绝
- 8字符注册成功无重复用户

**独立验证证据**

截图与只读用户存在性。

#### T033 — 验证密码上界：129字符拒绝，128字符接受。

难度：Medium；类别：账号与认证；需求：R002, R003

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_t033不存在；注册可用。

**测试数据**

```json
{
  "username": "eva_t033",
  "email": "eva_t033@medresearch.test",
  "invalid_password": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "valid_password": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
}
```

**原生CUA工作流**

1. 输入129字符密码及确认并尝试提交
2. 查看输入实际长度和错误
3. 清空后输入128字符及相同确认
4. 提交并重新登录确认所存密码

**预期结果**

129不能作为有效新密码被静默截断创建；128字符可完整保存并登录。

**客观通过判据（全部满足）**

- 129被明确限制/提示且未以静默截断方式创建用户
- 128完整长度被接受
- 128密码可登录
- 不附加复杂度限制

**独立验证证据**

独立DOM仅核长度、只读用户状态及CUA重新登录；不记录完整密码。

#### T034 — 分别用常见、纯数字和用户名相似密码注册。

难度：Medium；类别：账号与认证；需求：R002

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 三个合成用户均不存在；注册可用。

**测试数据**

```json
{
  "variants": [
    {
      "username": "eva_t034a",
      "password": "password"
    },
    {
      "username": "eva_t034b",
      "password": "12345678"
    },
    {
      "username": "eva_t034c",
      "password": "eva_t034c"
    }
  ],
  "email_rule": "username@medresearch.test"
}
```

**原生CUA工作流**

1. 依次为三个合成账户打开注册
2. 填写对应8–128字符密码与相同确认
3. 提交，完成必要的隔离邮件步骤
4. 退出并用相同密码登录

**预期结果**

三个有效长度密码都被接受，不受常见/纯数字/相似度隐藏规则拒绝。

**客观通过判据（全部满足）**

- 三组均注册并登录成功
- 不存在未在V3要求中的复杂度/常见密码限制
- 每个账号仅创建一次

**独立验证证据**

截图、只读账号清单和登录结果；三个变体必须全部满足才PASS。

#### T035 — 验证注册确认密码的浏览器及API精确匹配。

难度：Medium；类别：账号与认证；需求：R003, R041

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- FAULT请求代理已独立自测；eva_t035不存在。

**测试数据**

```json
{
  "username": "eva_t035",
  "password": "abcdefgh",
  "browser_mismatch": "abcdefgH",
  "proxy_mismatch": "abcdefgh "
}
```

**原生CUA工作流**

1. 输入密码abcdefgh与不同大小写确认abcdefgH并提交
2. 观察明确匹配错误
3. 改为完全一致并点击注册，由已登记代理仅把该次确认值增加一个末尾空格
4. 观察服务端拒绝
5. 关闭注入后输入完全一致值再注册

**预期结果**

浏览器和服务器均拒绝不精确相等，纠正后正常注册。

**客观通过判据（全部满足）**

- 大小写不匹配有明确错误
- 代理证据证明不匹配请求到达服务端
- 服务端拒绝且未创建用户
- 纠正后注册成功且不残留错误成功提示

**独立验证证据**

代理原始/变更请求差异脱敏记录、响应与只读DB。代理只改confirmation，CUA执行所有表单提交。

#### T036 — 密码字段为空时保存邮箱，并检查持久化和错误消息。

难度：Medium；类别：账号与认证；需求：R005, R008

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a登录；初始邮箱已验证；MAIL可用以处理应用实际要求的邮箱变更验证。

**测试数据**

```json
{
  "new_email": "eva_a_updated@medresearch.test",
  "invalid_email": "not-an-email"
}
```

**原生CUA工作流**

1. 账号页保留所有密码字段为空
2. 修改邮箱为新合成邮箱并保存
3. 按实际要求在隔离邮箱完成验证
4. 刷新页面并退出重登核对邮箱
5. 再次编辑成非法邮箱并保存
6. 核对字段错误且之前成功提示不再误导

**预期结果**

邮箱可以独立保存且跨会话保持；非法邮箱有字段提示，旧成功提示不与错误冲突。

**客观通过判据（全部满足）**

- 空密码不阻挡邮箱保存
- 刷新/重登显示新邮箱
- 原密码仍可登录
- 非法邮箱不被保存
- 出现清晰邮箱错误且无冲突旧成功信息

**独立验证证据**

截图、只读用户邮箱与凭证状态；不要求规格未指定的邮箱唯一性。

#### T037 — 修改密码时验证确认字段、服务端校验和新旧凭证行为。

难度：Medium；类别：账号与认证；需求：R001, R002, R003, R008, R041

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a登录；FAULT确认字段代理可用。

**测试数据**

```json
{
  "old_password_ref": "AUTH.initial",
  "new_password": "87654321",
  "wrong_confirm": "8765432A"
}
```

**原生CUA工作流**

1. 账号页查看新密码下方规则
2. 填入新密码与不匹配确认，提交并观察错误
3. 填一致确认再提交，由代理仅修改确认值为8765432A
4. 确认服务端拒绝
5. 关闭注入后以完全一致确认修改
6. 退出，先用旧密码登录，再用新密码登录

**预期结果**

两个校验层都拒绝不匹配；符合简单规则的新密码成功替换旧凭证。

**客观通过判据（全部满足）**

- 页面提交前规则和确认字段可见
- 浏览器/服务端不匹配均拒绝且密码不变
- 合法变更完成
- 旧密码无法登录，新密码可登录
- 错误后不显示误导成功提示

**独立验证证据**

代理证据、只读密码哈希变更时间及CUA两次登录结果；不输出哈希。

#### T038 — 在未配置SMTP的本地环境确认开发行为及已有账号可用性。

难度：Medium；类别：账号与认证；需求：R011, R012

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 独立无SMTP配置实例；eva_a原有保存文献/集合；不向任何外部邮箱发送。

**测试数据**

```json
{
  "new_user": "eva_t038",
  "email": "eva_t038@medresearch.test"
}
```

**原生CUA工作流**

1. 阅读本地账号/开发提示
2. 用已有eva_a登录并访问保存研究
3. 退出后尝试注册新合成账号
4. 观察邮件不可用时的明确说明和可用开发流程

**预期结果**

SMTP缺失的行为有明确说明；已有账户研究仍可访问，不谎称实际发送或已配置外部服务。

**客观通过判据（全部满足）**

- 已有账号可登录并打开原研究
- 开发行为有明确可见说明或可达设置文档
- 注册结果与该明确行为一致
- 未将控制台/本地验证说成真人收件成功

**独立验证证据**

UI/设置文档截图及SMTP关闭审计；具体开发策略不在规格中固定，禁止按结果临场放宽是否明确。

#### T039 — 研究页面触发登录后返回原查询与筛选。

难度：Medium；类别：账号与认证；需求：R006, R027

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 匿名；正常PubMed；固定查询已用日期及Review筛选；需要保存等认证动作。

**测试数据**

```json
{
  "query": "type 2 diabetes",
  "filters": [
    "Last 5 Years",
    "Review"
  ],
  "sort": "Publication Date"
}
```

**原生CUA工作流**

1. 执行固定查询并应用筛选、排序
2. 对结果使用需认证的研究动作
3. 在认证界面登录eva_a
4. 检查返回页面及查询筛选

**预期结果**

回到触发认证的研究页面，保留查询/筛选状态，不丢回普通默认搜索。

**客观通过判据（全部满足）**

- 返回已知内部研究页
- 查询文本与两个筛选保留
- 可继续原研究任务
- URL状态与UI一致

**独立验证证据**

认证前后截图/URL及最终查询请求。

#### T040 — 会话过期后在仍打开的账号页恢复未保存邮箱草稿。

难度：Medium；类别：账号与认证；需求：R007, R009

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a登录，账号页保持打开；外部fixture可使其服务端session过期，不清浏览器页面。

**测试数据**

```json
{
  "draft_email": "eva_a_draft@medresearch.test"
}
```

**原生CUA工作流**

1. 将邮箱编辑为草稿但不保存
2. 由前置辅助使该会话过期
3. 点击保存触发失效处理
4. 按提示以同一个eva_a重新登录
5. 回到仍打开的账号页观察编辑框
6. 保存草稿并刷新核对

**预期结果**

同用户重认证后未保存草稿恢复，用户主动保存后才持久化。

**客观通过判据（全部满足）**

- 过期前DB没有草稿邮箱
- 认证后输入框仍有完整草稿
- 恢复不误保存到其他账号
- 主动保存后持久化

**独立验证证据**

会话fixture日志、截图、只读邮箱状态；不得通过测试工具把草稿重新填回。

### 筛选与状态

#### T041 — 依次使用近1年、5年、10年筛选。

难度：Medium；类别：筛选与状态；需求：R022, R026

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 真实查询结果存在；评估UTC日期在fixture记录。

**测试数据**

```json
{
  "query": "cardiovascular disease",
  "windows": [
    1,
    5,
    10
  ]
}
```

**原生CUA工作流**

1. 搜索
2. 选择Last 1 Year并查看标记、请求、结果
3. 移除后选择Last 5 Years
4. 移除后选择Last 10 Years

**预期结果**

每种日期窗口准确映射官方有效日期约束并作用于全集。

**客观通过判据（全部满足）**

- 三个窗口各自显示且更新结果
- 出站日期语义与所选窗口一致
- 结果/总数对应同次官方日期查询
- 没有仅过滤现有页

**独立验证证据**

当前UTC时间、请求和官方响应；允许PubMed合法的年度边界定义，不强制未指定时区细节。

#### T042 — 提交有效及倒置的自定义发表日期范围。

难度：Medium；类别：筛选与状态；需求：R022, R050

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 正常PubMed。

**测试数据**

```json
{
  "query": "diabetes",
  "valid_range": [
    "2020-01-01",
    "2020-12-31"
  ],
  "invalid_range": [
    "2021-01-01",
    "2020-01-01"
  ]
}
```

**原生CUA工作流**

1. 搜索并设置有效日期范围
2. 观察结果和标记
3. 改为开始晚于结束并应用
4. 纠正为有效范围

**预期结果**

有效范围约束结果；倒置范围明确提示或阻止，不展示误导结果。

**客观通过判据（全部满足）**

- 有效范围请求/结果与官方对应
- 倒置输入有可理解反馈
- 纠正后可继续使用
- URL没有残留不适用范围

**独立验证证据**

截图、URL、官方日期查询oracle。

#### T043 — 逐项使用六种规定文章类型筛选。

难度：Medium；类别：筛选与状态；需求：R023, R026

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 正常PubMed，固定广义查询。

**测试数据**

```json
{
  "query": "cancer",
  "types": [
    "Clinical Trial",
    "Randomized Controlled Trial",
    "Review",
    "Systematic Review",
    "Meta-Analysis",
    "Case Report"
  ]
}
```

**原生CUA工作流**

1. 搜索cancer
2. 依序选择一种类型并记录结果，移除该类型后再测下一种
3. 最后清除类型筛选

**预期结果**

每个指定类型可用且转换为有效PubMed筛选。

**客观通过判据（全部满足）**

- 六种类型均可选择
- 每次标记与出站查询对应
- PMID与官方同次响应一致
- 不因个别结果类型展示简写而忽略查询正确性

**独立验证证据**

逐型请求日志及截图；全部六种通过才PASS。

#### T044 — 分别筛选摘要、免费全文和全文可用文献。

难度：Medium；类别：筛选与状态；需求：R024, R026

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 固定查询可返回结果。

**测试数据**

```json
{
  "query": "diabetes",
  "availability": [
    "Abstract Available",
    "Free Full Text",
    "Full Text Available"
  ]
}
```

**原生CUA工作流**

1. 搜索
2. 依次单独应用三个全文/摘要筛选，每次先清掉上一项
3. 打开每种筛选的一篇结果核对状态

**预期结果**

三个可用性筛选均作用于官方全集并如实标注。

**客观通过判据（全部满足）**

- 三项控件存在且可应用
- 出站PubMed筛选语义正确
- 结果标识与官方响应一致
- 选中免费全文的记录有官方支持的免费状态

**独立验证证据**

官方查询、EFetch/链接与截图。

#### T045 — 将检索限定为指定语言后恢复全部语言。

难度：Medium；类别：筛选与状态；需求：R025, R026

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- PubMed正常；语言English为固定测试值。

**测试数据**

```json
{
  "query": "hypertension",
  "language": "English"
}
```

**原生CUA工作流**

1. 搜索
2. 打开语言筛选选择English
3. 观察标记、URL和结果
4. 移除语言筛选

**预期结果**

语言筛选有效，移除后恢复未限定语言的查询。

**客观通过判据（全部满足）**

- 语言值正确进入有效PubMed查询
- 结果对应官方English查询
- 移除后请求不含该限制

**独立验证证据**

截图与前后官方请求。

#### T046 — 分别检索人类及其他动物研究。

难度：Medium；类别：筛选与状态；需求：R025, R026

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 真实PubMed正常。

**测试数据**

```json
{
  "query": "diabetes",
  "species": [
    "Humans",
    "Other Animals"
  ]
}
```

**原生CUA工作流**

1. 搜索
2. 单独选Humans，核对请求及结果
3. 移除后单独选Other Animals，核对请求及结果

**预期结果**

两种物种筛选各自使用真实有效PubMed语义。

**客观通过判据（全部满足）**

- 两种选择均可操作
- Humans与Other Animals的查询语义可区分
- 结果与对应官方请求一致

**独立验证证据**

抓包及官方响应，不只根据文献标题推断物种。

#### T047 — 使用MEDLINE子集，并在上游支持时排除预印本。

难度：Medium；类别：筛选与状态；需求：R025, R026

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 官方查询语法预检记录排除预印本是否受支持；M1 PREPRINT存在用于比较。

**测试数据**

```json
{
  "query": "COVID-19",
  "filters": [
    "MEDLINE subset",
    "Exclude preprints"
  ]
}
```

**原生CUA工作流**

1. 搜索
2. 应用MEDLINE并核对结果
3. 移除MEDLINE
4. 若官方支持排除预印本则应用该项并核对查询及预印本排除情况

**预期结果**

MEDLINE筛选有效；官方支持时必须提供正确排除预印本行为。

**客观通过判据（全部满足）**

- MEDLINE转为有效subset约束
- 支持排除预印本时该控件/功能存在并影响实际查询
- 匹配关系与官方一致
- 若官方不支持，记录条件不适用证据；不得仅因产品缺少而宣称不支持

**独立验证证据**

官方支持性预检、ESearch响应与manifest.PREPRINT。

#### T048 — 组合多个筛选，单独移除，再全部清空。

难度：Medium；类别：筛选与状态；需求：R026, R027

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 真实PubMed正常。

**测试数据**

```json
{
  "query": "cancer immunotherapy",
  "filters": [
    "Last 5 Years",
    "Review",
    "English",
    "Abstract Available"
  ]
}
```

**原生CUA工作流**

1. 搜索后应用四项筛选
2. 核对四个状态标记和结果
3. 单独移除Review
4. 核对其余三项仍在
5. 点击Clear All

**预期结果**

多筛选共同约束全集；单删不破坏其他条件，清空彻底恢复基础查询。

**客观通过判据（全部满足）**

- 每阶段URL/UI/出站查询一致
- 单删只去掉Review
- 清空后无残留过滤条件
- 各阶段总数来自真实全集

**独立验证证据**

截图、URL和三个阶段官方请求。

#### T049 — 通过刷新、复制URL与浏览器前进后退恢复搜索状态。

难度：Medium；类别：筛选与状态；需求：R027

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 浏览器允许第二标签；正常PubMed。

**测试数据**

```json
{
  "query": "electronic health records",
  "filters": [
    "Review",
    "Last 5 Years"
  ],
  "sort": "Publication Date"
}
```

**原生CUA工作流**

1. 创建查询状态A：Review
2. 增加Last 5 Years及排序形成B
3. 刷新B
4. 复制B的URL到新标签打开
5. 回原标签按浏览器后退，再前进

**预期结果**

每种导航恢复对应查询与过滤状态，UI和URL一致。

**客观通过判据（全部满足）**

- 刷新/复制URL后保持B
- 后退回到前一实际历史状态，前进恢复B
- 不展示与URL冲突的筛选结果

**独立验证证据**

各阶段URL/截图与出站查询；浏览器历史新增粒度按实际导航记录，不强制每次状态更新都另建记录。

### 高级搜索

#### T050 — 构建AND、OR、NOT混合条件并增删行。

难度：Medium；类别：高级搜索；需求：R028, R030

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 高级搜索页可用。

**测试数据**

```json
{
  "conditions": [
    "diabetes",
    "insulin",
    "metformin",
    "gestational"
  ],
  "operators": [
    "AND",
    "OR",
    "NOT"
  ]
}
```

**原生CUA工作流**

1. 添加四行条件及指定运算符
2. 检查查询预览
3. 删除第四行并观察预览
4. 重新添加NOT gestational
5. 执行搜索

**预期结果**

新增/删除与运算符变化正确进入兼容PubMed表达式。

**客观通过判据（全部满足）**

- 行增删不留下幽灵条件
- 三个运算符均可选择并保留
- 预览与提交查询语义一致
- 结果来自对应官方检索

**独立验证证据**

生成表达式、出站请求和官方结果核对；具体混合优先级另在T052测。

#### T051 — 通过七种字段分别生成并执行字段限定查询。

难度：Medium；类别：高级搜索；需求：R028, R029

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- BASE及M1元数据有相应字段；无MeSH则前置BLOCKED。

**测试数据**

```json
{
  "fields": {
    "All Fields": "diabetes",
    "Title": "diabetes",
    "Author": "manifest.BASE.first_personal_author",
    "Journal": "manifest.BASE.journal",
    "Abstract": "diabetes",
    "MeSH Terms": "Diabetes Mellitus",
    "Publication Date": "2020"
  }
}
```

**原生CUA工作流**

1. 对每个规定字段新建单行查询并填写固定词
2. 检查预览字段标签
3. 执行并返回构造器继续下一字段

**预期结果**

七种字段都产生语义正确的PubMed查询。

**客观通过判据（全部满足）**

- 七字段可选择
- 字段限制没有丢失/错映射
- 每次执行与预览一致
- 总数和PMID对应官方查询

**独立验证证据**

七次预览/请求/响应；允许合法PubMed等价字段别名。

#### T052 — 保留括号并正确执行有OR分组的AND表达式。

难度：Medium；类别：高级搜索；需求：R028, R030

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 高级页提供可行的分组UI或可编辑完整表达式入口。

**测试数据**

```json
{
  "query": "(\"large language models\" OR \"LLM\") AND \"electronic health records\""
}
```

**原生CUA工作流**

1. 在高级页用可用分组/表达式输入构建固定查询
2. 查看预览
3. 执行并检查实际查询
4. 返回并编辑组内一项后再次预览

**预期结果**

括号和逻辑优先级始终保持，不改成不同语义查询。

**客观通过判据（全部满足）**

- 提交语义等于固定表达式
- 括号没有被扁平化丢失
- 结果对应官方同表达式
- 编辑不损坏分组

**独立验证证据**

预览、外部请求和官方结果；不要求规格仅称where feasible的特定拖拽/树形编辑器。

#### T053 — 校验畸形高级检索表达式并纠正。

难度：Medium；类别：高级搜索；需求：R030, R050

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 高级查询可手动输入或由界面触发对应错误。

**测试数据**

```json
{
  "invalid": [
    "(diabetes OR cancer",
    "diabetes AND"
  ],
  "valid": "(diabetes OR cancer) AND humans[MeSH Terms]"
}
```

**原生CUA工作流**

1. 提交未闭合括号表达式
2. 记录反馈
3. 提交悬空AND表达式
4. 记录反馈
5. 改成有效表达式并执行

**预期结果**

两种畸形输入有明确反馈；有效表达式可继续检索。

**客观通过判据（全部满足）**

- 错误不能伪装为成功匹配
- 反馈解释表达式问题或需修正位置
- 修正后调用真实PubMed并显示结果

**独立验证证据**

截图与请求日志；可在前端或服务端校验，不限定实现。

#### T054 — 保存高级查询并在重新登录后再次运行。

难度：Medium；类别：高级搜索；需求：R028, R039

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a登录；无同名已保存查询。

**测试数据**

```json
{
  "query": "diabetes[Title] AND insulin[All Fields]",
  "name": "EVA insulin title study"
}
```

**原生CUA工作流**

1. 构建固定高级查询
2. 选择Save a search并填写名称（若支持名称）
3. 退出并重新登录
4. 打开已保存查询并执行

**预期结果**

常用查询持久化，可再次执行相同语义检索。

**客观通过判据（全部满足）**

- 保存条目在重登录后存在
- 查询内容未变
- 重执行使用真实官方查询
- 不会仅保存当前可见结果作为查询

**独立验证证据**

截图与只读SavedSearch记录、出站请求。

### 搜索历史

#### T055 — 从历史恢复带筛选和排序的查询。

难度：Medium；类别：搜索历史；需求：R027, R039

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a历史初始为空；正常PubMed。

**测试数据**

```json
{
  "query": "clinical natural language processing",
  "filters": [
    "Last 5 Years",
    "Review"
  ],
  "sort": "Publication Date"
}
```

**原生CUA工作流**

1. 执行固定筛选排序搜索
2. 再执行另一查询diabetes
3. 打开历史并检查时间顺序和记录字段
4. 重执行第一条研究查询

**预期结果**

历史按时间排列并完整保存/恢复研究状态。

**客观通过判据（全部满足）**

- 两条时间可区分且排序一致
- 目标记录查询/时间/筛选/排序/结果数正确
- 重执行恢复目标状态
- 当前新结果数允许随PubMed变化，不覆盖历史原统计

**独立验证证据**

历史截图、初次/重执行请求、只读历史元数据。

#### T056 — 删除一个历史项后清空其余历史。

难度：Medium；类别：搜索历史；需求：R016, R039

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a预置三条固定真实搜索历史；eva_b历史另存。

**测试数据**

```json
{
  "queries": [
    "diabetes",
    "cancer",
    "hypertension"
  ]
}
```

**原生CUA工作流**

1. 打开历史
2. 删除中间一条
3. 刷新确认仅该条消失
4. 使用Clear History，若出现确认先取消检查无变化，再重新确认清空
5. 刷新并重新登录

**预期结果**

删除及清空持久化且不影响他人历史；有确认时取消无副作用。

**客观通过判据（全部满足）**

- 单删只删除选中记录
- 清空后eva_a历史为空并跨登录保持
- eva_b历史不变
- 若有确认，取消时无删除

**独立验证证据**

截图与只读历史集合；具体哪些操作使用确认由全局可访问确认用例另外检查。

### 保存文献

#### T057 — 在保存库中搜索、排序并打开详情。

难度：Medium；类别：保存文献；需求：R036

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a保存BASE、DOI及FREE三个不同PMID，若槽位重复则按M1候选数值顺序补至三个；含各自真实年份/标题。

**测试数据**

```json
{
  "search_term": "manifest.BASE.title中的第一个长度至少5的非停用词",
  "saved_pmids": "冻结的三个不同PMID"
}
```

**原生CUA工作流**

1. 打开Saved Articles
2. 使用保存库搜索词
3. 检查匹配与非匹配项
4. 清空搜索并选择一个可用排序
5. 打开一项详情

**预期结果**

查询仅作用于个人保存库，排序与其明确标签一致，详情身份正确。

**客观通过判据（全部满足）**

- 过滤集合等于冻结库中匹配项
- 清空后恢复全部三个
- 至少提供可操作排序且顺序符合选项
- 详情PMID正确

**独立验证证据**

只读个人库与独立排序/标题匹配oracle；排序种类未指定不强制特定选项。

#### T058 — 导出个人保存库的引用并核对用户数据边界。

难度：Medium；类别：保存文献；需求：R034, R036, R041

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a库内恰好两篇不同真实记录；eva_b另保存第三篇不在A库的真实记录；下载目录隔离。

**测试数据**

```json
{
  "saved_set": "冻结的eva_a两个真实PMID",
  "other_user_only": "冻结第三个不同真实PMID",
  "format": "RIS"
}
```

**原生CUA工作流**

1. 打开Saved Articles核对两篇
2. 使用保存文献引用导出能力，若为逐篇导出则依次导出两篇
3. 打开所有下载文件进行独立审计

**预期结果**

当前用户两篇保存引用均可导出，文件合计内容准确且不包含B的独有书签。

**客观通过判据（全部满足）**

- 每篇均有非空可解析RIS输出
- 合计文献集合准确等于A的两篇
- 不混入B独有文献或私人书签信息
- 字段来自真实元数据

**独立验证证据**

下载文件SHA256、独立RIS解析与两用户保存库oracle；不要求保存库必须支持特定子集多选UI，通用多选另由T063验证。

### 研究集合

#### T059 — 重命名集合并执行有确认保护的删除。

难度：Medium；类别：研究集合；需求：R016, R037

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a集合EVA Rename已有BASE。

**测试数据**

```json
{
  "old_name": "EVA Rename",
  "new_name": "EVA Renamed"
}
```

**原生CUA工作流**

1. 重命名集合并保存
2. 刷新确认名称
3. 发起删除，检查确认对话框
4. 取消并确认集合保留
5. 再次删除并确认

**预期结果**

改名持久化；删除有可理解确认且取消安全，确认后仅移除目标集合。

**客观通过判据（全部满足）**

- 新名称刷新后仍在
- 存在可访问的删除确认
- 取消不删集合
- 确认后集合消失
- 公共文献/他人集合不被误删

**独立验证证据**

截图与只读集合/关联记录；删除集合不规定是否保留个人独立书签，但不能删无关数据。

#### T060 — 向集合添加两篇、搜索并移除其中一篇。

难度：Medium；类别：研究集合；需求：R037

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a有空集合EVA Working；两篇不同真实PMID已固定。

**测试数据**

```json
{
  "collection": "EVA Working",
  "articles": [
    "manifest.BASE",
    "manifest.DOI（若相同则清单下一不同PMID）"
  ]
}
```

**原生CUA工作流**

1. 从详情或保存库把两篇加入集合
2. 打开集合核对两篇
3. 输入唯一匹配首篇的冻结标题词搜索
4. 清空搜索并移除首篇
5. 刷新

**预期结果**

集合收录、集合内检索和移除均按目标文献工作。

**客观通过判据（全部满足）**

- 初始加入两篇准确记录
- 搜索结果不混入集合外文章
- 移除后仅剩第二篇
- 刷新状态保持

**独立验证证据**

截图与只读集合成员集合。

### 引用与导出

#### T061 — 复制同一文献的MLA与Vancouver引用。

难度：Medium；类别：引用与导出；需求：R034

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- BASE元数据固定；剪贴板oracle可用。

**测试数据**

```json
{
  "pmid": "31452104",
  "formats": [
    "MLA",
    "Vancouver"
  ]
}
```

**原生CUA工作流**

1. 打开详情
2. 选择MLA并复制到隔离文本区
3. 再选择Vancouver并复制
4. 比较两个实际剪贴板内容

**预期结果**

两个格式各自生成对应结构，文献信息准确。

**客观通过判据（全部满足）**

- 两次剪贴板确实更新
- 作者、标题、刊名、日期及可用标识正确
- 格式结构可区分且符合命名风格
- 没有undefined/null或虚构字段

**独立验证证据**

剪贴板文本及独立格式/元数据核查。

#### T062 — 分别导出单篇BibTeX与RIS。

难度：Medium；类别：引用与导出；需求：R034

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- BASE真实元数据；独立下载目录。

**测试数据**

```json
{
  "pmid": "31452104",
  "formats": [
    "BibTeX",
    "RIS"
  ]
}
```

**原生CUA工作流**

1. 打开详情
2. 导出BibTeX
3. 再导出RIS
4. 查看两个文件

**预期结果**

两个文件可各自按目标格式解析，均只有该篇。

**客观通过判据（全部满足）**

- 两个下载存在且非空
- BibTeX有有效条目结构，RIS有记录结构
- 恰好一篇且标识/标题正确
- 可用字段无编造

**独立验证证据**

文件SHA256及独立解析器，截图记录点击。

#### T063 — 在搜索结果中选择多篇导出。

难度：Medium；类别：引用与导出；需求：R020, R034

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- query有至少10条真实结果；不预设跨页选择是必需功能。

**测试数据**

```json
{
  "query": "electronic health records",
  "selected_positions": [
    1,
    3,
    5
  ],
  "format": "BibTeX"
}
```

**原生CUA工作流**

1. 执行查询并固定当前页
2. 选择第1、3、5条
3. 选择BibTeX导出
4. 独立解析下载

**预期结果**

导出准确的三篇选中真实文献。

**客观通过判据（全部满足）**

- UI支持多选
- 下载恰好三篇且与选择PMID一致
- 未选文章不混入
- 每条可解析且元数据正确

**独立验证证据**

选择前后截图、同次官方元数据及文件解析。

#### T064 — 对缺DOI、缺期号和缺页码文献生成五种引用。

难度：Medium；类别：引用与导出；需求：R034, R035

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- M1 ABSENT_FIELDS最小覆盖集固定，逐字段有官方缺失证据。

**测试数据**

```json
{
  "records": "manifest.ABSENT_FIELDS",
  "formats": [
    "APA",
    "MLA",
    "Vancouver",
    "BibTeX",
    "RIS"
  ]
}
```

**原生CUA工作流**

1. 依序打开覆盖缺失字段的真实记录
2. 对每篇生成五格式引用/导出
3. 审计生成文本及文件

**预期结果**

缺字段被安全省略/按格式合法处理，其他字段正常保留。

**客观通过判据（全部满足）**

- 每种格式可生成
- 无虚构DOI/期号/页码
- 无null/undefined/空模板污染
- 有的作者标题刊名标识不丢失

**独立验证证据**

五格式文本/文件与官方缺失字段oracle；不可拿本来有字段的记录冒充缺失。

#### T065 — 验证作者后缀在详情和全部五种引用中保留。

难度：Medium；类别：引用与导出；需求：R010, R031, R034

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- M1 SUFFIX真实结构化Suffix非空。

**测试数据**

```json
{
  "pmid": "manifest.SUFFIX.pmid",
  "suffix": "manifest.SUFFIX.author_suffix",
  "formats": [
    "APA",
    "MLA",
    "Vancouver",
    "BibTeX",
    "RIS"
  ]
}
```

**原生CUA工作流**

1. 打开详情并查看含后缀作者
2. 依次生成APA、MLA、Vancouver、BibTeX、RIS
3. 审计该作者身份

**预期结果**

后缀在展示及五格式中均保留，不与名/姓丢失合并成另一身份。

**客观通过判据（全部满足）**

- 详情该作者后缀可见
- 五格式均保留规范化后缀内容
- 作者顺序/归属正确

**独立验证证据**

官方结构化作者与格式输出；标点标准差异不当作后缀丢失。

### 搜索校验

#### T066 — 访问非法PMID并搜索格式错误的DOI。

难度：Medium；类别：搜索校验；需求：R048, R050

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 正常浏览器；非法值固定，不能替换为仅不存在但格式合法的标识。

**测试数据**

```json
{
  "invalid_pmid": "not-a-pmid",
  "invalid_doi": "10.invalid/@@@"
}
```

**原生CUA工作流**

1. 在应用文献路由中把PMID替换为not-a-pmid并导航
2. 观察错误和返回搜索能力
3. 在标识检索入口输入10.invalid/@@@并提交
4. 纠正为真实DOI再搜索

**预期结果**

错误输入得到友好反馈或明确无效/无结果处理，纠正后可继续。

**客观通过判据（全部满足）**

- 非法PMID不导致未处理崩溃
- 非法DOI不产生虚构文章
- 无敏感堆栈
- 真实DOI纠正后可以定位记录

**独立验证证据**

截图、HTTP响应状态与官方真实DOI核查；不要求存在独立DOI专用输入。

### 响应式与可访问性

#### T067 — 在手机视口筛选搜索并读完整文献详情。

难度：Medium；类别：响应式与可访问性；需求：R019, R026, R031, R054

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- VIEWPORT手机；实时查询。

**测试数据**

```json
{
  "query": "diabetes",
  "filters": [
    "Review",
    "Last 5 Years"
  ],
  "viewport": "390x844"
}
```

**原生CUA工作流**

1. 手机首页执行检索
2. 打开筛选入口应用两项
3. 滚动结果并打开详情
4. 阅读摘要和作者区域
5. 返回结果

**预期结果**

手机上能完成筛选和阅读，不因布局遮挡丢失重要操作。

**客观通过判据（全部满足）**

- 筛选可打开应用与关闭
- 活动标记可见
- 卡片和详情主要信息可读
- 返回后保留查询及筛选

**独立验证证据**

手机各阶段截图、URL与官方查询。

#### T068 — 仅用键盘操作搜索、分页及集合删除对话框。

难度：Medium；类别：响应式与可访问性；需求：R016, R054

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a登录；有EVA Keyboard集合及可分页真实查询；独立语义审计可用。

**测试数据**

```json
{
  "query": "diabetes",
  "collection": "EVA Keyboard"
}
```

**原生CUA工作流**

1. 只用Tab/Shift+Tab定位搜索框和按钮并执行
2. 键盘到下一页并激活
3. 进入集合删除确认
4. 检查初始焦点、遍历按钮并取消
5. 独立检查相关标签、导航/分页/对话框语义和对比度

**预期结果**

关键控件键盘可用、焦点可见，表单和对话框具有明确可访问含义。

**客观通过判据（全部满足）**

- 全程无需鼠标即可完成
- 焦点可见且顺序不阻断任务
- 输入有标签，导航/分页/对话框有可理解名称/语义
- 确认可取消且未删数据
- 相关文本/控件视觉清楚可辨，记录对比度测量用于解释，规格未给出的AA数值不单独作为硬失败门槛

**独立验证证据**

CUA键盘日志/截图及独立DOM/对比计算；不能仅由截图推断ARIA正确。

### 排序与分页

#### T069 — 在大结果集上翻页并核对服务端分页和筛选全集计数。

难度：Medium；类别：排序与分页；需求：R020, R026, R043, R049

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 真实query计数大于100；服务器出站日志可观察。

**测试数据**

```json
{
  "query": "diabetes",
  "page_size": 20,
  "filter": "Review"
}
```

**原生CUA工作流**

1. 执行query设20条每页
2. 记录第一页PMID
3. 进入下一页并记录
4. 应用Review并查看第一页和下一页
5. 比较各次官方分页请求与总数

**预期结果**

正确向官方/后端请求对应页，结果计数为实际筛选全集。

**客观通过判据（全部满足）**

- 页1/2对应正确偏移且各20条
- 没有前端把第一页副本当第二页
- Review总数来自全集查询
- 实际请求不下载全部结果库

**独立验证证据**

同次ESearch retstart/retmax或等价后端缓存索引证据、结果PMID与页面截图。

### 加载与反馈

#### T070 — 在可控慢网络中观察加载并完成查询。

难度：Medium；类别：加载与反馈；需求：R016, R051

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- FAULT仅为一条实时外部请求增加3秒延迟，最终透传真实响应；不改响应内容。

**测试数据**

```json
{
  "query": "cardiovascular disease",
  "delay_ms": 3000
}
```

**原生CUA工作流**

1. 打开搜索提交query
2. 在延迟期间截图观察
3. 等待真实响应结束
4. 核对加载状态结束及结果可用

**预期结果**

等待时提供可见加载反馈，完成后呈现真实结果且不残留卡住状态。

**客观通过判据（全部满足）**

- 延迟窗口存在可理解加载提示
- 成功后提示结束
- 结果与真实响应一致
- 后续可继续打开详情

**独立验证证据**

注入开始/结束时间、截图与实际官方响应。

## Hard（20例）

### 保存文献

#### T071 — 从不同入口重复保存同一PMID，并检查跨会话持久化。

难度：Hard；类别：保存文献；需求：R036, R047, R053

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a无BASE书签；真实BASE存在；可同时打开搜索与详情标签。

**测试数据**

```json
{
  "pmid": "31452104"
}
```

**原生CUA工作流**

1. 搜索BASE并从结果保存
2. 进入详情再次尝试保存
3. 打开第二标签重复已保存动作（如果按钮表示移除则不点击移除）
4. 刷新保存库
5. 退出并重新登录再查看

**预期结果**

重复保存被幂等处理或明确提示，不产生重复书签，跨会话保持一条。

**客观通过判据（全部满足）**

- 保存库只有一条BASE
- DB对eva_a与BASE只有一个保存关系
- 重新登录后仍有该条
- 共享出版物身份不无谓重复

**独立验证证据**

截图及只读用户-PMID书签/规范出版物计数；不把已保存状态下的取消按钮当作第二次保存。

### 用户隔离与安全

#### T072 — 同一浏览器切换两个用户，核查私人数据隔离。

难度：Hard；类别：用户隔离与安全；需求：R038, R039, R040, R041

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a/eva_b各有不同合成邮箱、独有保存PMID、集合和历史；共享公共文献允许。

**测试数据**

```json
{
  "accounts": [
    "eva_a",
    "eva_b"
  ],
  "private_names": [
    "EVA A Private",
    "EVA B Private"
  ]
}
```

**原生CUA工作流**

1. 用eva_a访问账号、保存库、集合、历史并记录身份
2. 退出
3. 用eva_b登录并访问同四区域
4. 后退/前进并刷新
5. 退出重登eva_a

**预期结果**

各账户只看到自己的私人研究和账号信息，不沿用前一用户缓存。

**客观通过判据（全部满足）**

- B不出现A专属邮箱/集合/书签关系/历史
- A重新登录后数据完整
- 私人响应归属与当前用户一致
- 公共PubMed文献本身不误当私人泄露

**独立验证证据**

两用户截图、只读归属清单与实际响应；任何缺环境数据则BLOCKED。

#### T073 — 直接访问另一用户的私有集合URL。

难度：Hard；类别：用户隔离与安全；需求：R038, R041, R053

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a集合EVA A Private含BASE；预先仅在fixture登记其合法URL/ID；eva_b登录。

**测试数据**

```json
{
  "target": "eva_a.private_collection_url"
}
```

**原生CUA工作流**

1. 以eva_b打开A的集合URL
2. 观察拒绝/不存在状态
3. 尝试浏览器刷新
4. 回自己的Collections正常访问

**预期结果**

即使知道对象地址也不能读取他人集合。

**客观通过判据（全部满足）**

- 页面及响应均无A集合名称/成员/私有属性
- 有友好拒绝/不存在反馈
- B自己的集合仍可用
- A数据不改变

**独立验证证据**

CUA导航截图及读响应oracle；401/403/404均可符合不泄露要求，不强制状态码。

#### T074 — 阻止通过篡改集合对象ID执行他人集合写操作。

难度：Hard；类别：用户隔离与安全；需求：R038, R041, R053

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a、eva_b各有集合；B有合法改名操作；FAULT代理可以仅替换对象ID；只读DB快照已保存。

**测试数据**

```json
{
  "victim_collection": "eva_a.private_collection_id",
  "legitimate_collection": "eva_b.private_collection_id",
  "attempted_name": "EVA unauthorized rename"
}
```

**原生CUA工作流**

1. 以eva_b打开自己的集合并输入新名称
2. 点击保存，由代理把目标ID替为A集合ID，其他认证保持B
3. 观察失败反馈
4. 关闭注入，在自己的集合正常改名
5. 重新登录A核对原集合

**预期结果**

服务端对象权限拒绝跨用户写入，合法自己操作可完成。

**客观通过判据（全部满足）**

- 被篡改请求确实抵达后端
- A集合任何属性未变
- 越权请求无成功写入
- B合法请求可成功
- 错误不泄露A私有详情

**独立验证证据**

代理差异日志、响应及两用户只读前后快照；只注入合成对象。

#### T075 — 用缺少CSRF保护的实际浏览器提交验证服务端防护。

难度：Hard；类别：用户隔离与安全；需求：R041

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a登录；同一隔离实例cookie会话认证；FAULT可删CSRF相关值并标记跨站Origin；独立确认请求抵达服务端。

**测试数据**

```json
{
  "operation": "create collection",
  "name": "EVA CSRF Probe",
  "injected_origin": "https://untrusted.medresearch.test"
}
```

**原生CUA工作流**

1. 通过CUA填写创建集合表单
2. 点击创建，代理只移除本次CSRF证明并将Origin改为隔离不可信域
3. 观察拒绝
4. 关闭注入，按正常UI再次创建

**预期结果**

伪造跨站写请求不能创建集合；正常同站请求可创建。

**客观通过判据（全部满足）**

- 负向请求服务端拒绝且无DB变更
- 不能仅凭浏览器CORS拦截宣称服务端CSRF通过
- 正常请求成功
- 会话和其他用户数据未损坏

**独立验证证据**

入站/响应日志及只读集合计数；若非cookie认证，按预先登记等价CSRF威胁模型验证且不能运行后免除要求。

#### T076 — 验证密码存储与本地应用cookie隔离。

难度：Hard；类别：用户隔离与安全；需求：R009, R041, R045

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a已有账户；只读安全oracle能在隔离DB核验密码算法而不导出散列；另一个受控本地测试应用具有同名会话cookie场景；本机HTTPS仅在配置存在时检查Secure属性。

**测试数据**

```json
{
  "app_account": "eva_a",
  "other_app": "隔离本地cookie冲突探针，不访问真实其他应用"
}
```

**原生CUA工作流**

1. 登录MedResearch并打开私人库
2. 在另一个标签登录受控本地探针并写其session/CSRF cookie
3. 返回MedResearch刷新并保存一篇文献
4. 退出MedResearch后检查探针会话仍存在
5. 在后台只读核验密码存储和会话cookie属性

**预期结果**

双方会话不会互相覆盖；密码以可识别的安全哈希形式保存，密钥不出现在客户端。

**客观通过判据（全部满足）**

- MedResearch登录在探针操作后仍有效
- 退出不误清探针会话
- DB不存明文/可逆密码，哈希格式及验证与标准算法一致
- 会话cookie安全属性与实际HTTP/HTTPS环境适当，JS不能读取HttpOnly会话值
- 客户端无服务端API密钥

**独立验证证据**

CUA截图、脱敏cookie名称/域/属性、只读哈希算法验证布尔结果；不能由登录成功推断哈希正确。

#### T088 — 在认证失败和外部故障中核查客户端不泄露凭证与私人数据。

难度：Hard；类别：用户隔离与安全；需求：R040, R041, R045, R053

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 两合成账户与服务器测试API key配置可用；独立审计器知道敏感值但输出仅命中布尔/字段名；FAULT可制造503。

**测试数据**

```json
{
  "login_attempt": {
    "username": "eva_a",
    "password": "incorrect-password"
  },
  "other_user": "eva_b",
  "fault_query": "\"biomedical informatics\""
}
```

**原生CUA工作流**

1. 以错误密码登录并查看错误
2. 用eva_a正确登录
3. 执行注入503的查询
4. 查看错误和自己的账号/研究页
5. 独立审计此次浏览器可见资源、网络及错误正文

**预期结果**

失败消息友好，客户端没有服务器key、数据库连接串、密码/会话秘密或B私人数据。

**客观通过判据（全部满足）**

- 错误密码不会登录
- UI错误不含敏感内部信息
- 浏览器响应/静态资源无服务器API key/数据库秘密
- 不出现B私人数据
- 审计不把正常HttpOnly Set-Cookie响应误判为前端泄露

**独立验证证据**

脱敏网络/资源审计、截图及敏感匹配结果；无法审计只能BLOCKED，不能以未看见UI泄漏当PASS。

### 账号与认证

#### T077 — 在会话失效后从文献保存动作重新认证并完成研究。

难度：Hard；类别：账号与认证；需求：R006, R009, R036, R041

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a登录；BASE未保存；session expiry fixture可用；含查询和筛选的结果页仍开着。

**测试数据**

```json
{
  "query": "31452104",
  "filter": "Abstract Available"
}
```

**原生CUA工作流**

1. 打开目标结果并停留
2. 由辅助使会话失效
3. 点击Save Article触发认证
4. 以eva_a登录
5. 核对返回研究状态
6. 若动作未自动完成则由用户再次点击保存
7. 到库中核对

**预期结果**

过期状态一致被识别；回到原研究页并可完成保存，避免误写匿名/他人数据。

**客观通过判据（全部满足）**

- 失效后不静默声称已保存
- 重新认证返回正确页及query/filter
- 最终恰好一条eva_a书签
- 允许用户显式重做保存，不强制规格未承诺自动重放

**独立验证证据**

会话expiry日志、认证前后截图与只读书签。

#### T078 — 检验登录回跳只允许已知内部页面。

难度：Hard；类别：账号与认证；需求：R006, R041

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 登录入口实际return参数名称由UI导航日志预先确定，不依据执行结果选择；FAULT可替换该参数；匿名。

**测试数据**

```json
{
  "malicious_destinations": [
    "https://evil.medresearch.test/collect",
    "//evil.medresearch.test/collect",
    "/unknown-evaluation-route"
  ],
  "allowed_destination": "带diabetes及Review筛选的已知搜索页"
}
```

**原生CUA工作流**

1. 通过需认证动作进入登录页
2. 依次用隔离代理把return参数换成三个固定异常目的并正常CUA登录，每次独立重置
3. 观察落地地址
4. 最后在正常内部return目的完成登录

**预期结果**

外部、协议相对及未知内部目标不会被当作允许回跳；已知内部目的可返回并保留研究状态。

**客观通过判据（全部满足）**

- 三种异常目标均未发生跳转/外部数据请求
- 异常目标被安全拒绝或落到已知内部页
- 正常内部回跳保留query/filter
- 不将unknown内部404当作已知白名单通过

**独立验证证据**

CUA登录日志、地址、网络导航记录；仅隔离保留域名，禁止真实外传。

#### T079 — 旧账号使用原短密码登录并访问历史研究，不要求姓名补全。

难度：Hard；类别：账号与认证；需求：R003, R004, R010, R011

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- LEGACY真实兼容fixture可用；其六位密码/旧姓名称值及保存研究在启动前固定。

**测试数据**

```json
{
  "account": "legacy_eva",
  "legacy_password": "246810"
}
```

**原生CUA工作流**

1. 用旧凭证登录
2. 查看账号页
3. 访问原保存文献、集合和历史
4. 在密码字段空白的情况下保存合成邮箱
5. 退出后仍用旧密码登录

**预期结果**

新密码规则不用于拒绝既有登录；旧数据保持，UI无姓名/资料完成强制。

**客观通过判据（全部满足）**

- 6位旧密码可登录
- 无确认密码或新规则复核阻挡登录
- 旧姓名字段在DB保留但不出现账号UI
- 历史研究仍可用
- 仅改邮箱不重置原凭证

**独立验证证据**

旧fixture哈希/快照、CUA截图和只读数据前后比较；缺可信旧fixture为BLOCKED。

### 引用与导出

#### T080 — 对长作者名单、特殊字符和电子发表日期生成可解析引用。

难度：Hard；类别：引用与导出；需求：R034, R035

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- M1 LONG、UNICODE、EDATE真实记录固定；独立格式解析器支持Unicode。

**测试数据**

```json
{
  "records": [
    "manifest.LONG",
    "manifest.UNICODE",
    "manifest.EDATE"
  ],
  "formats": [
    "APA",
    "MLA",
    "Vancouver",
    "BibTeX",
    "RIS"
  ]
}
```

**原生CUA工作流**

1. 分别打开固定记录核对真实元数据
2. 逐种生成五格式引用并下载适用文件
3. 将结果导入隔离独立解析器核对字段

**预期结果**

格式处理长名单、特殊字符及电子日期而不乱码或编造信息。

**客观通过判据（全部满足）**

- 五格式可生成并保留有效作者身份
- 按格式允许et al.等正规截断，不误要求全部作者展示
- Unicode字符正确或合法可还原转义
- 日期取自真实电子/出版元数据，无伪造卷页
- 下载可解析

**独立验证证据**

官方结构化数据、剪贴板/文件及独立解析；不强制规格未指定引用格式版本。

### 相关文献

#### T081 — 打开没有相关关系的数据记录并检查不虚构指标。

难度：Hard；类别：相关文献；需求：R031, R033, R052

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- M1 NO_RELATED官方ELink为空；BASE相关详情正常可用对照。

**测试数据**

```json
{
  "pmid": "manifest.NO_RELATED.pmid"
}
```

**原生CUA工作流**

1. 打开无相关关系的详情
2. 查看相关/相似区域和任何被引/相似度显示
3. 尝试继续打开PubMed或其他详情功能

**预期结果**

相关内容为空时有清楚空态；没有未经官方证实的相似度或引用次数。

**客观通过判据（全部满足）**

- 明确无相关数据而非永远加载
- 不制造相关文章/分数/计数
- 详情其他真实内容可用

**独立验证证据**

官方空ELink与截图；若真实参考/被引关系另有数据，只允许展示该独立证据支持的内容。

### 外部服务与恢复

#### T082 — 在PubMed超时后看到可理解反馈并恢复真实检索。

难度：Hard；类别：外部服务与恢复；需求：R044, R046, R051

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- FAULT让本次未缓存查询的全部上游尝试超时，直到UI显示失败或达到预登记请求/运行限额；随后完全解除；限额预先设置不改期望。

**测试数据**

```json
{
  "query": "\"mitochondrial quality control\" AND diabetes",
  "fault": "upstream timeout until explicit release"
}
```

**原生CUA工作流**

1. 提交固定未缓存查询
2. 观察加载、有限重试及最终提示
3. 解除网络故障
4. 由CUA点击重试或重新搜索
5. 打开一篇真实结果

**预期结果**

超时不无限卡住或伪造文章；故障解除后可恢复真实查询。

**客观通过判据（全部满足）**

- 失败阶段有清楚友好超时/不可用反馈
- 重试次数/等待有界且不超预先记录的安全限额
- 无虚构成功结果
- 解除后结果与官方响应一致

**独立验证证据**

代理时序、请求计数、截图与恢复后的官方响应；若CUA预算先耗尽且不足判断上界，ERROR/BLOCKED不能草率FAIL。

#### T083 — 处理上游429并遵守限流后恢复。

难度：Hard；类别：外部服务与恢复；需求：R044, R051

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- FAULT对固定查询前两次上游请求返回429及Retry-After:2，之后透传；记录执行时官方限额与配置key状态，真实请求受速率保护。

**测试数据**

```json
{
  "query": "\"cardiac rehabilitation\"",
  "fault_sequence": [
    "429 Retry-After=2",
    "429 Retry-After=2",
    "real response"
  ]
}
```

**原生CUA工作流**

1. CUA执行查询
2. 观察等待/友好限流提示
3. 让应用按其策略重试或由用户在提示后重试
4. 确认最终真实结果

**预期结果**

不会忙循环撞限额；限流后仍能恢复且UI不泄露秘密。

**客观通过判据（全部满足）**

- 没有超过官方当前限额的实际外呼
- 没有在Retry-After窗口内无节制重试
- 最终经合法重试获得真实结果或有明确可重试限流状态后用户重试成功
- 不伪造数据

**独立验证证据**

外呼时间戳、官方限额预检及截图；不固定规格未要求的重试次数。

#### T084 — 外部服务不可用时主搜索不能伪装成功或转入未标注演示。

难度：Hard；类别：外部服务与恢复；需求：R013, R046, R051

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- FAULT对未缓存查询所有上游请求返回503直到解除；若产品提供offline模式，清单已预先登记其入口。

**测试数据**

```json
{
  "query": "\"renal denervation\" AND hypertension",
  "fault": "503"
}
```

**原生CUA工作流**

1. 执行未缓存实时搜索
2. 查看最终错误和任何出现的文献
3. 如存在明确离线入口，由CUA主动进入并检查标签/数据来源
4. 退出离线模式并解除503后重搜

**预期结果**

主搜索明确失败/不可用，不用虚构文章顶替；只有主动明确离线模式可展示已核实fixtures。

**客观通过判据（全部满足）**

- 主模式无伪造成功结果
- 错误不含服务器敏感细节
- 存在离线模式时标签持续明确且记录可官方验证
- 恢复后真实查询成功

**独立验证证据**

代理响应、截图及任何展示PMID的官方核实；不要求必须实现offline模式。

#### T085 — 部分元数据返回时安全展示并避免污染后续完整结果。

难度：Hard；类别：外部服务与恢复；需求：R049, R052

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 固定真实搜索页至少10篇；FAULT只在首次对应ESummary/EFetch批响应移除第3篇记录或其摘要字段，其余字节对应真实记录；记录原始与注入差异；cache可观察。

**测试数据**

```json
{
  "query": "diabetes",
  "page_size": 10,
  "fault": "first metadata batch omits third PMID"
}
```

**原生CUA工作流**

1. CUA执行查询
2. 检查部分响应后的卡片/错误提示
3. 关闭故障
4. 按应用提供的重试/刷新途径再次访问缺失文献
5. 核对完整官方详情

**预期结果**

其他记录不被错配；缺失信息不编造；后续可获得真实完整数据而非永久污染缓存。

**客观通过判据（全部满足）**

- 第3篇缺失不被另一篇替代身份
- 可理解缺字段/部分失败状态
- 没有虚构摘要或错误作者
- 故障解除及正常cache失效/重试后可恢复完整数据
- cache不会把不完整响应当作永久完整真相

**独立验证证据**

原始官方批响应、注入差异、只读cache状态及恢复响应；可等待预登记TTL，不临场修改期待。

#### T086 — 集合保存遇到数据库错误后安全恢复。

难度：Hard；类别：外部服务与恢复；需求：R037, R053

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- FAULT可仅中断隔离测试DB连接或将本次写事务回滚，不改代码；eva_a集合EVA DB Original已有两篇。

**测试数据**

```json
{
  "old_name": "EVA DB Original",
  "new_name": "EVA DB Recovered",
  "fault": "one collection rename transaction cannot commit"
}
```

**原生CUA工作流**

1. 打开集合改名
2. 在已安排DB故障期间点击保存
3. 观察错误并刷新
4. 恢复数据库
5. 由CUA再次改名保存并重开集合

**预期结果**

失败不伪称持久化成功，原数据安全；恢复后操作成功。

**客观通过判据（全部满足）**

- 失败时友好提示且无SQL/凭证/堆栈
- 失败事务没有半写或成员丢失
- 恢复后名称准确并持久化
- 两篇成员完整

**独立验证证据**

只读DB前后快照、故障日志和截图；基础设施必须可控恢复，否则BLOCKED。

#### T089 — 处理格式损坏的PubMed响应并在恢复后继续打开真实详情。

难度：Hard；类别：外部服务与恢复；需求：R043, R044, R051, R052

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- FAULT对首次BASE EFetch响应返回不可解析的截断XML，后续保持故障到友好提示，解除后透传；BASE缓存从隔离环境清理。

**测试数据**

```json
{
  "pmid": "31452104",
  "fault": "malformed truncated XML"
}
```

**原生CUA工作流**

1. CUA打开BASE详情
2. 观察错误/重试状态
3. 解除故障
4. 通过UI重试或刷新
5. 核对完整详情

**预期结果**

解析失败不暴露堆栈、不生成半真半假详情，恢复后真实数据可用。

**客观通过判据（全部满足）**

- 格式错误有可理解反馈
- 无未经核实拼接字段或虚构内容
- 不把畸形响应写成可复用完整cache
- 恢复后PMID/标题/摘要与官方一致

**独立验证证据**

故障代理日志、响应hash、只读cache和恢复详情截图。

### 缓存与性能

#### T087 — 检查重复查询缓存、参数隔离及配置过期后的重新检索。

难度：Hard；类别：缓存与性能；需求：R044, R049

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 隔离环境TTL预先设为60秒；外呼/cache观察器可读；任何查询正常成功；fixture不改应用代码。

**测试数据**

```json
{
  "query": "diabetes",
  "same_query_variant": "  diabetes  ",
  "changed_filter": "Review",
  "ttl_seconds": 60
}
```

**原生CUA工作流**

1. CUA搜索diabetes并记录结果
2. 60秒内再次搜索diabetes及前后空格变体
3. 加入Review搜索
4. 在缓存TTL过期后重新执行初始无筛选查询

**预期结果**

等价规范化请求复用适当缓存，不混用不同筛选；过期后重新验证上游。

**客观通过判据（全部满足）**

- 重复等价查询没有不必要重复上游元数据请求
- Review与无筛选缓存隔离且结果正确
- 60秒配置被应用，过期后可观察必要刷新
- 不因cache返回错误用户私人数据

**独立验证证据**

外呼次数/参数/时间戳、cache只读条目及同次官方响应；不要求精确零请求，允许合理重新验证。

### API输入与文档

#### T090 — 通过真实搜索UI提交被篡改的非法分页参数并恢复。

难度：Hard；类别：API输入与文档；需求：R020, R048, R050, R053

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- FAULT可仅修改CUA触发搜索请求的page/page_size等实际等价参数；先记录正常参数名；DB/上游请求可观察。

**测试数据**

```json
{
  "variants": [
    {
      "page": -1
    },
    {
      "page_size": 0
    },
    {
      "page_size": "not-a-number"
    }
  ],
  "valid_size": 20
}
```

**原生CUA工作流**

1. 正常搜索diabetes确认界面可用
2. 依次点击下一页/分页设置，每次由代理仅替换指定参数为固定非法值
3. 记录用户反馈和服务器返回
4. 关闭注入恢复20条第一页

**预期结果**

后台校验非法参数，不发生异常全集加载、敏感错误或错配状态；恢复后正常分页。

**客观通过判据（全部满足）**

- 三组非法参数均明确拒绝或以文档定义安全默认值规范化
- 无未处理500/敏感内部信息
- 不因异常参数下载整个结果集
- 正常参数恢复后20条结果准确

**独立验证证据**

修改前后请求差异、响应与官方外呼日志；合法默认行为必须在执行前文档登记。

## Expert（10例）

### 完整研究流程

#### T091 — 新研究者完成注册、主题筛选、选文、建库及导出综述资料。

难度：Expert；类别：完整研究流程；需求：R006, R011, R018, R022, R023, R031, R034, R036, R037, R039

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- MAIL可用；eva_t091不存在；查询真实结果至少三篇；下载/剪贴板oracle就绪。

**测试数据**

```json
{
  "username": "eva_t091",
  "email": "eva_t091@medresearch.test",
  "password": "research",
  "query": "type 2 diabetes",
  "filters": [
    "Last 5 Years",
    "Review"
  ],
  "collection": "EVA Diabetes Review",
  "selection": "筛选后同次官方第一页前三个不同PMID",
  "export_format": "Vancouver"
}
```

**原生CUA工作流**

1. 通过UI注册，并按应用验证码或链接机制完成隔离邮件验证；普通注册完成后核对直达搜索
2. 执行主题检索并应用两个筛选
3. 打开前三篇检查真实详情并各自保存
4. 创建研究集合并把三篇加入
5. 从完整集合导出Vancouver引用
6. 退出并重新登录
7. 从历史重开研究，再检查库和集合

**预期结果**

整个新用户研究链路身份与查询状态一致，选定文章、集合和导出跨会话完整保存。

**客观通过判据（全部满足）**

- 注册符合V3且实际生成消息的验证流程成功
- 三篇PMID等于官方选中集合
- 保存库和集合重登录后均含三篇
- 集合导出三篇完整真实引用
- 历史恢复原query/filter
- 无跨用户混入

**独立验证证据**

端到端截图/动作、邮件捕获及验证证据、官方响应、只读用户/研究数据及下载审计。

#### T092 — 维护超过一页的大型文献集合并导出完整集合。

难度：Expert；类别：完整研究流程；需求：R020, R028, R030, R034, R037, R039, R049

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a有EVA Evidence Set，预置LIBRARY55真实记录；M1扩展清单LIBRARY55由固定diabetes查询sort=pub date的前55个不同PMID构成，在执行前取官方元数据冻结；下载审计可用。

**测试数据**

```json
{
  "collection": "EVA Evidence Set",
  "initial_count": 55,
  "advanced_query": "(diabetes[Title] OR insulin[Title]) AND therapy[All Fields]",
  "formats": [
    "BibTeX",
    "RIS"
  ]
}
```

**原生CUA工作流**

1. 从高级搜索构建固定表达式并保存查询
2. 执行并选择预检固定的新增PMID（固定高级查询官方第一页20篇中顺序第一篇未在LIBRARY55的记录；整页无合格记录则前置BLOCKED）
3. 把该篇加入EVA Evidence Set
4. 打开集合并按标题搜索刚加入文章
5. 清除集合内搜索
6. 分别导出整个集合为BibTeX和RIS
7. 重登录后运行已保存查询

**预期结果**

大型集合搜索正常，完整导出跨越当前可见页且包含新加入记录；保存查询持久。

**客观通过判据（全部满足）**

- 最终集合56个唯一PMID
- 两种完整集合导出都恰好56篇，与集合全集相等
- 导出不受之前集合内搜索/当前可见页截断
- 保存查询重登录可再执行
- 无全库下载行为

**独立验证证据**

冻结55+1真实清单、只读集合全集及独立导出解析；若无56篇真实预检数据则BLOCKED。

### 账号与研究恢复

#### T093 — 保持两标签研究工作并从账号会话过期中恢复未保存邮箱。

难度：Expert；类别：账号与研究恢复；需求：R006, R007, R008, R009, R027, R039

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a登录；两标签分别为带筛选研究结果与账号页；session expiry fixture/MAIL可用；账号页不能关闭。

**测试数据**

```json
{
  "query": "electronic health records",
  "filters": [
    "Review",
    "Last 5 Years"
  ],
  "draft_email": "eva_a_multitab@medresearch.test"
}
```

**原生CUA工作流**

1. 标签一执行固定带筛选查询
2. 标签二编辑邮箱为草稿，不保存
3. 前置使会话过期
4. 在账号页点击保存并完成同一用户认证
5. 确认草稿恢复并主动保存，按需验证邮件
6. 切回研究标签刷新并核对原query/filter
7. 从历史重新运行该研究并保存一篇

**预期结果**

重认证既恢复账号草稿也保留独立研究页面状态，最终保存属于同一用户。

**客观通过判据（全部满足）**

- 草稿在同用户认证后完整恢复且未被旧服务端邮箱覆盖
- 主动保存后邮箱持久化
- 研究标签query/filter保持
- 历史重执行与最终书签正确
- 没有重复用户/错误身份写入

**独立验证证据**

双标签截图、会话expiry记录、只读邮箱/历史/书签以及实际邮件捕获记录。

### 用户隔离与安全

#### T094 — 会话过期后换另一账号，防止未保存邮箱和研究操作串到新用户。

难度：Expert；类别：用户隔离与安全；需求：R007, R009, R038, R040, R041

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- A/B独立账号及研究；A账号页未保存草稿仍开着；expiry fixture可用。

**测试数据**

```json
{
  "a_draft_email": "eva_a_do_not_leak@medresearch.test",
  "b_email": "eva_b@medresearch.test",
  "b_collection": "EVA B New Session"
}
```

**原生CUA工作流**

1. A在账号页输入草稿但不保存
2. 使A会话过期
3. 在重认证流程改用B登录
4. 查看账号页并核对身份和邮箱
5. 通过B创建集合并保存一篇真实文献
6. 退出后重新登录A检查邮箱及研究

**预期结果**

同用户草稿保留规则不会把A草稿应用给B；新会话研究写入正确归属。

**客观通过判据（全部满足）**

- B页面不将A邮箱草稿呈现为B的待保存数据
- B服务端邮箱未被A草稿覆盖
- 新集合/书签仅属于B
- A邮箱未在未主动保存时改变
- A/B原私有研究无混用

**独立验证证据**

两用户前后只读快照、CUA切换截图；不要求跨用户保存A草稿，因为规格只保证同用户恢复。

### 研究与服务恢复

#### T095 — 外部PubMed停机期间保持已有研究资料可信，恢复后继续扩展集合。

难度：Expert；类别：研究与服务恢复；需求：R013, R034, R036, R037, R039, R046, R049, R051

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- eva_a有已存完整真实元数据的两篇书签和集合；此前研究历史存在；FAULT对所有新的PubMed外呼返回503，现有DB不受影响；下载oracle可用。

**测试数据**

```json
{
  "collection": "EVA Offline Recovery",
  "saved_records": "冻结两篇真实完整记录",
  "new_query": "\"cardiac rehabilitation\" AND exercise"
}
```

**原生CUA工作流**

1. 在故障前打开库及集合核对两篇
2. 开启上游503故障
3. 从集合导出已有两篇RIS
4. 执行新的实时查询并观察明确失败
5. 重开保存研究核对未受损
6. 解除故障
7. 通过历史/搜索重执行新查询，选择一篇新文献加入集合
8. 重新导出完整集合

**预期结果**

外部失败不伪造新结果或损坏持久研究；已有完整元数据引用仍可信，恢复后集合可扩展。

**客观通过判据（全部满足）**

- 故障期导出包含原两篇正确元数据
- 新查询失败明确且没有虚构替代
- 原私人数据完整
- 恢复后新文献真实加入，集合恰好三篇
- 最终导出三篇准确

**独立验证证据**

故障日志、官方恢复响应、只读库/集合及前后RIS文件。

### 旧数据兼容与引用

#### T096 — 使用旧账号继续整理含作者后缀的历史文献并全格式导出。

难度：Expert；类别：旧数据兼容与引用；需求：R003, R004, R010, R011, R031, R034, R036, R037, R047

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- LEGACY提供可信Round1兼容记录，SUFFIX后缀官方可核实；保留旧姓名字段与六位凭证；记录初始私有集合和metadata快照。

**测试数据**

```json
{
  "account": "legacy_eva",
  "historical_pmid": "manifest.SUFFIX.pmid",
  "new_collection": "EVA Legacy Continued",
  "formats": [
    "APA",
    "MLA",
    "Vancouver",
    "BibTeX",
    "RIS"
  ]
}
```

**原生CUA工作流**

1. 用原短密码登录
2. 从旧保存库打开含后缀文献
3. 核对详情后将其加入新集合
4. 再次通过实时PMID搜索同篇并检查保存状态
5. 把新集合分别导出五格式
6. 退出重新登录并查看旧研究及新集合

**预期结果**

旧凭证和记录保留；重取同篇不丢作者后缀或产生重复，研究可继续组织并导出。

**客观通过判据（全部满足）**

- 旧账号无需补姓名/重设密码即可访问
- 旧收藏和集合仍完整
- 实时重取后身份/后缀保持
- 用户同PMID没有重复书签/不必要出版物重复
- 新集合五格式均保留后缀且可用
- 重登录后新旧研究均在

**独立验证证据**

兼容fixture证据、只读原始/最终数据、官方SUFFIX记录与五格式文件。

### 真实检索一致性

#### T097 — 执行多条件大规模检索并审计排序、全集计数与深分页。

难度：Expert；类别：真实检索一致性；需求：R013, R018, R020, R021, R022, R023, R025, R026, R027, R043, R044, R049

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 真实PubMed；预检固定query/filter下结果至少150，目标第3页须在执行时官方合法检索窗口内，否则BLOCKED而非改查询；同次外呼日志和缓存证据可用。

**测试数据**

```json
{
  "query": "diabetes AND therapy",
  "date_range": [
    "2020-01-01",
    "2025-12-31"
  ],
  "filters": [
    "Review",
    "English"
  ],
  "sort": "Publication Date",
  "page_size": 50,
  "target_page": 3
}
```

**原生CUA工作流**

1. 输入固定query
2. 设置日期范围、Review、English与Publication Date
3. 设50条每页
4. 记录第一页和总数
5. 翻到第二、第三页
6. 复制当前URL到新标签并核对状态
7. 移除Review筛选并比较实际全集查询

**预期结果**

复合查询语义、排序、统计与每一页均对应真实上游响应，不限于最初缓存小子集。

**客观通过判据（全部满足）**

- 前三页各50篇且各自偏移正确
- 总数等于同次官方复合查询计数
- 排序真实作用于全集
- URL恢复query/filter及可表达分页状态
- 移除Review后的计数/结果对应更宽查询
- 请求批量/分页有界且遵守官方速率

**独立验证证据**

同次ESearch/批元数据日志、三页PMID清单、URL截图；动态库变化仅依同次证据判断，不用陈旧固定总数；不要求突破NCBI官方检索窗口（包括适用的10000条上限），也不因不可达超上限页判产品失败。

### 持久化与部署准备

#### T098 — 在配置为PostgreSQL的隔离部署重启服务后继续研究。

难度：Expert；类别：持久化与部署准备；需求：R014, R036, R037, R039, R049, R055, R058

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 独立PostgreSQL实例与按交付说明启动的应用；可受控停止/启动服务且不清DB；只读DB配置/索引审计；不部署公网、不读写生产库。

**测试数据**

```json
{
  "account": "eva_a",
  "collection": "EVA Restart Durable",
  "query": "diabetes",
  "pmid": "31452104"
}
```

**原生CUA工作流**

1. 通过UI登录并搜索BASE保存书签
2. 创建集合并加入BASE
3. 执行固定query留下历史
4. 按交付启动说明由环境辅助重启应用服务，保留数据库
5. CUA刷新，按需重新登录
6. 检查账号、书签、集合、历史并导出引用

**预期结果**

服务重启后持久研究完整；生产配置使用持久PostgreSQL，文档足以恢复运行。

**客观通过判据（全部满足）**

- 只读连接证据确认PostgreSQL而非临时SQLite
- 服务重启不清除用户/书签/集合/历史
- 重登录和导出可用
- 服务端环境配置可用且不泄露客户端
- 与此研究路径相关查找/关联存在合理索引的只读证据

**独立验证证据**

启动/重启日志、脱敏DB类型/索引审计、前后只读数据及CUA截图；框架栈/全部架构/源码发布另作工件审计，不凭此一例宣称全覆盖。

### API输入与文档

#### T099 — 完成研究操作并利用生成API文档核对对应服务及健康检查。

难度：Expert；类别：API输入与文档；需求：R032, R034, R037, R043, R048, R058

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- 交付说明能提供API文档/health入口；所有导航由CUA浏览器完成；独立抓包oracle可关联用户动作与API。

**测试数据**

```json
{
  "query": "31452104",
  "collection": "EVA API Contract",
  "required_endpoint_domains": [
    "Authentication",
    "Publication search",
    "Publication details",
    "Related publications",
    "Advanced search",
    "Saved publications",
    "Collections",
    "Search history",
    "Citation export",
    "User profile",
    "Health check"
  ]
}
```

**原生CUA工作流**

1. CUA登录、搜索BASE并打开详情和相关区域
2. 保存BASE并创建集合加入
3. 导出一份RIS
4. 在浏览器打开交付提供的生成API文档；若为JSON/YAML文件则由CUA打开或下载，独立只读查看器审计规定API类别
5. 在浏览器访问health入口
6. 独立核查刚才实际响应与文档结构

**预期结果**

真实工作流使用可用后端；生成文档覆盖规定API，健康检查可用且不泄密，响应组织一致。

**客观通过判据（全部满足）**

- 用户保存/集合/引用操作成功
- API文档确为可用生成文档（HTML、JSON、YAML或可下载规范均可），包含全部规定服务类别
- health有可理解成功状态且无秘密
- 实际响应与文档结构一致，错误/列表结构无无故混乱
- 不把静态功能截图代替后端证据

**独立验证证据**

CUA页面/下载证据、文档内容快照及脱敏实际API响应；具体endpoint路径由交付文档取得，不预设实现路径。

### 移动与无障碍研究流程

#### T100 — 在手机尺寸下用键盘完成高级研究、认证回跳、整理和导出。

难度：Expert；类别：移动与无障碍研究流程；需求：R006, R015, R027, R028, R030, R034, R036, R037, R054

**前置条件**

- 遵守requirements.json中的G0、AUTH、LIVE、VERIFY全局前置；各例独立重置。
- VIEWPORT手机390×844；匿名起始；已存在eva_a；真实查询至少两篇；可下载文件并做语义/焦点独立审计。

**测试数据**

```json
{
  "query": "(diabetes[Title] OR insulin[Title]) AND therapy[All Fields]",
  "filter": "Review",
  "collection": "EVA Mobile Accessible",
  "format": "RIS"
}
```

**原生CUA工作流**

1. 通过手机导航进入Advanced Search
2. 仅用键盘构建或输入固定分组查询并执行
3. 通过可访问控件应用Review
4. 打开一篇详情并触发保存认证
5. 键盘填写eva_a凭证，核对返回原研究页及状态
6. 保存该文献并创建集合加入
7. 打开集合选择RIS完整导出
8. 回到研究页确认可继续操作

**预期结果**

移动布局、键盘导航、分组检索、回跳和个人研究整条链路可完成。

**客观通过判据（全部满足）**

- 核心步骤无需精确鼠标点击才能操作
- 焦点可见且表单/分页/对话框标签语义可理解
- 登录回跳保留query/filter及目标文献上下文
- 书签和集合归eva_a且元数据真实
- RIS含准确一篇
- 手机布局无阻挡主要任务的裁切/遮盖

**独立验证证据**

完整CUA键盘日志/手机截图、独立DOM语义、URL、只读研究数据与RIS文件；不以桌面代跑手机例。

