# 中文翻译标准（TRANSLATION STANDARDS）

本文件定义《Programming Massively Parallel Processors》（Hwu, Kirk, El Hajj，第 4 版，以下简称 PMPP）中译工作的统一规范。所有 `web/` 目录下的 HTML 正文翻译均应遵守本标准。

---

## 1. 目标与范围

- **目标**：产出准确、流畅、术语统一的中文译本，便于中文读者无障碍学习 CUDA / GPU 并行编程。
- **范围**：翻译 `web/chapters/` 下所有章节正文（前言、致谢、各章、附录图、索引等），以及 `web/index.html` 落地页中的说明性文字。
- **不翻译**：
  - 代码、标识符、API 名称、命令行（`web/` 中 `<pre>` 块及其内部文本）；
  - 数学公式本体（MathML `<math>…</math>`）；
  - 图片文件名、链接 `href`、锚点 `id`、`class` 等 HTML 属性；
  - 顶层导航栏（`topnav`）中用于页面跳转的 `optgroup`/`option` 标签当前保留英文（见 §4.6 例外）。

---

## 2. 总体原则

1. **信达雅、以信为先**：先求准确，再求通顺。技术含义优先于字面直译；宁可稍显生硬也不能歪曲原意。
2. **术语统一**：必须使用 §5 术语表。同一英文术语全文须对应唯一中文词，不得混用（如不能同时出现"线程束"和" warp 束"指同一概念）。
3. **不增不减**：不省略、不合并、不增补原文信息。原文的限定词（如 *typically, often, may, must*）须如实译出。
4. **保留结构**：章节编号（`1.1`、`2.3`）、图号（`Figure 2.1`）、表号（`Table 3.2`）、公式编号、习题编号保持不变，仅翻译其后的文字。
5. **主语与视角**：保留原文的人称与视角（多为无主语句或 *we* 泛指），不擅自改为中文常见的"我们"——除非原文明确使用 *we*，此时可译为"我们"。

---

## 3. HTML 文件处理规则

- **只改可见文本节点**，绝不改动标签、属性、实体（`&amp;` `&lt;` 等）与空元素。
- **保留所有 `id`/`href`/`src`**：它们是章节交叉引用与导航锚点，改动会破坏链接。
- **`<pre>` 代码块**：块内代码原样保留。代码注释可译（见 §6.3），但不得改动任何符号、字符串、缩进。
- **`<math>` 公式**：MathML 节点整体原样保留；公式前后的说明文字译为中文。
- **`<figure>` / `<figcaption>`**：`Figure X.Y` 译为"图 X.Y"，其后说明文字译为中文；`<img>` 标签及 `src` 不动。
- **`<table>`**：表标题（`caption`）译为中文；表头与单元格中的术语按 §5 翻译，数值/符号保留。
- **`<em>` / `<strong>`**：保留标签，仅译其内部文本。
- **不得引入新标签或改变层级**，以免破坏 CSS 排版。

---

## 4. 各内容元素处理细则

### 4.1 章节标题（h1 / h2 / h3）
保留编号，翻译标题。例：
`1.1 Heterogeneous parallel computing` → `1.1 异构并行计算`
`7. Convolution: An introduction to constant memory and caching`
→ `7. 卷积：常量内存与缓存简介`

### 4.2 Abstract（摘要）
`Abstract` 译为"摘要"。正文逐句翻译，保持客观陈述语气。

### 4.3 Keywords（关键词）
`Keywords` 译为"关键词"。分号分隔的词条逐项翻译，保留分号分隔与末尾句号。词条须与 §5 术语表一致。
例：`Parallel computing; heterogeneous computing; GPU computing`
→ `并行计算；异构计算；GPU 计算`

### 4.4 Chapter Outline（章节大纲）
`Chapter Outline` 译为"本章大纲"。其中的子节标题照 §4.1 翻译，右侧页码数字保留。

