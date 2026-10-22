# 赤蛮奇MVZ2资源集中站

MVZ2（Minecraft VS Zombies 2）各原版和改版的官方链接、下载链接和官方群链接的集中站。

网站地址：[https://sekibanki.genouka.top/](https://sekibanki.genouka.top/)

## 项目结构

```
├── data/                   # 结构化数据（JSON）
│   ├── zh.json             # 中文主页数据
│   ├── en.json             # 英文主页数据
│   ├── gaming_guide.json   # 游戏攻略页数据
│   └── contributing.json   # 贡献指南页数据
├── tool/
│   └── gen.py              # 从 JSON 生成静态 HTML 和数据 JSON 的脚本
├── index.html              # 生成的中文主页
├── index.json              # 中文主页数据（由 data/zh.json 发布）
├── en/index.html           # 生成的英文主页
├── en/index.json           # 英文主页数据（由 data/en.json 发布）
├── gaming_guide.html       # 生成的游戏攻略页
├── gaming_guide.json       # 游戏攻略页数据
├── contributing.html       # 生成的贡献指南页
├── contributing.json       # 贡献指南页数据
├── manifest.json           # 站点清单（所有页面的 HTML/JSON 路径）
├── 404.html                # 404 页面
└── .github/workflows/
    └── static.yml          # GitHub Pages 部署工作流
```

## 如何贡献条目

### 方式一：直接编辑 JSON（推荐）

1. Fork 本仓库
2. 编辑 `data/` 目录下对应的 JSON 文件（`*.html`/`*.json` 由构建自动生成，无需手改）
3. 本地运行 `python tool/gen.py` 生成 HTML 并预览
4. 提交 Pull Request

### 方式二：提交 Issue

在 [Issues](https://github.com/Genouka/SekibankiMvzWeb/issues) 页面提交：
- 新增条目的名称、链接、备注
- 修改现有条目的错误信息
- 任何其他建议

### JSON 数据格式

在 `version_table.rows` 中新增一个条目，格式如下：

```json
{
  "name": "改版名称[引擎]",
  "links": [
    { "text": "链接显示文字", "href": "https://example.com" },
    { "text": "另一个链接", "href": "https://example2.com" }
  ],
  "note": "备注信息，支持<a href=\"...\">HTML</a>"
}
```

字段说明：

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | 改版名称，建议附带引擎标识如 `[GMS]`、`[Unity]` |
| `links` | 是 | 链接数组，每项含 `text` 和 `href` |
| `note` | 否 | 备注信息，支持 HTML 标签 |
| `extra_text` | 否 | 链接列额外文字（纯文本） |
| `links_text_only` | 否 | 若为 `true`，则 `note` 内容显示在链接列，备注列留空 |

## JSON 数据接口

为了让其他客户端（App、Bot、聚合工具等）也能使用本站数据，构建时会将每页的结构化 JSON 一并发布到网站，路径与 HTML 页面一一对应：

| HTML 页面 | JSON 数据 | 数据源 |
|-----------|-----------|--------|
| `index.html` | `index.json` | `data/zh.json` |
| `en/index.html` | `en/index.json` | `data/en.json` |
| `gaming_guide.html` | `gaming_guide.json` | `data/gaming_guide.json` |
| `contributing.html` | `contributing.html` 对应的 `contributing.json` | `data/contributing.json` |
| — | `manifest.json` （站点清单） | 构建脚本自动生成 |

例如英文主页数据的访问地址为：`https://sekibanki.genouka.top/en/index.json`

- 每个 HTML 页面的 `<title>` 后带有 `<link rel="alternate" type="application/json" href="...">`，客户端可据此自动发现对应的 JSON
- `manifest.json` 列出所有页面的 `title`、`language`、`html` 与 `json` 路径，可作为接入的入口文件
- 页面对应的 JSON 与 `data/` 下的源文件内容完全一致，`python tool/gen.py --check` 会同时校验两者

### 编写客户端时的建议

1. 先请求 `manifest.json` 获取页面列表
2. 根据需要请求对应的 `*.json` 获取结构化数据
3. 数据更新请关注 `last_updated` 字段

## 本地预览

```bash
python tool/gen.py        # 生成所有 HTML 页面
python tool/gen.py --check # 检查已生成的文件是否需要更新
```

生成后直接在浏览器中打开 `index.html` 即可预览。

## 注意事项

- 所有链接必须是官方可信链接
- 涉及争议内容的条目需在 `name` 或 `note` 中标注 `[争议]`
- 已停更的改版需在 `note` 中注明
- 中文版为首先更新的版本，英文版可随后同步

## 许可

本网站赤蛮奇标志图片由 Cuerzor58 授权使用，系东方Project的同人二次创作，未经作者允许不可使用于他处。
