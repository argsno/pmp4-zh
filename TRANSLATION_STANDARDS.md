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

1. **信达雅、以信为先**：先求准确，再求通顺。技术含义优先于字面直译，不要逐词硬译；宁可稍显生硬也不能歪曲原意。
2. **术语统一**：必须使用 §5 术语表。同一英文术语全文须对应唯一中文词，不得混用（如不能同时出现"线程束"和" warp 束"指同一概念）。
3. **不增不减**：不省略、不合并、不增补原文信息。原文的限定词（如 *typically, often, may, must*）须如实译出。除原文外**不添加任何内容**——不加背景介绍、概念解释、示例、总结或个人理解。
4. **保留结构**：章节编号（`1.1`、`2.3`）、图号（`Figure 2.1`）、表号（`Table 3.2`）、公式编号、习题编号保持不变，仅翻译其后的文字。段落组织、逻辑顺序、因果关系亦保持原样，不为迁就中文习惯而重排。
5. **主语与视角**：保留原文的人称与视角（多为无主语句或 *we* 泛指），不擅自改为中文常见的"我们"——除非原文明确使用 *we*，此时可译为"我们"。
6. **多义词按技术语境取义**：同一英文词在普通语境与技术语境中含义不同，一律按本领域的技术含义翻译，不得照搬普通词典释义。如 `issue` 在 CPU 语境下指"发射"（指令发射，instruction issue），不译"问题"；`kernel` 在 CUDA 语境下译"核函数"，在操作系统语境下才译"内核"。拿不准时查 §5 术语表或按 §7 标注 `（TODO: 待确认）`。

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

### 4.6 导航栏与目录
`web/index.html` 与各章 `<header class="topnav">` 中的 `<select>` 下拉项，其 `optgroup` 文案与 `option` 显示文本已按 `translations/nav.json` 中译（如 `Chapter 1. Introduction` → `第 1 章 引言`）。`value` 属性保存的是锚点与文件名，是导航真正生效的部分，**一律不可改动**；渲染器在本地化顶栏时只替换显示文本、原样保留 `value`，从而保证跳转与英文站一致。

### 4.7 Exercises（习题）
`Exercises` 译为"习题"。题干、提示译为中文；其中的代码片段、变量名、输出示例保留原文格式。

### 4.8 References（参考文献）
`References` 译为"参考文献"。文献条目中的**作者姓名、文章/书名、期刊/会议名、出版信息保留原文**（专有名词不译）；条目前后若含解释性文字可译为中文。若需提供中文译名，以括号附于原文之后，不得替换原文。

---

## 5. 术语对照表（核心）

> 原则：与 NVIDIA 官方 CUDA 中文文档保持一致；首现时按 §7 在括号内保留英文原词（如"线程束（warp）"），后续直接使用中文。对已按表格约定"保留不译"的词（如 API 名、GPU/CUDA 等），不适用本条。

### 5.0 本表的状态与读法

**状态：已冻结（frozen）；收尾合并已应用。**

本表在全书翻译开工前一次性扩充完成，并于收尾时（任务 08）把各页 `translations/<page-stem>/newterms.json` 中的表外新词统一合并回本表。翻译任务对本表**只读**：

- 翻译任务**不得**编辑本文件。多个翻译任务并发运行时，同时写同一个共享文件必然互相覆盖。
- 遇到表外新词，写入本页自己的 `translations/<page-stem>/newterms.json`，格式为 `{"en": …, "zh": …, "note": …}`，由后续收尾任务统一合并回本表。
- 命中本表的英文词，其中文译法必须与本表一致；此项由渲染器机械校验，不一致的页面不予生成。

**表格约定**（渲染器的术语校验依赖这些约定，改动表格时须遵守）：

术语表由 §5.1–§5.10 中表头恰为 `| 英文 | 中文 |` 的 Markdown 表格构成。解析器以该表头识别术语表，本节这张说明表（表头 `| 写法 | 含义 |`）因此不会被误读为词条。

| 写法 | 含义 |
|---|---|
| 英文列出现 ` / ` | 分隔多个英文写法，它们**共用**该行中文列的处理方式。两种情形：同义词（`pinned memory / page-locked memory`），以及共享同一处理方式的名字列表（`cudaMalloc / cudaFree / cudaMemcpy`） |
| 中文列 | **恰好一个**译法。§2.2 要求同一英文术语全文对应唯一中文词，故中文列不出现 ` / ` |
| `保留不译` / `保留英文（…）` | 该词在译文中保持英文原样；圆括号内说明理由（多为 API 名、标识符、架构代号） |
| 中文列圆括号内的补充 | 可选成分，出现与否均合规（如"面向吞吐量（的设计）"） |
| 英文列圆括号内的缩写 | 缩写与全称同权，均按该行中文译法处理 |

两条容易踩的坑：

- 英文列的 ` / ` **不表示位置配对**。若两个英文词各有各的译法（如 input tile 与 output tile），必须拆成两行；挤在一行会让校验器无法判断哪个词对应哪个译法。
- 一个英文术语只能有一个中文译法，哪怕两种译法都通行。例如 scan 与 prefix sum 在本书中是同一个概念，一律译作"扫描"——正是为了避免读者把"扫描"和"前缀和"当成两回事。首现时按 §5 开头的原则写成"扫描（prefix sum）"即可兼顾。

