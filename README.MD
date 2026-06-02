# UUextract_news

一个面向中文新闻网页的正文与元信息抽取项目。当前代码的核心能力是从新闻 URL 或 HTML 字符串中解析标题、发布时间、来源、正文 HTML 和纯文本，适合作为爬虫、新闻清洗、搜索聚合、RAG 入库或后续 LLM 摘要/分析链路的前置抽取层。

> 现状说明：原 README 提到 “searxng 和 LLM”，但当前仓库没有看到 searxng 调用、LLM 调用或相关配置。现在的稳定主体是 HTML 新闻解析；searxng/LLM 更像后续集成方向，不应被当作已实现能力。

## 功能概览

- 从 URL 拉取页面，并用 `chardet` 识别响应编码。
- 清理脚本、样式、噪声标签和常见无用文本。
- 通过 DOM 结构评分定位新闻正文区域。
- 基于 `class` / `id` 候选节点进行二次正文筛选。
- 提取并归一化正文中的图片链接。
- 提取标题、发布时间、来源等新闻元信息。
- 返回正文 HTML、纯文本、标题、日期、来源和清洗后的页面 HTML。
- 提供 `FastAPI` 服务接口，可通过 HTTP 提交 URL 获取抽取结果。
- `Bert/` 目录包含数据准备和 BERT 训练实验代码，用于后续探索机器学习辅助抽取。

## 项目结构

```text
.
├── main.py                  # 本地脚本入口，批量调用 UU.uu() 抽取新闻
├── server.py                # FastAPI 服务入口
├── req.py                   # HTTP 请求封装，负责请求头和编码识别
├── config.py                # 全局规则、阈值、标签白名单、正则配置
├── requirements.txt         # 核心依赖版本
├── extract/
│   ├── __init__.py          # UU 主入口，整合正文、标题、日期、来源抽取
│   ├── news.py              # 新闻正文抽取主流程
│   ├── parse.py             # DOM 评分、meta 读取、质量检测等通用解析逻辑
│   ├── title.py             # 标题提取与清洗
│   ├── date.py              # 发布时间提取
│   └── source.py            # 来源提取
├── clearner/
│   └── clean.py             # HTML 清洗、噪声过滤、图片链接处理
├── example/
│   ├── __init__.py          # 历史测试 URL 集合
│   └── links.py             # 另一组测试 URL
├── Bert/
│   ├── extract_.py          # 简单抓取并生成新闻训练数据
│   ├── read_data.py         # 从 MongoDB 读取 URL 并生成模型数据
│   ├── rem.py               # 模型数据清洗实验
│   └── train.py             # BERT 分类训练实验
├── html_source/
│   └── t1.html              # 本地 HTML 样例，不是完整新闻正文样例
└── plan.txt                 # 历史开发计划和测试 URL 记录
```

## 核心抽取流程

主入口是 `extract.UU`：

1. `Req.req()` 请求网页并设置响应编码。
2. `RemoveUseless.clean_jumbled_text()` 移除已知噪声文本。
3. `RemoveUseless.clean_article_html()` 用标签白名单清理 HTML。
4. `Parse.dom_tree()` 统计候选节点中的段落数量、中文标点数量和容器复杂度，选择最可能的正文节点。
5. `RemoveUseless.id_cls()` 根据 `class` / `id` 节点再次竞争，得到最终正文块。
6. `Title.summarize()` 从 `title`、`h1`、`meta title` 中抽取标题。
7. `Date.extract_date()` 从 date 类 meta 或正文正则中抽取日期。
8. `Source.source()` 从 `meta source` 或页面 “来源” 文案中抽取来源。

返回字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `title` | `str` | 新闻标题 |
| `date` | `str \| None` | 发布时间，优先来自 meta，其次来自正文正则 |
| `source` | `list[str]` | 新闻来源 |
| `article` | `str` | 正文 HTML 片段 |
| `plain_text` | `str` | 去空白后的正文纯文本 |
| `html` | `str` | 清洗后的页面 HTML |

## 快速开始

当前仓库自带 `venv/`，本机验证可直接使用：

```bash
source venv/bin/activate
python main.py
```

如果重新创建环境：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

注意：`requirements.txt` 没有列出服务端和 MongoDB 实验依赖。运行 `server.py` 需要额外安装：

```bash
pip install fastapi uvicorn pydantic
```

运行 `Bert/read_data.py` 需要额外安装：