### 4.5 正文段落（p / li / section）
逐段翻译。注意：
- 长难句可拆分为中文短句，但不得改变逻辑关系；
- 被动语态按中文习惯转主动（如 *It is assumed that…* → "我们假设……"）；
- 指代（*this, these, it*）按中文习惯显化或省略，以通顺为准。

### 4.6 导航栏与目录（例外）
`web/index.html` 与各章 `<header class="topnav">` 中的 `<select>` 下拉项当前**保留英文**，以保证与既有锚点、文件名一致、避免破坏跳转。待全书译毕后，可统一将 `optgroup` 文案（如 `Chapter 1. Introduction`）及 `option` 显示文本中译，但 `value` 属性中的文件名不可改。

### 4.7 Exercises（习题）
`Exercises` 译为"习题"。题干、提示译为中文；其中的代码片段、变量名、输出示例保留原文格式。

### 4.8 References（参考文献）
`References` 译为"参考文献"。文献条目中的**作者姓名、文章/书名、期刊/会议名、出版信息保留原文**（专有名词不译）；条目前后若含解释性文字可译为中文。若需提供中文译名，以括号附于原文之后，不得替换原文。

---

## 5. 术语对照表（核心）

> 原则：与 NVIDIA 官方 CUDA 中文文档保持一致；首现时可在括号内保留英文原词（如"线程束（warp）"），后续直接使用中文。

### 5.1 硬件与体系结构
| 英文 | 中文 |
|---|---|
| GPU | GPU（保留不译） |
| CPU | CPU（保留不译） |
| heterogeneous computing | 异构计算 |
| throughput-oriented (design) | 面向吞吐量（的设计） |
| latency-oriented (design) | 面向延迟（的设计） |
| many-thread GPU | 多线程 GPU |
| streaming multiprocessor (SM) | 流式多处理器（SM） |
| core / CUDA core | 核心 / CUDA 核心 |
| warp | 线程束 |
| SIMD | SIMD（保留不译） |
| SIMT | SIMT（保留不译） |

### 5.2 CUDA 编程模型
| 英文 | 中文 |
|---|---|
| kernel (function) | 核函数 |
| host | 主机 |
| device | 设备 |
| thread | 线程 |
| block | 线程块 |
| grid | 网格 |
| threadIdx / blockIdx / blockDim / gridDim | 保留英文（API 名） |
| kernel launch | 核函数启动 |
| execution configuration `<<<…>>>` | 执行配置 `<<<…>>>` |

### 5.3 内存体系
| 英文 | 中文 |
|---|---|
| global memory | 全局内存 |
| shared memory | 共享内存 |
| constant memory | 常量内存 |
| local memory | 局部内存 |
| register (file) | 寄存器（文件） |
| texture memory | 纹理内存 |
| memory bandwidth | 内存带宽 |
| memory coalescing | 内存合并（访问） |
| coalesced access | 合并访问 |
| uncoalesced | 非合并 |

### 5.4 性能与优化
| 英文 | 中文 |
|---|---|
| occupancy | 占用率 |
| tiling | 分块 / 平铺 |
| thread coarsening | 线程粗化 |
| control divergence | 控制发散 |
| warp divergence | 线程束分化 |
| latency hiding / tolerance | 延迟隐藏 / 延迟容忍 |
| synchronization | 同步 |
| barrier | 屏障 |
| bank conflict | 存储体冲突 |
| speedup | 加速比 |
| Amdahl's law | 阿姆达尔定律 |
| Gustafson's law | 古斯塔夫森定律 |
| scalability | 可扩展性 |
| work efficiency | 工作效率 |