### 5.1 硬件与体系结构
| 英文 | 中文 |
|---|---|
| GPU | GPU（保留不译） |
| CPU | CPU（保留不译） |
| graphics processing unit | 图形处理器 |
| GPGPU | GPGPU（保留不译） |
| heterogeneous computing | 异构计算 |
| heterogeneous parallel computing | 异构并行计算 |
| throughput-oriented (design) | 面向吞吐量（的设计） |
| latency-oriented (design) | 面向延迟（的设计） |
| many-thread GPU | 多线程 GPU |
| many-thread trajectory | 多线程路线 |
| multicore trajectory | 多核路线 |
| streaming multiprocessor (SM) | 流式多处理器（SM） |
| streaming processor | 流处理器 |
| core | 核心 |
| CUDA core | CUDA 核心 |
| tensor core | 张量核心 |
| warp | 线程束 |
| SIMD / single-instruction, multiple-data | SIMD（保留不译） |
| SIMT | SIMT（保留不译） |
| SPMD / single-program multiple-data | 单程序多数据（SPMD） |
| von Neumann model | 冯·诺依曼模型 |
| arithmetic and logic unit (ALU) | 算术逻辑单元（ALU） |
| instruction fetch/dispatch unit | 取指/分发单元 |
| program counter | 程序计数器 |
| compute capability | 计算能力 |
| accelerator | 加速器 |
| PCIe bus | PCIe 总线 |
| direct memory access (DMA) | 直接内存访问（DMA） |
| hardware queue | 硬件队列 |
| Fermi / Kepler / Pascal | 保留英文（GPU 架构代号） |
| A100 | A100（保留英文，GPU 架构代号） |
| Ampere A100 | 保留英文 |
| coprocessor | 协处理器 |
| execution unit | 执行单元 |
| field-programmable gate arrays | 现场可编程门阵列 |
| G80 | G80（保留英文，GPU 架构代号） |
| HBM2 | 保留英文 |
| hyperthreading | 超线程 |
| mainframe | 大型主机 |
| microprocessor | 微处理器 |
| minicomputer | 小型计算机 |
| NVIDIA / Intel / AMD / ARM / Apple / ATI / GE / Siemens | 保留英文（公司名） |
| NVIDIA Tesla A100 / G80 | 保留英文（产品名或芯片代号） |
| out-of-order | 乱序 |
| processing block | 处理块 |
| supercomputer | 超级计算机 |
| VLIW | VLIW（超长指令字） |
| Volta | 保留英文 |
| Volta / Turing / Ampere | 保留英文（GPU 架构代号） |
| von Neumann | 冯·诺依曼 |

### 5.2 CUDA 编程模型
| 英文 | 中文 |
|---|---|
| CUDA / Compute Unified Device Architecture | CUDA（保留不译） |
| CUDA C | CUDA C（保留不译） |
| kernel (function) | 核函数 |
| host | 主机 |
| device | 设备 |
| host code | 主机代码 |
| device code | 设备代码 |
| thread | 线程 |
| block / thread block | 线程块 |
| grid | 网格 |
| threadIdx / blockIdx / blockDim / gridDim | 保留英文（内置变量名） |
| built-in variable | 内置变量 |
| kernel launch | 核函数启动 |
| grid launch | 网格启动 |
| execution configuration `<<<…>>>` | 执行配置 `<<<…>>>` |
| `__global__` / `__device__` / `__host__` | 保留英文（函数声明关键字） |
| `__shared__` / `__constant__` | 保留英文（变量声明关键字） |
| NVCC / NVIDIA C compiler | NVCC（NVIDIA C 编译器） |
| runtime API | 运行时 API |
| application programming interface (API) | 应用程序编程接口（API） |
| intrinsic function | 内建函数 |
| stub function | 桩函数 |
| linearized index | 线性化索引 |
| block scheduling | 线程块调度 |
| thread scheduling | 线程调度 |
| warp scheduling | 线程束调度 |
| zero-overhead scheduling | 零开销调度 |
| transparent scalability | 透明可扩展性 |
| barrier synchronization | 屏障同步 |
| `__syncthreads()` | 保留英文（API 名） |
| adjacent synchronization | 相邻同步 |
| race condition | 竞态条件 |
| deadlock | 死锁 |
| read-modify-write | 读-改-写 |
| CUDA stream | CUDA 流 |
| dynamic parallelism | 动态并行 |
| parent grid | 父网格 |
| child grid | 子网格 |
| nesting depth | 嵌套深度 |
| cooperative kernel | 协作核函数 |
| active thread | 活跃线程 |
| C++AMP | 保留英文（编程接口名） |
| call frame stack | 调用帧栈 |
| call stack | 调用栈 |
| ceiling division | 向上取整除法 |
| child kernel | 子核函数 |
| color-to-grayscale conversion | 彩色到灰度转换 |
| context switch | 上下文切换 |
| context switching | 上下文切换 |
| convergent kernel | 收敛核函数 |
| cooperating kernels | 协作核函数 |
| Cooperative Groups API | 保留英文 |
| CUDA FORTRAN | 保留英文（编程接口名） |
| data index | 数据索引 |
| device property query | 设备属性查询 |
| execution configuration parameter | 执行配置参数 |
| fixed-size pool | 固定大小池 |
| global index | 全局索引 |
| grayscale image | 灰度图像 |
| grid-wide synchronization | 网格级同步 |
| hierarchical organization | 层次化组织 |
| inactive thread | 非活跃线程 |
| independent thread scheduling | 独立线程调度 |
| internal block | 内部线程块 |
| kernel invocation | 核函数调用 |
| kernel queues | 核函数队列 |
| lambda | lambda 表达式 |
| loop parallelism | 循环级并行 |
| luminance | 亮度 |
| memory fence | 内存栅栏 |
| memory fencing | 内存栅栏 |
| metaprogramming | 元编程 |
| multikernel execution | 多核函数执行 |
| named stream | 命名流 |
| nested parallelism | 嵌套并行 |
| nesting level | 嵌套层级 |
| OpenGL / Direct3D | 保留英文（图形 API 名） |
| parent kernel | 父核函数 |
| pending launch pool | 待启动池 |
| resident warp | 驻留线程束 |
| source-level debugger | 源代码级调试器 |
| synchronization depth | 同步深度 |
| task decomposition | 任务分解 |
| thread grid | 线程网格 |
| virtual function | 虚函数 |
| virtualized pool | 虚拟化池 |
| Visual Profiler | 保留英文（NVIDIA 工具名） |
| weighted sum | 加权和 |