```bash
pip install pymongo
```

## Python 调用示例

```python
from extract import UU

extractor = UU()
result = extractor.uu(url="https://www.jiemian.com/article/12161417.html")

if result:
    print(result["title"])
    print(result["date"])
    print(result["source"])
    print(result["plain_text"])
```

也可以直接传入 HTML：

```python
from extract import UU

html = """
<html>
  <head>
    <title>测试新闻-测试网</title>
    <meta name="source" content="测试来源">
    <meta name="pubdate" content="2024-11-10">
  </head>
  <body>
    <div class="article">
      <h1>测试新闻标题</h1>
      <p>这是第一段新闻正文，包含足够多的中文标点，方便算法识别正文。</p>
      <p>这是第二段新闻正文，继续补充信息，确保正文长度超过阈值。</p>
      <p>这是第三段新闻正文，用于验证文章节点和纯文本输出是否可用。</p>
    </div>
  </body>
</html>
"""

result = UU().uu(html=html)
print(result["plain_text"])
```

## HTTP 服务

启动服务：

```bash
source venv/bin/activate
python server.py
```

`server.py` 当前监听 `0.0.0.0:8002`，接口为：

```text
POST /extract_plain_text/
Content-Type: application/json
```

请求示例：

```bash
curl -X POST http://127.0.0.1:8002/extract_plain_text/ \
  -H "Content-Type: application/json" \
  -d '{"url":"https://news.cctv.com/2024/11/10/ARTI1WOIBcN6zmKU0lzbZBTz241110.shtml"}'
```

响应示例：

```json
{
  "url": "https://news.cctv.com/2024/11/10/ARTI1WOIBcN6zmKU0lzbZBTz241110.shtml",
  "source": ["央视网"],
  "plain_text": "..."
}
```

以 `server.py` 为准：仓库里的 `test.py` 仍使用旧的 `localhost:8000/extract_plain_text` 示例，端口和路径都不是当前服务入口。

## BERT 实验目录

`Bert/` 目录不是当前正文抽取的必需依赖，主要用于实验：

- `extract_.py`：抓取少量 URL，提取标题和正文，生成 `news_data.json`。
- `read_data.py`：从本地 MongoDB `spider_data.model` 集合读取 URL，调用 `UU` 生成模型训练数据。
- `rem.py`：清洗 `model_data.json` 并输出 `model_cleaned_data.json`。
- `train.py`：加载清洗数据，使用 `transformers` 的 BERT 分类模型进行训练实验。

这里的训练代码还处于探索状态，不能直接视作可生产使用的模型训练管线。比如 `train.py` 对数据字段、标签构造和模型目标的假设仍比较粗糙，真实使用前需要重新梳理数据格式、标签体系和评估方式。

## 已知限制

- 对强依赖前端渲染的页面支持有限；当前实现主要处理服务端返回 HTML 中已经包含正文的页面。
- 正文二次筛选依赖 `class` / `id` 候选节点，极简 HTML 或结构异常页面可能抽不到正文。
- `plain_text` 会移除大量空白字符，适合检索和入库，但不保留自然段落格式。
- `Req.req()` 默认超时时间为 5 秒，网络差或站点反爬时容易失败。
- `requirements.txt` 中部分依赖版本较旧，尤其是 `lxml==4.6.3`、`torch==1.8.1`、`transformers==4.5.1`，在新 Python 环境上可能需要单独适配。
- 当前没有自动化测试，主要靠脚本和 URL 样本人工验证。
- `Bert/model_data.json` 体积较大，更像生成数据，不适合作为 README 中的手工维护内容。

## 后续 TODO

- 统一服务端、测试脚本和 README 中的端口与路径。
- 给 `requirements.txt` 补齐 `fastapi`、`uvicorn`、`pydantic`、`pymongo` 等可选依赖，或拆成 core/server/experiment 多份依赖文件。
- 给 `UU.uu()` 增加更明确的错误返回结构，避免异常时只打印错误并返回 `None`。
- 保留段落分隔，新增 `paragraphs` 字段。
- 增加图片列表字段，例如 `imgs`。
- 为动态网页增加浏览器渲染或正文 API 兜底方案。
- 引入自动化测试，覆盖典型新闻站、异常 HTML、无正文页面和编码异常页面。
- 如果要接入 searxng 和 LLM，需要新增搜索入口、去重策略、抽取队列、摘要/分类提示词和结果存储结构。
