#!/usr/bin/env python3
"""
从结构化JSON数据和HTML模板生成静态HTML页面。

用法:
    python tool/gen.py          # 生成所有页面
    python tool/gen.py --check  # 检查生成的文件是否与源文件一致
"""

import io
import json
import os
import shutil
import sys
from html import escape
from string import Template

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "dist")

# 需要复制到 dist 的静态资源
STATIC_ASSETS = [
    "sekibanki_logo_trans.webp",
    "sekibanki_mvz2.webp",
    "CNAME",
    "404.html",
]

UMAMI_SCRIPT = '<script defer src="https://status.genouka.top/script.js" data-website-id="fcac57f6-6c68-420e-a63a-c3fdbd63f160"></script>'
UMAMI_TRACKER = """<script type="text/javascript">
  (() => {
    const name = 'outbound-link-click';
    document.querySelectorAll('a').forEach(a => {
      if (a.host !== window.location.host && !a.getAttribute('data-umami-event')) {
        a.setAttribute('data-umami-event', name);
        a.setAttribute('data-umami-event-url', a.href);
      }
    });
  })();
</script>"""


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def render_link(link):
    return f'<a href="{escape(link["href"])}">{link["text"]}</a>'


def render_links(links):
    return "<br>\n".join(render_link(link) for link in links)


def render_table(headers, rows):
    header_html = "".join(f"<th>{h}</th>" for h in headers)
    rows_html = ""
    for row in rows:
        name = row["name"]
        if row.get("links_text_only"):
            links_cell = escape(row.get("note", "")) if row.get("note") else ""
            note_cell = ""
        elif row.get("links"):
            links_cell = render_links(row["links"])
            if row.get("extra_text"):
                links_cell += "<br>" + escape(row["extra_text"])
            note_cell = row.get("note", "")
        else:
            links_cell = ""
            note_cell = row.get("note", "")
        rows_html += f"""      <tr>
        <td>{name}</td>
        <td>
            {links_cell}
        </td>
        <td>{note_cell}</td>
      </tr>
"""
    return f"""  <table border="1" cellspacing="0" cellpadding="6">
    <thead>
      <tr>
{"".join(f"        {h}\n" for h in header_html.split("</th>") if h.strip())}      </tr>
    </thead>
    <tbody>
{rows_html}    </tbody>
  </table>"""


def generate_index_zh(data, json_href=""):

    d = data
    meta = d["meta"]
    header = d["header"]
    vt = d["version_table"]
    rt = d["resource_table"]
    fn = d["footnotes"]
    footer = d["footer"]

    # Build version table
    vt_headers = "".join(f"<th>{h}</th>" for h in vt["headers"])
    vt_rows = ""
    for row in vt["rows"]:
        name = row["name"]
        if row.get("links_text_only"):
            links_cell = escape(row.get("note", ""))
            note_cell = ""
        elif row.get("links"):
            links_cell = render_links(row["links"])
            if row.get("extra_text"):
                links_cell += "<br>" + row["extra_text"]
            note_cell = row.get("note", "")
        else:
            links_cell = ""
            note_cell = row.get("note", "")
        vt_rows += f"""      <tr>
        <td>{name}</td>
        <td>
            {links_cell}
        </td>
        <td>{note_cell}</td>
      </tr>
"""

    # Build resource table
    rt_headers = "".join(f"<th>{h}</th>" for h in rt["headers"])
    rt_rows = ""
    for row in rt["rows"]:
        name = row["name"]
        links_cell = render_links(row["links"]) if row.get("links") else ""
        note_cell = row.get("note", "")
        rt_rows += f"""      <tr>
        <td>{name}</td>
        <td>{links_cell}</td>
        <td>{note_cell}</td>
      </tr>
"""

    # Build footnotes table
    fn_rows = ""
    for item in fn["items"]:
        fn_rows += f"""    <tr>
        <td>{item['label']}</td>
        <td>
            <p>{item['content']}</p>
        </td>
    </tr>
"""

    analytics_style = f'style="color:{footer["analytics_color"]}"' if footer.get("analytics_color") else ""

    html = f"""<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta http-equiv='content-language' content='{meta["language"]}'>
<style>
body {{
background-color: #eeeeee;
color: #000000;
}}
a {{
    white-space: nowrap;
    color: sienna;
}}
@media (prefers-color-scheme: dark) {{
body {{
background-color: #222222;
color: #dddddd;
}}
a {{
    color: pink;
}}
}}
</style>
<title>{meta["title"]}</title>
{f'<link rel="alternate" type="application/json" href="{json_href}">' if json_href else ""}
<div style="display:none"><p>{header["description"]}</p></div>
<center>
<h1><img src="{meta["logo_img"]}" alt="{meta["logo_alt"]}" style="max-width: 100%;max-height: 30vh;"><br>{header["heading"]}</h1>
<p>最后更新于{meta["last_updated"]}</p>
<p>{header["other_lang_text"]} <a href="{header["other_lang_link"]["href"]}">{header["other_lang_link"]["text"]}</a></p>
<p style="color:green">{header["trust_notice"]}</p>
<p>{header["sub_page"]["label"]}<a href="{header["sub_page"]["href"]}">{header["sub_page"]["text"]}</a></p>
<p><a href="{header["contributing_link"]["href"]}">{header["contributing_link"]["text"]}</a></p>
<h2>{vt["title"]}</h2>
<div style="width: 100%;overflow-x: auto;">
  <table border="1" cellspacing="0" cellpadding="6">
    <thead>
      <tr>
        {vt_headers}
      </tr>
    </thead>
    <tbody>
{vt_rows}    </tbody>
  </table>
</div>
<p>{vt["footnote"]}</p>
<h2>{rt["title"]}</h2>
<div style="width: 100%;overflow-x: auto;">
  <table border="1" cellspacing="0" cellpadding="6">
    <thead>
      <tr>
        {rt_headers}
      </tr>
    </thead>
    <tbody>
{rt_rows}    </tbody>
  </table>
</div>
<hr/>
<h2>{fn["title"]}</h2>
<table border="1" cellspacing="0" cellpadding="6">
{fn_rows}</table>
<p>{fn["disclaimer"]}</p>
<hr/>
<p>{footer["maintainer_text"]}</p>
<p>{footer["logo_notice"]}</p>
<p {analytics_style}>{footer["analytics_notice"]}</p>
<p><a href="{footer["badge_link"]}"><img src="{footer["badge_img"]}" alt="{footer["badge_alt"]}"/></a></p>
<p><a href="{footer["github_url"]}">{footer["github_text"]}</a></p>
</center>
{UMAMI_SCRIPT}
{UMAMI_TRACKER}
"""
    return html