### 5.3 内存体系
| 英文 | 中文 |
|---|---|
| global memory | 全局内存 |
| device global memory | 设备全局内存 |
| shared memory | 共享内存 |
| constant memory | 常量内存 |
| local memory | 局部内存 |
| host memory | 主机内存 |
| device memory | 设备内存 |
| memory access | 内存访问 |
| register (file) | 寄存器（文件） |
| texture memory | 纹理内存 |
| scratchpad (memory) | 便笺存储器 |
| on-chip memory | 片上内存 |
| off-chip memory | 片外内存 |
| cache | 缓存 |
| L1 cache | L1 缓存 |
| L2 cache | L2 缓存 |
| constant cache | 常量缓存 |
| last-level cache | 末级缓存 |
| cache coherence | 缓存一致性 |
| DRAM / dynamic random-access memory | 动态随机存取存储器（DRAM） |
| DRAM burst | DRAM 突发传输 |
| DRAM channel | DRAM 通道 |
| bank | 存储体 |
| bank conflict | 存储体冲突 |
| high-bandwidth memory (HBM) | 高带宽内存（HBM） |
| memory bandwidth | 内存带宽 |
| memory coalescing | 内存合并（访问） |
| coalesced access | 合并访问 |
| uncoalesced | 非合并 |
| corner turning | 拐角变换 |
| memory divergence | 内存发散 |
| memory traffic | 内存流量 |
| memory bound | 访存受限（的） |
| data transfer | 数据传输 |
| pinned memory / page-locked memory | 锁页内存 |
| zero-copy memory | 零拷贝内存 |
| unified memory | 统一内存 |
| unified virtual address space (UVAS) | 统一虚拟地址空间（UVAS） |
| cudaMalloc / cudaFree / cudaMemcpy | 保留英文（API 名） |
| row-major layout | 行主序布局 |
| column-major layout | 列主序布局 |
| array of structures | 结构体数组 |
| automatic (array) variable | 自动（数组）变量 |
| data locality | 数据局部性 |
| address space | 地址空间 |
| bit line | 位线 |
| cache line | 缓存行 |
| coherence | 一致性 |
| column-major order | 列主序 |
| core array | 核心阵列 |
| data caching | 数据缓存 |
| data migration | 数据迁移 |
| decoder (DRAM) | 译码器 |
| double data rate (DDR) | 双倍数据速率（DDR） |
| DRAM cell | DRAM 存储单元 |
| global memory request | 全局内存请求 |
| interleaved data distribution | 交错数据分布 |
| linear layout | 线性布局 |
| managed memory | 托管内存 |
| memory access efficiency | 内存访问效率 |
| memory alignment | 内存对齐 |
| memory controller | 内存控制器 |
| memory copy | 内存拷贝 |
| noncoalesced memory access | 非合并内存访问 |
| page fault | 页错误 |
| paging | 换页 |
| physical address space | 物理地址空间 |
| private memory | 私有内存 |
| read-only data cache | 只读数据缓存 |
| row-major order | 行主序 |
| sense amplifier / sensing amplifier | 读出放大器 |
| system interconnect | 系统互连 |
| system memory | 系统内存 |
| Unified Virtual Addressing | 统一虚拟寻址 |
| unified virtual memory | 统一虚拟内存 |
| universal copy | 公共副本 |
| virtual address | 虚拟地址 |
| virtual address space | 虚拟地址空间 |
| virtual memory | 虚拟内存 |
| working set | 工作集 |
| zero-copy system memory access | 零拷贝系统内存访问 |

