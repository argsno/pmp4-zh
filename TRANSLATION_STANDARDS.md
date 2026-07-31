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

### 4.6 导航栏与目录（例外）
`web/index.html` 与各章 `<header class="topnav">` 中的 `<select>` 下拉项当前**保留英文**，以保证与既有锚点、文件名一致、避免破坏跳转。待全书译毕后，可统一将 `optgroup` 文案（如 `Chapter 1. Introduction`）及 `option` 显示文本中译，但 `value` 属性中的文件名不可改。

### 4.7 Exercises（习题）
`Exercises` 译为"习题"。题干、提示译为中文；其中的代码片段、变量名、输出示例保留原文格式。

### 4.8 References（参考文献）
`References` 译为"参考文献"。文献条目中的**作者姓名、文章/书名、期刊/会议名、出版信息保留原文**（专有名词不译）；条目前后若含解释性文字可译为中文。若需提供中文译名，以括号附于原文之后，不得替换原文。

---

## 5. 术语对照表（核心）

> 原则：与 NVIDIA 官方 CUDA 中文文档保持一致；首现时按 §7 在括号内保留英文原词（如"线程束（warp）"），后续直接使用中文。对已按表格约定"保留不译"的词（如 API 名、GPU/CUDA 等），不适用本条。

### 5.0 本表的状态与读法

**状态：已冻结（frozen）。**

本表在全书翻译开工前一次性扩充完成并经维护者过目。翻译任务对本表**只读**：

- 翻译任务**不得**编辑本文件。多个翻译任务并发运行时，同时写同一个共享文件必然互相覆盖。
- 遇到表外新词，写入本页自己的 `translations/<page-stem>/newterms.json`，格式为 `{"en": …, "zh": …, "note": …}`，收尾时由专门任务统一合并回本表。
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
3. **术语集中管理**：§5 术语表已冻结，翻译中**不得**直接编辑。发现表外术语时写入本页的 `newterms.json`（见 §5.0），由收尾任务统一合并。
4. **对照复核**：译后对照英文原文逐段核对，重点关注被动语态、限定词、长难句。
5. **构建验证**：翻译后重新运行 `build_site.py`（或直接在浏览器打开 `web/index.html`）确认无破坏。

---

*本标准随翻译实践持续修订。但 §5 术语表在翻译期间冻结：新词写入本页的 `newterms.json`，由收尾任务统一合并（见 §5.0）。*