### 5.5 通用技术词
| 英文 | 中文 |
|---|---|
| parallel programming | 并行编程 |
| parallel algorithm | 并行算法 |
| parallel pattern | 并行模式 |
| data parallelism | 数据并行 |
| task parallelism | 任务并行 |
| embarrassingly parallel | 易并行（的） |
| floating-point operation (FLOP) | 浮点运算（FLOP） |
| GFLOPS / TFLOPS | 保留不译 |
| deep learning | 深度学习 |
| matrix multiplication | 矩阵乘法 |
| convolution | 卷积 |

> 未在表中出现的术语，按"含义准确、业内通用"原则确定首译，并在译稿中保持前后一致；建议汇总到本表以便复用。

---

## 6. 标点符号、数字与排版

### 6.1 标点
- 中文句子使用全角标点：，。、；：？！""（）《》。
- 中文与英文/数字相邻时，中文标点置于外侧（如"如图 2.1 所示。"）。
- 并列英文术语或列表项之间可用中文顿号或逗号；原文的分号列举统一改为中文分号。
- 引号：中文用" "，内部的英文代码/标识符可用半角 `'` 或保留原样。

### 6.2 数字与单位
- 阿拉伯数字、百分号、单位（`GB/s`、`ms`、`%`、`10⁹`）保留半角原样。
- 数字与中文之间通常不加空格（如"约 100 万个线程"可写作"约100万个线程"，全书统一即可）；建议数字与单位间留半角空格（"100 GB/s"）。
- 范围用"~"或"至"，全书统一（推荐"至"，如"第 1 至 19 页"）。

### 6.3 代码与标识符
- 代码块（`<pre>`）、内联代码片段、函数名、变量名、类型名、API（如 `cudaMalloc`、`__global__`、`float*`）一律保留英文半角。
- 代码中的注释可译为中文，但须准确且不改变行为；字符串字面量一般不译。
- 正文提到代码符号时用半角（如"调用 `vecAdd` 核函数"）。

### 6.4 公式
- MathML 公式节点原样保留；公式中的变量符号（`<mi>`）不译。
- 公式的编号与前后说明译为中文。

---

## 7. 风格指南

- **语气**：教科书风格，平实、准确、指导性强。避免过度口语化或文学化。
- **句式**：多用短句；条件、因果、对比关系要清晰。可适当使用"其""该""此"回指前文。
- **专有名词**：首次出现可中英并列（如"线程束（warp）"），后文直接用中文。
- **一致性**：同一概念、同一短语的译法全文统一；发现不一致应及时回填修订。
- **不确定处**：翻译存疑的术语或长句，可在译稿中以 `（TODO: 待确认）` 标注，便于集中复核，但不得留空。

---

## 8. 质量检查清单

完成一章翻译后，逐项确认：

- [ ] 所有可见正文均已翻译，无遗漏段落、列表项、图表说明。
- [ ] 章节号、图号、表号、公式号、习题号保留原样。
- [ ] 术语符合 §5，且全文一致。
- [ ] 所有 `<pre>` 代码块、`<math>` 公式、HTML 属性未被改动。
- [ ] 交叉引用（`href="#…"`）与锚点（`id="…"`）完整保留，链接可用。
- [ ] 中文标点使用规范，数字/单位/代码格式符合 §6。
- [ ] 无机器翻译常见的生硬措辞（如"作为结果的""被给予"等）。
- [ ] 在浏览器中打开页面，确认排版、图片、导航未损坏。

---

## 9. 工作流程建议

1. **逐章翻译**：按 `Ch001` → `Ch023` 顺序，或按 Part 分组推进。
2. **先结构后润色**：第一遍保证准确与术语统一，第二遍通读润色流畅度。
3. **术语集中管理**：翻译中发现 §5 未覆盖的术语，及时补入 §5，保证后续一致。
4. **对照复核**：译后对照英文原文逐段核对，重点关注被动语态、限定词、长难句。
5. **构建验证**：翻译后重新运行 `build_site.py`（或直接在浏览器打开 `web/index.html`）确认无破坏。

---

*本标准随翻译实践持续修订。新增术语或规则请同步更新对应章节。*