### 5.4 性能与优化
| 英文 | 中文 |
|---|---|
| occupancy | 占用率 |
| tiling / tile | 分块 |
| input tile | 输入分块 |
| output tile | 输出分块 |
| halo cell | 光环单元 |
| ghost cell | 幽灵单元 |
| register tiling | 寄存器分块 |
| thread coarsening | 线程粗化 |
| coarsening factor | 粗化因子 |
| thread granularity | 线程粒度 |
| control divergence | 控制发散 |
| latency hiding | 延迟隐藏 |
| latency tolerance | 延迟容忍 |
| long-latency operation | 长延迟操作 |
| synchronization | 同步 |
| barrier | 屏障 |
| speedup | 加速比 |
| Amdahl's law | 阿姆达尔定律 |
| Gustafson's law | 古斯塔夫森定律 |
| scalability | 可扩展性 |
| work efficiency | 工作效率 |
| arithmetic intensity / computational intensity | 算术强度 |
| compute to global memory access ratio | 计算访存比 |
| roofline model | Roofline 模型 |
| performance cliff | 性能悬崖 |
| resource partitioning | 资源划分 |
| dynamic resource partitioning | 动态资源划分 |
| privatization | 私有化 |
| contention | 竞争 |
| aggregation | 聚合 |
| atomic operation | 原子操作 |
| atomicAdd / atomicCAS | 保留英文（API 名） |
| compare-and-swap | 比较并交换 |
| output interference | 输出干扰 |
| load balance | 负载均衡 |
| double buffering | 双缓冲 |
| strip mining | 条带挖掘 |
| loop fission / loop splitting | 循环分裂 |
| loop interchange | 循环交换 |
| profiler | 性能分析器 |
| critical path analysis | 关键路径分析 |
| false dependence | 伪依赖 |
| read-after-write dependence | 写后读依赖 |
| write-after-read dependence | 读后写依赖 |
| arithmetic-to-global memory access ratio | 算术运算与全局内存访问之比 |
| atomic add | 原子加 |
| coarsening loop | 粗化循环 |
| compute-bound | 计算受限（的） |
| control flow divergence | 控制流发散 |
| cross-iteration dependence | 跨迭代依赖 |
| CUDA Occupancy Calculator | 保留英文 |
| data reuse | 数据重用 |
| execution resource | 执行资源 |
| execution resource utilization efficiency | 执行资源利用率 |
| full occupancy | 满占用率 |
| hardware underutilization | 硬件未被充分利用 |
| heuristic tuning | 启发式调优 |
| interference between threads | 线程间干扰 |
| load imbalance | 负载不均衡 |
| loop unrolling | 循环展开 |
| memory latency | 内存延迟 |
| operational intensity | 运算强度 |
| operations per byte | 每字节操作数 |
| oversubscription | 过度订阅 |
| PC sampling | PC 采样 |
| predication | 断言执行 |
| private copy | 私有副本 |
| public copy | 公有副本 |
| redundant work | 冗余工作 |
| register spilling | 寄存器溢出 |
| resource allocation | 资源分配 |
| reuse ratio | 重用率 |
| SIMD efficiency | SIMD 效率 |
| spilled register | 溢出的寄存器 |
| strong scaling | 强扩展 |
| thread block slot | 线程块槽位 |
| thread slot | 线程槽位 |
| tiling efficiency | 分块效率 |
| true dependence | 真依赖 |
| weak scaling | 弱扩展 |

### 5.5 并行模式（parallel patterns）
| 英文 | 中文 |
|---|---|
| parallel pattern | 并行模式 |
| data parallelism | 数据并行 |
| task parallelism | 任务并行 |
| embarrassingly parallel | 易并行（的） |
| problem decomposition | 问题分解 |
| input-centric decomposition | 面向输入的分解 |
| output-centric decomposition | 面向输出的分解 |
| computational thinking | 计算思维 |
| scatter | 分散 |
| gather | 汇聚 |
| owner computes | 属主计算 |
| convolution | 卷积 |
| convolution filter | 卷积滤波器 |
| filter radius | 滤波器半径 |
| boundary condition | 边界条件 |
| image blur | 图像模糊 |
| stencil | 模板 |
| stencil sweep | 模板扫掠 |
| grid point | 网格点 |
| discretization | 离散化 |
| finite-difference method | 有限差分法 |
| finite-element method | 有限元法 |
| partial differential equation | 偏微分方程 |
| structured grid | 结构化网格 |
| unstructured grid | 非结构化网格 |
| histogram | 直方图 |
| binning | 分箱 |
| interleaved partitioning | 交错划分 |
| contiguous partitioning | 连续划分 |
| reduction | 归约 |
| reduction tree | 归约树 |
| segmented reduction | 分段归约 |
| identity value | 单位元 |
| associative operator | 结合性算子 |
| commutative operator | 交换性算子 |
| scan / prefix sum | 扫描 |
| inclusive scan | 包含式扫描 |
| exclusive scan | 排他式扫描 |
| segmented scan | 分段扫描 |
| single-pass scan | 单遍扫描 |
| Kogge-Stone algorithm | Kogge-Stone 算法 |
| Brent-Kung algorithm | Brent-Kung 算法 |
| merge | 归并 |
| co-rank (function) | 协秩（函数） |
| circular buffer | 环形缓冲区 |
| sorting | 排序 |
| radix sort | 基数排序 |
| merge sort | 归并排序 |
| sorting network | 排序网络 |
| bitonic sort | 双调排序 |
| sample sort | 样本排序 |
| stable sort | 稳定排序 |
| unstable sort | 不稳定排序 |
| comparison-based sorting | 基于比较的排序 |
| least significant bit (LSB) | 最低有效位（LSB） |
| radix value | 基数值 |
| divide-and-conquer | 分治 |
| compaction | 紧凑化 |
| regularization | 规整化 |
| 13-point stencil | 13 点模板 |
| 19-point stencil | 19 点模板 |
| 1D convolution | 1D 卷积 |
| 25-point stencil | 25 点模板 |
| alphabet position | 字母表位置 |
| atom-centric | 面向原子的 |
| atom-centric decomposition | 面向原子的分解 |
| block-level local sort | 块级局部排序 |
| block-wide scan | 块内扫描 |
| bottom-up sort methods | 自底向上排序方法 |
| boundary check | 边界检查 |
| bubble sort | 冒泡排序 |
| bucket | 桶 |
| bucketing | 分桶 |
| carry look-ahead | 先行进位 |
| commit | 提交 |
| comparison sort | 比较排序 |
| contiguous segment | 连续段 |
| convolution kernel | 卷积核 |
| counting sort | 计数排序 |
| cumulative sum | 累加和 |
| data-scalable algorithm | 数据可扩展算法 |
| destination index | 目标索引 |
| domain decomposition | 区域分解 |
| domino-style scan algorithm | 多米诺式扫描算法 |
| dynamic block index assignment | 动态线程块索引分配 |
| filter | 滤波器 |
| finite-volume method | 有限体积法 |
| five-point stencil | 五点模板 |
| grid-centric decomposition | 面向网格的分解 |
| halo overhead | 光环开销 |
| hierarchical reduction | 分层归约 |
| higher-order stencil | 高阶模板 |
| in-place | 原地 |
| input list | 输入列表 |
| input range | 输入范围 |
| input tile plane | 输入分块平面 |
| input tiling | 输入分块 |
| interleaved data partitioning | 交错数据划分 |
| key | 键 |
| key field | 键字段 |
| leader thread | 领头线程 |
| least significant digit (LSD) | 最低有效位（LSD） |
| lexicographical order | 字典序 |
| linear recursion | 线性递归 |
| local bucket | 局部桶 |
| local sort | 局部排序 |
| map-reduce | MapReduce |
| marker variable | 标记变量 |
| max reduction | 最大值归约 |
| merge tree | 归并树 |
| most significant bit | 最高有效位 |
| most significant digit (MSD) | 最高有效位（MSD） |
| multiblock | 多块 |
| nine-point stencil | 九点模板 |
| noncomparison sort | 非比较排序 |
| nondecreasing order | 非递减顺序 |
| nonincreasing order | 非递增顺序 |
| odd-even transposition sort | 奇偶转置排序 |
| output list | 输出列表 |
| output pixel | 输出像素 |
| output plane | 输出平面 |
| output range | 输出范围 |
| owner position / owner location | 属主位置 |
| partial reduction result | 部分归约结果 |
| partial sum | 部分和 |
| predecessor | 前驱 |
| prefix subarray | 前缀子数组 |
| primary key | 主键 |
| producer-consumer chain | 生产者-消费者链 |
| quicksort | 快速排序 |
| regular grid | 规则网格 |
| reverse tree | 反向树 |
| sampling sort | 样本排序 |
| scan block | 扫描块 |
| scan section | 扫描段 |
| secondary key | 次键 |
| sectional scan | 分段扫描 |
| segmented multiblock reduction | 分段多块归约 |
| seven-point stencil | 七点模板 |
| shuffle instruction | shuffle 指令 |
| stencil order | 模板阶数 |
| stream compaction | 流式紧凑化 |
| subarray | 子数组 |
| sum reduction | 求和归约 |
| three-point stencil | 三点模板 |
| time slice | 时间切片 |
| top-down sort methods | 自顶向下排序方法 |
| transposition sort | 转置排序 |
| two-phase hybrid | 两阶段混合式 |
| value field | 值字段 |
| work assignment | 工作分配 |
| work-efficient | 工作高效（的） |