def generate_index_en(data, json_href=""):

    d = data
    meta = d["meta"]
    header = d["header"]
    vt = d["version_table"]
    rt = d["resource_table"]
    fn = d["footnotes"]
    footer = d["footer"]

    vt_headers = "".join(f"<th>{h}</th>" for h in vt["headers"])
    vt_rows = ""
    for row in vt["rows"]:
        name = row["name"]
        if row.get("links_text_only"):
            links_cell = ""
            note_cell = row.get("note", "")
        elif row.get("links"):
            links_cell = render_links(row["links"])
            if row.get("extra_text"):
                links_cell += "<br>" + row["extra_text"]
            note_cell = row.get("note", "")
        else:
            links_cell = ""
            note_cell = row.get("note", "")
        vt_rows += f"""      <tr>
        <td>{name}</td>
        <td>
            {links_cell}
        </td>
        <td>{note_cell}</td>
      </tr>
"""

    rt_headers = "".join(f"<th>{h}</th>" for h in rt["headers"])
    rt_rows = ""
    for row in rt["rows"]:
        name = row["name"]
        links_cell = render_links(row["links"]) if row.get("links") else ""
        note_cell = row.get("note", "")
        rt_rows += f"""      <tr>
        <td>{name}</td>
        <td>{links_cell}</td>
        <td>{note_cell}</td>
      </tr>
"""

    fn_rows = ""
    for item in fn["items"]:
        fn_rows += f"""    <tr>
        <td>{item['label']}</td>
        <td>
            <p>{item['content']}</p>
        </td>
    </tr>
"""

    analytics_style = f'style="color:{footer["analytics_color"]}"' if footer.get("analytics_color") else ""

    other_lang_line = f'<a href="{header["other_lang_link"]["href"]}">{header["other_lang_link"]["text"]}</a>'

    html = f"""<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta http-equiv='content-language' content='{meta["language"]}'>
<style>
body {{
background-color: #eeeeee;
color: #000000;
}}
a {{
    white-space: nowrap;
    color: sienna;
}}
@media (prefers-color-scheme: dark) {{
body {{
background-color: #222222;
color: #dddddd;
}}
a {{
    color: pink;
}}
}}
</style>
<title>{meta["title"]}</title>
{f'<link rel="alternate" type="application/json" href="{json_href}">' if json_href else ""}
<div style="display:none"><p>{header["description"]}</p></div>
<center>
<h1><img src="{meta["logo_img"]}" alt="{meta["logo_alt"]}" style="max-width: 100%;max-height: 30vh;"><br>{header["heading"]}</h1>
<p>Last updated: {meta["last_updated"]}</p>
<p>{other_lang_line}</p>
<p style="color:green">{header["trust_notice"]}</p>
<p>{header["sub_page"]["label"]}<a href="{header["sub_page"]["href"]}">{header["sub_page"]["text"]}</a></p>
<p><a href="{header["contributing_link"]["href"]}">{header["contributing_link"]["text"]}</a></p>
<h2>{vt["title"]}</h2>
<div style="width: 100%;overflow-x: auto;">
  <table border="1" cellspacing="0" cellpadding="6">
    <thead>
      <tr>
        {vt_headers}
      </tr>
    </thead>
    <tbody>
{vt_rows}    </tbody>
  </table>
</div>
<p>{vt["footnote"]}</p>
<h2>{rt["title"]}</h2>
<div style="width: 100%;overflow-x: auto;">
  <table border="1" cellspacing="0" cellpadding="6">
    <thead>
      <tr>
        {rt_headers}
      </tr>
    </thead>
    <tbody>
{rt_rows}    </tbody>
  </table>
</div>
<hr/>
<h2>{fn["title"]}</h2>
<table border="1" cellspacing="0" cellpadding="6">
{fn_rows}</table>
<p>{fn["disclaimer"]}</p>
<hr/>
<p>{footer["maintainer_text"]}</p>
<p>{footer["logo_notice"]}</p>
<p {analytics_style}>{footer["analytics_notice"]}</p>
<p><a href="{footer["badge_link"]}"><img src="{footer["badge_img"]}" alt="{footer["badge_alt"]}"/></a></p>
<p><a href="{footer["github_url"]}">{footer["github_text"]}</a></p>
</center>
{UMAMI_SCRIPT}
{UMAMI_TRACKER}
"""
    return html


