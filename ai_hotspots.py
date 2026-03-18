import requests
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

keywords = ["AI", "OpenAI", "Python", "GPU", "LLM", "agent", "Mistral", "model"]
results = []

for page in range(1, 4):  # 抓前3页
    url = f"https://news.ycombinator.com/?p={page}"
    response = requests.get(url, verify=False)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.select("tr.athing")

    for row in rows:
        title_tag = row.select_one(".titleline a")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = title_tag.get("href")

        subtext_row = row.find_next_sibling("tr")
        score_tag = subtext_row.select_one(".score") if subtext_row else None
        author_tag = subtext_row.select_one(".hnuser") if subtext_row else None
        comment_links = subtext_row.select("a") if subtext_row else []

        score_text = score_tag.get_text(strip=True) if score_tag else "0 points"
        author = author_tag.get_text(strip=True) if author_tag else "unknown"
        comments = comment_links[-1].get_text(strip=True) if comment_links else "0 comments"

        score_match = re.search(r"\d+", score_text)
        score_num = int(score_match.group()) if score_match else 0

        comments_match = re.search(r"\d+", comments)
        comments_num = int(comments_match.group()) if comments_match else 0

        if any(k.lower() in title.lower() for k in keywords):
            if link.startswith("item?") or link.startswith("from?"):
                full_link = "https://news.ycombinator.com/" + link
            else:
                full_link = link

            domain = urlparse(full_link).netloc.replace("www.", "")
            if not domain:
                domain = "news.ycombinator.com"

            results.append({
                "title": title,
                "link": full_link,
                "score_text": score_text,
                "score_num": score_num,
                "author": author,
                "comments": comments,
                "comments_num": comments_num,
                "domain": domain
            })

# 去重：按标题去重
seen = set()
unique_results = []
for item in results:
    if item["title"] not in seen:
        unique_results.append(item)
        seen.add(item["title"])

results = sorted(unique_results, key=lambda x: (x["score_num"], x["comments_num"]), reverse=True)

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

cards_html = ""

for item in results:
    hot_badge = ""
    if item["score_num"] >= 300:
        hot_badge = '<span class="pill hot">🔥 热门</span>'
    elif item["score_num"] >= 150:
        hot_badge = '<span class="pill warm">热门</span>'

    cards_html += f"""
    <article class="card">
        <div class="score-badge">{item['score_num']}</div>

        <div class="card-top">
            <span class="pill source">{item['domain']}</span>
            {hot_badge}
        </div>

        <a class="title" href="{item['link']}" target="_blank" rel="noopener noreferrer">
            {item['title']}
        </a>

        <div class="meta">
            <span>作者：{item['author']}</span>
            <span>{item['score_text']}</span>
            <span>{item['comments']}</span>
        </div>
    </article>
    """

if not cards_html:
    cards_html = '<div class="empty">今天没有匹配关键词的热点。</div>'