### 5.6 稀疏矩阵与图计算
| 英文 | 中文 |
|---|---|
| sparse matrix | 稀疏矩阵 |
| sparse matrix storage format | 稀疏矩阵存储格式 |
| sparse matrix-vector multiplication (SpMV) | 稀疏矩阵-向量乘法（SpMV） |
| nonzero element | 非零元素 |
| coordinate list format (COO) | 坐标列表格式（COO） |
| compressed sparse row (CSR) | 压缩稀疏行格式（CSR） |
| compressed sparse column (CSC) | 压缩稀疏列格式（CSC） |
| ELL format | ELL 格式 |
| hybrid ELL-COO format | ELL-COO 混合格式 |
| jagged diagonal storage (JDS) | 锯齿对角存储格式（JDS） |
| data padding | 数据填充 |
| transposition | 转置 |
| Gaussian elimination | 高斯消元 |
| fill-in | 填充元 |
| conjugate gradient (CG) | 共轭梯度（CG） |
| graph | 图 |
| vertex | 顶点 |
| edge | 边 |
| source vertex | 源顶点 |
| destination vertex | 目标顶点 |
| adjacency matrix | 邻接矩阵 |
| breadth-first search (BFS) | 广度优先搜索（BFS） |
| graph traversal | 图遍历 |
| frontier | 前沿 |
| vertex-centric | 面向顶点的 |
| edge-centric | 面向边的 |
| push implementation | 推送式实现 |
| pull implementation | 拉取式实现 |
| top-down strategy | 自顶向下策略 |
| bottom-up strategy | 自底向上策略 |
| direction-optimized | 方向优化的 |
| idempotence | 幂等性 |
| dense matrix | 稠密矩阵 |
| dense vector | 稠密向量 |
| graph search | 图搜索 |
| hop | 跳 |
| incoming edge | 入边 |
| linear-algebraic formulation | 线性代数表述 |
| outgoing edge | 出边 |
| padding element | 填充元素 |
| small world graph | 小世界图 |
| social network | 社交网络 |
| unweighted graph | 无权图 |
| vertex degree | 顶点度数 |
| wavefront | 波前 |

