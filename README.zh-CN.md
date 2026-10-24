# Pictionary 多语言生成器（Pictionary I18N Generator）

> **Pictionary 词站的多语言生成器——把词库与内容页翻译为西班牙语、德语、法语、葡萄牙语版本，并输出完整的 hreflang alternate 组，让每个语言版本在搜索引擎眼里都正确互链。仅标准库。**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CLI](https://img.shields.io/badge/CLI-ready-4B8BBE)](i18n_generator.py)
[![No dependencies](https://img.shields.io/badge/deps-stdlib%20only-blueviolet)](requirements.txt)

---

## 相关链接

- 🎲 **在线工具体验：** [Pictionary Word Generator — 免费 7000+ 画画提示词](https://pictionarywordgenerators.com/)
- 🕹️ **在线对战：** [Virtual Pictionary — 浏览器里和朋友一起玩](https://pictionarywordgenerators.com/virtual-pictionary)
- 英文版说明：[README.md](README.md)

---

## 这个工具做什么

一个只有英文的内容站，等于把大半互联网拒之门外。把词库和主题页本地化，
就能打开西语、德语、法语、葡语市场——但前提是搜索引擎能区分这些语言版本，
这就是 hreflang 的职责：组里少一种语言、少了 `x-default`、或者某个 alternate
URL 写错，都可能让所有语言版本在索引里被压制。

本工具自动化这两半：

1. **`translate`** — 把词库 JSON 翻译成逐语言 JSON（`es` / `de` / `fr` /
   `pt`）：内置离线词典表、逐词覆盖标记、`i18n-manifest.json` 汇总。
   完全确定性，无 API Key，数据不出本机。
2. **`pages`** — 渲染语言感知的 HTML 页面（词表 + 生成器嵌入 + FAQ），
   带**完整 hreflang alternate 组**（英文 + 4 语言 + `x-default`）、
   canonical、Open Graph 与 JSON-LD WebPage schema。多语言标题/描述/FAQ
   文案内置在 `PAGE_COPY` 表中。
3. **`verify`** — 校验任意渲染页面：hreflang 组是否含全部语言、
   `x-default` 是否在、站内 URL 是否零裸 URL（排除 JSON-LD 与属性 URL）。
   CI 友好，发现问题退出非零。

内置词典覆盖 49 个常见 Pictionary 词的四语翻译；表外词保留英文并标记
`untranslated` + 覆盖率百分比，让你随时知道专业译员还需要审校哪些词。

## 为什么重要

这是工具链之上的本地化层：
[Pictionary Wordlist Generator](https://github.com/anleeylee/pictionary-wordlist-generator)
创建词库，[Pictionary Page Generator](https://github.com/anleeylee/pictionary-page-generator)
生成英文页面，[Pictionary SEO Scanner](https://github.com/anleeylee/pictionary-seo-scanner)
保证站内 SEO 健康，[Pictionary Keyword Tracker](https://github.com/anleeylee/pictionary-keyword-tracker)
决定下一个做什么，[Pictionary GSC Monitor](https://github.com/anleeylee/pictionary-gsc-monitor)
跟踪收录，[Pictionary Link Matrix](https://github.com/anleeylee/pictionary-link-matrix)
扩张外链。本工具把同样的页面与词库以四种语言输出——并配上谷歌信得过的
hreflang 组。

## 安装

```bash
git clone https://github.com/anleeylee/pictionary-i18n-generator.git
cd pictionary-i18n-generator

# 仅标准库 —— 无需 pip install
python i18n_generator.py --help
```

## 用法

```bash
# 1. 把词库翻译为 es / de / fr / pt JSON + 汇总清单
python i18n_generator.py translate \
  --input examples/wordlist.json --out-dir out

# 2. 渲染带完整 hreflang 组的多语言 HTML 页面
python i18n_generator.py pages \
  --input examples/wordlist.json --slug virtual-pictionary --out-dir out

# 3. 卫生门禁（CI 友好，发现问题退出非零）
python i18n_generator.py verify \
  --file out/virtual-pictionary.es.html
```

### 输出

- `<slug>.{es,de,fr,pt}.json` + `i18n-manifest.json` — 逐语言词库与覆盖统计
- `<slug>.{en,es,de,fr,pt}.html` — 语言感知页面：hreflang 组、canonical、
  Open Graph、JSON-LD schema、翻译词表与 FAQ

## 测试

```bash
python -m unittest discover -s tests -v
```

覆盖：词典查询（已知/未知/大小写/全部 4 语言）、词库翻译结构与覆盖标记、
完整 hreflang 组与本地化 URL、渲染页面 head 完整性、裸 URL 识别（排除
script/属性）、完整 CLI 链路。15 项测试，全部离线。

## 许可

MIT——可自由使用与扩展，请保留署名。词典表可继续扩充，生成的页面可自由发布。
