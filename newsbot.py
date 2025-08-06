#!/usr/bin/env python3
import requests
import feedparser
from datetime import datetime
import os

# --- CONFIGURATION ---
API_KEY = "YOUR_NEWSAPI_KEY"            # TheNewsAPI.com free key
RSS_FEEDS = ["http://feeds.bbci.co.uk/sport/rss.xml"]
SITE_DIR = os.path.join(os.path.dirname(__file__), 'site')
INDEX_PATH = os.path.join(SITE_DIR, 'index.html')
ARTICLES_DIV_ID = 'articles'

# --- FUNCTIONS ---
def fetch_newsapi_sports(limit=5):
    url = "https://api.thenewsapi.com/v1/news/top"
    params = {"api_token": API_KEY, "locale": "en", "categories": "sports", "limit": limit}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json().get('data', [])
    return [{'title': a['title'], 'desc': a['description'], 'url': a['url'], 'source': a['source'] if 'source' in a else 'NewsAPI'} for a in data]


def fetch_rss(limit=5):
    items = []
    for feed in RSS_FEEDS:
        d = feedparser.parse(feed)
        for entry in d.entries[:limit]:
            items.append({'title': entry.title, 'desc': getattr(entry, 'summary', ''), 'url': entry.link, 'source': d.feed.get('title', 'RSS')})
    return items


def summarize(text, max_sentences=3):
    sents = text.replace('\n',' ').split('. ')
    return '. '.join(sents[:max_sentences]).strip()


def build_articles_html(articles):
    html = ''
    for art in articles:
        summary = summarize(art['desc'])
        html += f"<article>"
        html += f"<h2><a href='{art['url']}'>{art['title']}</a></h2>"
        html += f"<p>{summary}</p>"
        html += f"<div class='source'>Source: {art['source']}</div>"
        html += "</article>"
    return html


def inject_articles(html_content, articles_html):
    start = html_content.find(f'<div id="{ARTICLES_DIV_ID}"')
    insert_pos = html_content.find('>', start) + 1
    end_div = html_content.find('</div>', insert_pos)
    new_content = html_content[:insert_pos] + '\n' + articles_html + '\n' + html_content[end_div:]
    return new_content


# --- MAIN ---
if __name__ == '__main__':
    # Fetch and merge
    news = fetch_newsapi_sports() + fetch_rss()

    # Read index.html
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # Build and inject
    articles_html = build_articles_html(news)
    updated = inject_articles(html, articles_html)

    # Write back
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(updated)

    print(f"[{datetime.now().isoformat()}] Updated {len(news)} articles.")