### 5.7 数值与浮点
| 英文 | 中文 |
|---|---|
| floating-point operation (FLOP) | 浮点运算（FLOP） |
| GFLOPS / TFLOPS | 保留不译 |
| floating-point number system | 浮点数系统 |
| floating-point data representation | 浮点数据表示 |
| IEEE-754 standard | IEEE-754 标准 |
| sign bit | 符号位 |
| exponent (of a floating-point number) | 阶码 |
| mantissa | 尾数 |
| normalized representation | 规格化表示 |
| denormalization | 非规格化 |
| abrupt underflow | 突然下溢 |
| excess encoding | 移码编码 |
| representable number | 可表示数 |
| single-precision | 单精度 |
| double-precision | 双精度 |
| half-precision | 半精度 |
| not a number (NaN) | 非数（NaN） |
| units in the last place (ULP) | 末位单位（ULP） |
| rounding | 舍入 |
| alignment shifting | 对阶移位 |
| numerical stability | 数值稳定性 |
| Kahan summation algorithm | Kahan 求和算法 |
| linear solver | 线性方程组求解器 |
| backward substitution | 回代 |
| pivoting | 选主元 |
| system of linear equations | 线性方程组 |
| biased encoding | 移码（有偏）编码 |
| bit pattern | 位模式 |
| branch divergence | 分支发散 |
| communication-avoiding algorithm | 避免通信的算法 |
| comparator | 比较器 |
| compensated summation algorithm | 补偿求和算法 |
| denormalized number | 非规格化数 |
| dynamic range | 动态范围 |
| excess representation | 移码表示 |
| excess-3 | 移码 3 |
| floating-point arithmetic | 浮点算术 |
| identity matrix | 单位矩阵 |
| inverse matrix | 逆矩阵 |
| inversion operation | 求倒数运算 |
| iterative method | 迭代法 |
| iterative solver | 迭代求解器 |
| lead variable | 主变量 |
| no-zero | no-zero（无零） |
| normalized number | 规格化数 |
| number line | 数轴 |
| pairwise product | 两两乘积 |
| pairwise sum | 成对和 |
| partial pivoting | 部分选主元 |
| place value | 位值 |
| polynomial approximation | 多项式逼近 |
| precision | 精度 |
| presort | 预排序 |
| quiet NaN | 静默 NaN |
| reserved bit pattern | 保留位模式 |
| right-hand-side value | 右端项 |
| round to zero | 舍入到零 |
| rounding error | 舍入误差 |
| signaling NaN | 发信号 NaN |
| special function unit | 特殊函数单元 |
| special function unit (SFU) | 特殊函数单元（SFU） |
| top equation | 顶部方程 |
| transcendental function | 超越函数 |
| triangular matrix | 三角矩阵 |
| two's complement | 二进制补码 |

### 5.8 应用领域（深度学习、医学影像、分子动力学）
| 英文 | 中文 |
|---|---|
| deep learning | 深度学习 |
| machine learning | 机器学习 |
| neural network | 神经网络 |
| convolutional neural network (CNN) | 卷积神经网络（CNN） |
| perceptron | 感知机 |
| multilayer perceptron (MLP) | 多层感知机（MLP） |
| multilayer classifier | 多层分类器 |
| activation function | 激活函数 |
| convolutional layer | 卷积层 |
| subsampling layer / pooling layer | 池化层 |
| feature map | 特征图 |
| filter bank | 滤波器组 |
| inference | 推理 |
| training | 训练 |
| forward propagation | 前向传播 |
| backpropagation | 反向传播 |
| stochastic gradient descent | 随机梯度下降 |
| chain rule | 链式法则 |
| error function | 误差函数 |
| learning rate | 学习率 |
| epoch | 轮次 |
| minibatch | 小批量 |
| general matrix multiply (GEMM) | 通用矩阵乘法（GEMM） |
| cuDNN / cuBLAS / cuFFT / Thrust | 保留英文（库名） |
| magnetic resonance imaging (MRI) | 磁共振成像（MRI） |
| k-space | k 空间 |
| Cartesian scan trajectory | 笛卡儿扫描轨迹 |
| non-Cartesian scan trajectory | 非笛卡儿扫描轨迹 |
| iterative reconstruction | 迭代重建 |
| signal-to-noise ratio (SNR) | 信噪比（SNR） |
| molecular dynamics | 分子动力学 |
| electrostatic potential map | 静电势图 |
| direct Coulomb summation (DCS) | 直接库仑求和（DCS） |
| cutoff binning | 截断分箱 |
| cutoff summation | 截断求和 |
| Bezier curve | 贝塞尔曲线 |
| quadtree | 四叉树 |
| anatomical constraint | 解剖约束 |
| apodization | 变迹 |
| artificial neural network | 人工神经网络 |
| bilinear interpolation | 双线性插值 |
| control point | 控制点 |
| cost function | 代价函数 |
| CUTLASS | CUTLASS（保留英文） |
| cutoff distance | 截断距离 |
| cutoff radius | 截断半径 |
| dummy atom | 虚拟原子 |
| electrostatic potential energy | 静电势能 |
| energy grid | 能量网格 |
| energy grid point | 能量网格点 |
| fast Fourier transform (FFT) | 快速傅里叶变换（FFT） |
| feature extractor | 特征提取器 |
| feedforward network | 前馈网络 |
| field inhomogeneity | 场不均匀性 |
| Fourier transform domain | 傅里叶变换域 |
| fully connected layer | 全连接层 |
| gridding | 网格化 |
| Hermitian transpose | 厄米转置 |
| inverse fast Fourier transform (iFFT) | 逆快速傅里叶变换（iFFT） |
| linear classifier | 线性分类器 |
| neighborhood bin | 邻域箱 |
| neighborhood list | 邻域列表 |
| OCR | 光学字符识别（OCR） |
| overflow list | 溢出列表 |
| peak signal-to-noise ratio (PSNR) | 峰值信噪比（PSNR） |
| phantom object | 体模 |
| positron emission tomography (PET) | 正电子发射断层成像（PET） |
| projection imaging | 投影成像 |
| quasi-Bayesian | 准贝叶斯 |
| radial line | 径向线 |
| reference image | 参考图像 |
| rosette | 玫瑰线 |
| scan trajectory | 扫描轨迹 |
| spatial frequency domain | 空间频率域 |
| Toeplitz | Toeplitz |
| view angle transformation | 视角变换 |
| visual molecular dynamics (VMD) | 可视化分子动力学（VMD） |
| voxel | 体素 |
| weighting function | 加权函数 |

