import requests
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

results = []

keywords = ["AI", "OpenAI", "Python", "GPU", "LLM", "agent", "Mistral", "model"]
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

        import re
        match = re.search(r"\d+", score_text)
        score_num = int(match.group()) if match else 0

        if any(k.lower() in title.lower() for k in keywords):
            if link.startswith("item?") or link.startswith("from?"):
                link = "https://news.ycombinator.com/" + link

            results.append({
                "title": title,
                "link": link,
                "score_text": score_text,
                "score_num": score_num,
                "author": author,
                "comments": comments
            })


response.encoding = response.apparent_encoding
soup = BeautifulSoup(response.text, "html.parser")

rows = soup.select("tr.athing")
results = []

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

    # 提取纯数字分数，方便排序
    match = re.search(r"\d+", score_text)
    score_num = int(match.group()) if match else 0

    if any(k.lower() in title.lower() for k in keywords):
        if link.startswith("item?") or link.startswith("from?"):
            link = "https://news.ycombinator.com/" + link

        results.append({
            "title": title,
            "link": link,
            "score_text": score_text,
            "score_num": score_num,
            "author": author,
            "comments": comments
        })

# 按分数从高到低排序
results.sort(key=lambda x: x["score_num"], reverse=True)

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

cards_html = ""

for item in results:
    cards_html += f"""
    <div class="card">
        <div class="score-badge">{item['score_num']}</div>
        <a class="title" href="{item['link']}" target="_blank">{item['title']}</a>
        <div class="meta">
            <span>{item['score_text']}</span>
            <span>作者：{item['author']}</span>
            <span>{item['comments']}</span>
        </div>
    </div>
    """

if not cards_html:
    cards_html = '<div class="empty">今天没有匹配关键词的热点。</div>'

html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>今日 AI 热点</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            margin: 0;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        h1 {{
            font-size: 36px;
            margin-bottom: 10px;
        }}
        .sub {{
            color: #94a3b8;
            margin-bottom: 30px;
        }}
        .card {{
            position: relative;
            background: #1e293b;
            border-radius: 16px;
            padding: 20px 20px 20px 72px;
            margin-bottom: 16px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.25);
        }}
        .score-badge {{
            position: absolute;
            left: 20px;
            top: 20px;
            width: 38px;
            height: 38px;
            border-radius: 999px;
            background: #38bdf8;
            color: #0f172a;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .title {{
            color: #7dd3fc;
            text-decoration: none;
            font-size: 20px;
            font-weight: 600;
            line-height: 1.5;
            display: block;
            margin-bottom: 10px;
        }}
        .title:hover {{
            text-decoration: underline;
        }}
        .meta {{
            color: #cbd5e1;
            font-size: 14px;
            display: flex;
            gap: 18px;
            flex-wrap: wrap;
        }}
        .empty {{
            background: #1e293b;
            border-radius: 16px;
            padding: 20px;
            color: #cbd5e1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>今日 AI 热点</h1>
        <div class="sub">按分数排序 ｜ 数据来源：Hacker News ｜ 生成时间：{now}</div>
        {cards_html}
    </div>
</body>
</html>
"""

with open("ai_hotspots.html", "w", encoding="utf-8") as f:
    f.write(html)

print("已生成网页文件：ai_hotspots.html")
print(f"共找到 {len(results)} 条 AI 相关热点（已按分数排序）")