def generate_gaming_guide(data, json_href=""):

    d = data
    meta = d["meta"]
    header = d["header"]
    table = d["table"]
    footer = d["footer"]

    tbl_headers = "".join(f"<th>{h}</th>" for h in table["headers"])
    tbl_rows = ""
    for row in table["rows"]:
        name = row["name"]
        links_cell = render_links(row["links"]) if row.get("links") else ""
        note_cell = row.get("note", "")
        tbl_rows += f"""      <tr>
        <td>{name}</td>
        <td>{links_cell}</td>
        <td>{note_cell}</td>
      </tr>
"""

    analytics_style = f'style="color:{footer["analytics_color"]}"' if footer.get("analytics_color") else ""

    html = f"""<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta http-equiv='content-language' content='{meta["language"]}'>
<style>
body {{
background-color: #eeeeee;
color: #000000;
}}
a {{
    white-space: nowrap;
    color: sienna;
}}
@media (prefers-color-scheme: dark) {{
body {{
background-color: #222222;
color: #dddddd;
}}
a {{
    color: pink;
}}
}}
</style>
<title>{meta["title"]}</title>
{f'<link rel="alternate" type="application/json" href="{json_href}">' if json_href else ""}
<center>
<a href="{header["breadcrumb"]["href"]}">{header["breadcrumb"]["text"]}</a> &gt;&gt; {header["breadcrumb_current"]}<br>
<span style="color:red">{header["construction_notice"]}</span><br>
<h1><img src="{meta["logo_img"]}" alt="{meta["logo_alt"]}" style="max-width: 100%;max-height: 30vh;"><br>{header["heading"]}</h1>
<p>最后更新于{meta["last_updated"]}</p>
<div style="width: 100%;overflow-x: auto;">
  <table border="1" cellspacing="0" cellpadding="6">
    <thead>
      <tr>
        {tbl_headers}
      </tr>
    </thead>
    <tbody>
{tbl_rows}    </tbody>
  </table>
</div>
<hr/>
<p>{footer["maintainer_text"]}</p>
<p>{footer["logo_notice"]}</p>
<p {analytics_style}>{footer["analytics_notice"]}</p>
</center>
{UMAMI_SCRIPT}
{UMAMI_TRACKER}
"""
    return html


def generate_contributing(data, json_href=""):

    d = data
    meta = d["meta"]
    header = d["header"]
    sections = d["sections"]
    footer = d["footer"]

    sections_html = ""
    for section in sections:
        sections_html += f"<h2>{section['title']}</h2>\n"
        if section.get("items"):
            for item in section["items"]:
                sections_html += f"<h3>{item['subtitle']}</h3>\n{item['content']}\n"
        if section.get("content"):
            sections_html += f"{section['content']}\n"

    html = f"""<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta http-equiv='content-language' content='{meta["language"]}'>
<style>
body {{
background-color: #eeeeee;
color: #000000;
}}
a {{
    white-space: nowrap;
    color: sienna;
}}
@media (prefers-color-scheme: dark) {{
body {{
background-color: #222222;
color: #dddddd;
}}
a {{
    color: pink;
}}
}}
code {{
    background-color: #f0f0f0;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.9em;
}}
@media (prefers-color-scheme: dark) {{
code {{
    background-color: #333333;
}}
}}
pre {{
    background-color: #f0f0f0;
    padding: 12px;
    border-radius: 5px;
    overflow-x: auto;
    text-align: left;
    display: inline-block;
    max-width: 90vw;
}}
@media (prefers-color-scheme: dark) {{
pre {{
    background-color: #333333;
}}
}}
</style>
<title>{meta["title"]}</title>
{f'<link rel="alternate" type="application/json" href="{json_href}">' if json_href else ""}
<center>
<a href="{header["breadcrumb"]["href"]}">{header["breadcrumb"]["text"]}</a><br>
<h1>{header["heading"]}</h1>
{sections_html}
<hr/>
<p>{footer["contribute_text"]}</p>
<p><a href="{footer["github_url"]}">{footer["github_text"]}</a></p>
</center>
{UMAMI_SCRIPT}
{UMAMI_TRACKER}
"""
    return html