### 5.9 多 GPU 与集群
| 英文 | 中文 |
|---|---|
| high-performance computing (HPC) | 高性能计算（HPC） |
| message passing interface (MPI) | 消息传递接口（MPI） |
| MPI process | MPI 进程 |
| communicator | 通信域 |
| MPI rank | MPI 进程号 |
| point-to-point communication | 点对点通信 |
| collective communication | 集合通信 |
| MPI_Send / MPI_Recv / MPI_Barrier | 保留英文（API 名） |
| domain partitioning | 域划分 |
| compute process | 计算进程 |
| edge process | 边界进程 |
| internal process | 内部进程 |
| overlapping computation and communication | 计算与通信重叠 |
| Jacobi iterative method | 雅可比迭代法 |
| CUDA-aware MPI | CUDA 感知的 MPI |
| OpenMP / OpenCL / OpenACC | 保留英文（编程接口名） |
| bounce buffer | 弹跳缓冲区 |
| boundary slice | 边界切片 |
| cluster | 集群 |
| collective operations | 集合操作 |
| compute cluster | 计算集群 |
| compute node | 计算节点 |
| CUDA aware message passing interface | CUDA 感知的 MPI |
| data server | 数据服务器 |
| distributed memory model | 分布式内存模型 |
| halo exchange | 光环交换 |
| halo slice | 光环切片 |
| intercommunicator | 组间通信域 |
| intracommunicator | 组内通信域 |
| login node | 登录节点 |
| tag | 标记 |

### 5.10 通用技术词
| 英文 | 中文 |
|---|---|
| massively parallel | 大规模并行 |
| parallel programming | 并行编程 |
| parallel algorithm | 并行算法 |
| parallel computing | 并行计算 |
| sequential program | 串行程序 |
| parallel program | 并行程序 |
| matrix multiplication | 矩阵乘法 |
| tiled matrix multiplication | 分块矩阵乘法 |
| matrix-vector multiplication | 矩阵-向量乘法 |
| dot product | 点积 |
| vector addition | 向量加法 |
| multidimensional array | 多维数组 |
| linear algebra | 线性代数 |
| bottleneck | 瓶颈 |
| overhead | 开销 |
| throughput | 吞吐量 |
| latency | 延迟 |
| adaptive refinement | 自适应加密 |
| adaptive subdivision | 自适应细分 |
| AI | 保留英文（人工智能缩写） |
| algorithmic complexity | 算法复杂度 |
| application-level speedup | 应用级加速比 |
| Basic Linear Algebra Subprograms (BLAS) | 基本线性代数子程序（BLAS） |
| batch mode | 批量模式 |
| bin | 箱 |
| binary search | 二分查找 |
| bitwise-and operation | 按位与运算 |
| black art | 玄学 |
| bounding box | 边界框 |
| branch degree | 分支度数 |
| carpooling | 拼车 |
| clock cycle | 时钟周期 |
| coauthor | 合著者 |
| coefficient | 系数 |
| compression | 压缩 |
| computational scientist | 计算科学家 |
| computational thinker | 计算思维者 |
| computing model | 计算模式 |
| concurrency | 并发 |
| curvature | 曲率 |
| data analytics | 数据分析 |
| data element | 数据元素 |
| debugger | 调试器 |
| definiteness | 确定性 |
| differential equation | 微分方程 |
| digital twin | 数字孪生 |
| driving direction map services | 驾车路线地图服务 |
| dynamically linked library | 动态链接库 |
| effective computability | 有效可计算性 |
| eigenvalue analysis | 特征值分析 |
| exascale | 百亿亿次级 |
| exception handling | 异常处理 |
| external reviewer | 外部审稿人 |
| fabrication process | 制造工艺 |
| father of CUDA | CUDA 之父 |
| feature size | 特征尺寸 |
| finiteness | 有限性 |
| geometric series | 几何级数 |
| golden age of computing | 计算的黄金时代 |
| GPU computing | GPU 计算 |
| grid spacing | 网格间距 |
| HDTV / high-definition (HD) TV | 高清电视 |
| high-fidelity simulation | 高保真模拟 |
| implicit method | 隐式方法 |
| individualized medicine | 个体化医疗 |
| initial condition | 初始条件 |
| inner product | 内积 |
| installed base | 装机量 |
| interpolation | 插值 |
| kiosk | 自助终端 |
| lattice point | 格点 |
| lead architect | 首席架构师 |
| legacy library | 遗留库 |
| legacy program | 遗留程序 |
| lithography mask | 光刻掩模版 |
| loop nest | 循环嵌套 |
| LU decomposition | LU 分解 |
| mask | 掩码 |
| maze routing | 迷宫布线 |
| Monte Carlo methods | 蒙特卡洛方法 |
| mutex | 互斥量 |
| National Institutes of Health (NIH) | 美国国立卫生研究院（NIH） |
| net terminal | 网络端子 |
| NTSC | 保留英文（电视制式缩写，不译） |
| numerical approximation | 数值近似 |
| numerical method | 数值方法 |
| order relation | 序关系 |
| ordering relation | 序关系 |
| outlet gate | 输出门 |
| oversampling | 过采样 |
| paradigm shift | 范式转变 |
| parallelotope | 平行多面体 |
| Pareto optimal curve | 帕累托最优曲线 |
| polynomial evaluation | 多项式求值 |
| quadrant | 象限 |
| randomization | 随机化 |
| ray tracing | 光线追踪 |
| recurrence | 递推 |
| scalar variable | 标量变量 |
| self-driving cars | 自动驾驶汽车 |
| space efficiency | 空间效率 |
| spline | 样条 |
| spline curve | 样条曲线 |
| square matrix | 方阵 |
| statistical estimation method | 统计估计方法 |
| stride | 步长 |
| submatrix | 子矩阵 |
| superapplications | 超级应用 |
| supercircle | 超圆 |
| system call | 系统调用 |
| task-level parallelization | 任务级并行化 |
| Taylor series | 泰勒级数 |
| terascale | 万亿次级 |
| time step | 时间步 |
| turbulence simulation | 湍流模拟 |
| uniform grid | 均匀网格 |
| value interval | 值区间 |
| wiring block | 布线块 |
| work queue | 工作队列 |
| workload | 工作负载 |