html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>今日 AI 热点</title>
    <style>
        :root {{
            --bg: #081225;
            --panel: rgba(16, 24, 40, 0.78);
            --panel-2: rgba(30, 41, 59, 0.95);
            --text: #e5eefc;
            --muted: #94a3b8;
            --line: rgba(148, 163, 184, 0.14);
            --blue: #60a5fa;
            --cyan: #67e8f9;
            --hot: #fb7185;
            --warm: #f59e0b;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background:
                radial-gradient(circle at top left, rgba(56, 189, 248, 0.12), transparent 30%),
                radial-gradient(circle at top right, rgba(96, 165, 250, 0.10), transparent 28%),
                linear-gradient(180deg, #07111f 0%, #0b1730 100%);
            color: var(--text);
        }}

        .container {{
            width: min(1100px, calc(100% - 32px));
            margin: 0 auto;
        }}

        .hero {{
            padding: 56px 0 28px;
        }}

        .hero-box {{
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.72));
            border: 1px solid var(--line);
            border-radius: 28px;
            padding: 32px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.25);
            backdrop-filter: blur(10px);
        }}

        .eyebrow {{
            display: inline-block;
            font-size: 13px;
            letter-spacing: 0.08em;
            color: var(--cyan);
            margin-bottom: 10px;
        }}

        h1 {{
            margin: 0 0 12px;
            font-size: clamp(34px, 6vw, 56px);
            line-height: 1.05;
        }}

        .sub {{
            color: var(--muted);
            font-size: 16px;
            line-height: 1.7;
            margin-bottom: 20px;
        }}

        .stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }}

        .stat {{
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid var(--line);
            border-radius: 999px;
            padding: 10px 14px;
            color: #dbeafe;
            font-size: 14px;
        }}

        .section-title {{
            margin: 26px 0 16px;
            font-size: 20px;
            color: #dbeafe;
        }}

        .grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
            padding-bottom: 40px;
        }}

        .card {{
            position: relative;
            background: var(--panel-2);
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 22px 22px 22px 84px;
            box-shadow: 0 10px 35px rgba(0,0,0,0.22);
            transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
        }}

        .card:hover {{
            transform: translateY(-2px);
            border-color: rgba(103, 232, 249, 0.28);
            box-shadow: 0 18px 40px rgba(0,0,0,0.28);
        }}

        .score-badge {{
            position: absolute;
            left: 22px;
            top: 24px;
            width: 44px;
            height: 44px;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 16px;
            color: #062033;
            background: linear-gradient(135deg, var(--cyan), var(--blue));
        }}

        .card-top {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
        }}

        .pill {{
            display: inline-flex;
            align-items: center;
            height: 28px;
            padding: 0 10px;
            border-radius: 999px;
            font-size: 13px;
            border: 1px solid var(--line);
        }}

        .pill.source {{
            color: #c7d2fe;
            background: rgba(30, 41, 59, 0.7);
        }}

        .pill.hot {{
            color: #ffe4e6;
            background: rgba(251, 113, 133, 0.14);
            border-color: rgba(251, 113, 133, 0.28);
        }}

        .pill.warm {{
            color: #fef3c7;
            background: rgba(245, 158, 11, 0.12);
            border-color: rgba(245, 158, 11, 0.28);
        }}

        .title {{
            display: block;
            color: #7dd3fc;
            text-decoration: none;
            font-size: clamp(22px, 2.3vw, 32px);
            line-height: 1.35;
            font-weight: 760;
            margin-bottom: 14px;
        }}

        .title:hover {{
            text-decoration: underline;
        }}

        .meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            color: var(--muted);
            font-size: 14px;
        }}

        .empty {{
            background: var(--panel-2);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 24px;
            color: var(--muted);
        }}

        @media (max-width: 680px) {{
            .hero {{
                padding-top: 28px;
            }}

            .hero-box {{
                padding: 22px;
                border-radius: 20px;
            }}

            .card {{
                padding: 20px 18px 18px 18px;
            }}

            .score-badge {{
                position: static;
                margin-bottom: 14px;
            }}

            .title {{
                font-size: 24px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <section class="hero">
            <div class="hero-box">
                <div class="eyebrow">AI HOTSPOTS · AUTO CURATED</div>
                <h1>今日 AI 热点</h1>
                <div class="sub">
                    抓取 Hacker News 前 3 页，按分数和评论热度排序，自动筛选 AI / Python / GPU / LLM / Agent 相关内容。
                </div>

                <div class="stats">
                    <div class="stat">共 {len(results)} 条结果</div>
                    <div class="stat">数据源：Hacker News</div>
                    <div class="stat">生成时间：{now}</div>
                </div>
            </div>
        </section>

        <div class="section-title">热点列表</div>
        <section class="grid">
            {cards_html}
        </section>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("已生成网页文件：index.html")
print(f"共找到 {len(results)} 条 AI 相关热点")