# 站点清单文件名，包含所有页面的 HTML/JSON 路径，便于客户端发现和接入
MANIFEST_NAME = "manifest.json"


def json_path_for(output_path):
    """页面 HTML 输出路径对应的 JSON 输出路径（同目录同名，仅扩展名不同）。"""
    assert output_path.endswith(".html")
    return output_path[:-5] + ".json"


def to_url_path(path):
    """将文件系统路径转换为 URL 风格的相对路径（使用正斜杠）。"""
    return path.replace(os.sep, "/")


PAGES = [
    ("data/zh.json", "index.html", generate_index_zh),
    ("data/en.json", "en/index.html", generate_index_en),
    ("data/gaming_guide.json", "gaming_guide.html", generate_gaming_guide),
    ("data/contributing.json", "contributing.html", generate_contributing),
]


def build_manifest(entries):
    buf = io.StringIO()
    json.dump({"pages": entries}, buf, ensure_ascii=False, indent=2)
    buf.write("\n")
    return buf.getvalue()


def check_output(output_path, full_output_path, content, all_ok):
    if os.path.exists(full_output_path):
        with open(full_output_path, "r", encoding="utf-8") as f:
            existing = f.read()
        if existing == content:
            print(f"  OK: {output_path}")
        else:
            print(f"  DIFF: {output_path} (needs regeneration)")
            all_ok = False
    else:
        print(f"  MISSING: {output_path}")
        all_ok = False
    return all_ok


def write_output(output_path, full_output_path, content):
    os.makedirs(os.path.dirname(full_output_path), exist_ok=True)
    with open(full_output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Generated: {to_url_path(output_path)}")


def generate_all(check_only=False):
    all_ok = True

    if not check_only:
        # 清理 dist 目录
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # 复制静态资源
        for asset in STATIC_ASSETS:
            src = os.path.join(BASE_DIR, asset)
            dst = os.path.join(OUTPUT_DIR, asset)
            if os.path.exists(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                print(f"  Copied: {asset}")

    manifest = []

    for data_path, output_path, generator in PAGES:
        full_data_path = os.path.join(BASE_DIR, data_path)
        full_output_path = os.path.join(OUTPUT_DIR, output_path)
        json_output = json_path_for(output_path)
        full_json_path = os.path.join(OUTPUT_DIR, json_output)

        data = load_json(full_data_path)
        html = generator(data, json_href=os.path.basename(json_output))

        meta = data.get("meta", {})
        manifest_entry = {
            "title": meta.get("title"),
            "language": meta.get("language"),
            "html": to_url_path(output_path),
            "json": to_url_path(json_output),
        }
        if meta.get("last_updated"):
            manifest_entry["last_updated"] = meta["last_updated"]
        manifest.append(manifest_entry)

        if check_only:
            all_ok = check_output(output_path, full_output_path, html, all_ok)
            with open(full_data_path, "r", encoding="utf-8") as f:
                json_content = f.read()
            all_ok = check_output(json_output, full_json_path, json_content, all_ok)
        else:
            write_output(output_path, full_output_path, html)
            # 直接复制源数据 JSON，保证与 data/ 目录内容一致
            shutil.copyfile(full_data_path, full_json_path)
            print(f"  Generated: {to_url_path(json_output)}")

    # 生成站点清单
    manifest_content = build_manifest(manifest)
    manifest_output = os.path.join(OUTPUT_DIR, MANIFEST_NAME)
    if check_only:
        all_ok = check_output(MANIFEST_NAME, manifest_output, manifest_content, all_ok)
    else:
        write_output(MANIFEST_NAME, manifest_output, manifest_content)

    return all_ok


if __name__ == "__main__":
    check_only = "--check" in sys.argv
    if check_only:
        print("Checking generated files...")
        ok = generate_all(check_only=True)
        sys.exit(0 if ok else 1)
    else:
        print("Generating static HTML pages...")
        generate_all()
        print("Done!")