> 未在表中出现的术语，按"含义准确、业内通用"原则确定首译，并在译稿中保持前后一致。**不要直接编辑本表**——按 §5.0 写入本页的 `newterms.json`。

---

## 6. 标点符号、数字与排版

### 6.1 标点
- 中文句子使用全角标点：，。、；：？！""（）《》。
- 中文与英文/数字相邻时，中文标点置于外侧（如"如图 2.1 所示。"）。
- 并列英文术语或列表项之间可用中文顿号或逗号；原文的分号列举统一改为中文分号。
- 引号：中文用" "，内部的英文代码/标识符可用半角 `'` 或保留原样。

### 6.2 数字与单位
- 阿拉伯数字、百分号、单位（`GB/s`、`ms`、`%`、`10⁹`）保留半角原样。
- 中文与数字/英文之间的空格由渲染器**机械强制**：在 CJK 与拉丁字符（含数字）的交界处统一插入半角空格（如"约 100 万个线程""使用 CUDA"）。译者无需自行加空格，也不得依赖"全书统一即可"之类的松散约定——并发翻译下各页无法自行保持一致，这项排版由渲染器兜底。
- 数字与单位之间建议留半角空格（"100 GB/s"），渲染器不作强制。
- 范围一律用"至"（如"第 1 至 19 页"）。

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
- **专有名词**：首次出现时中英并列，格式为"中文名称（英文名称）"（如"线程束（warp）"）；英文含缩写时可写作"中文名称（英文全称, 缩写）"（如"同时多线程（Simultaneous Multithreading, SMT）"）。后文一律直接用中文或业内常用缩写，不再重复英文。
- **一致性**：同一概念、同一短语的译法全文统一；发现不一致应及时回填修订。
- **不确定处**：翻译存疑的术语或长句，可在译稿中以 `（TODO: 待确认）` 标注，便于集中复核，但不得留空。

---

## 8. 质量检查清单

完成一章翻译后，逐项确认：

- [ ] 所有可见正文均已翻译，无遗漏段落、列表项、图表说明。
- [ ] 章节号、图号、表号、公式号、习题号保留原样。
- [ ] 术语符合 §5，且全文一致；多义词已按 §2.6 取技术义（issue→发射、kernel→核函数 等）。
- [ ] 首现术语已按 §7 格式中英并列，后文统一用中文。
- [ ] 所有 `<pre>` 代码块、`<math>` 公式、HTML 属性未被改动。
- [ ] 交叉引用（`href="#…"`）与锚点（`id="…"`）完整保留，链接可用。
- [ ] 中文标点使用规范，数字/单位/代码格式符合 §6。
- [ ] 无机器翻译常见的生硬措辞（如"作为结果的""被给予"等）。
- [ ] 无增补原文未含的内容（背景介绍、概念解释、示例、总结、个人理解）。
- [ ] 在浏览器中打开页面，确认排版、图片、导航未损坏。

---

## 9. 工作流程建议

1. **逐章翻译**：按 `Ch001` → `Ch023` 顺序，或按 Part 分组推进。
2. **先结构后润色**：第一遍保证准确与术语统一，第二遍通读润色流畅度。
3. **术语集中管理**：§5 术语表已冻结，翻译中**不得**直接编辑。发现表外术语时写入本页的 `newterms.json`（见 §5.0），由收尾任务统一合并（本书收尾合并已在任务 08 完成）。
4. **对照复核**：译后对照英文原文逐段核对，重点关注被动语态、限定词、长难句。
5. **构建验证**：翻译后重新运行 `build_site.py`（或直接在浏览器打开 `web/index.html`）确认无破坏。

---

*本标准随翻译实践持续修订。§5 术语表的收尾合并（各页 `newterms.json` 并入本表）已在任务 08 完成；此后新增的术语仍写入本页的 `newterms.json`，由后续收尾任务统一合并（见 §5.0）。*
