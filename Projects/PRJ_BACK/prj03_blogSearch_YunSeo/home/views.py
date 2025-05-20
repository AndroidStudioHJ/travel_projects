# -*- coding: utf-8 -*-
import urllib.request
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from django.shortcuts import render
import sys
import os

# sentiment.py 파일의 경로를 시스템 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sentiment import build_search_url, fetch_html, parse_posts, split_by_sentiment

# --- 1) 검색 URL 생성 ---
def build_search_url(query: str) -> str:
    base = "https://search.naver.com/search.naver?ssc=tab.blog.all&sm=tab_jum&query="
    return base + quote_plus(query)

# --- 2) HTML 가져오기 ---
def fetch_html(url: str, user_agent: str = None) -> bytes:
    headers = {
        "User-Agent": user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.3"
        )
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as res:
        return res.read()

# --- 3) 포스트 파싱 ---
def parse_posts(html: bytes) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    posts = []
    for item in soup.select("ul.lst_view li.bx"):
        a_title = item.select_one("a.title_link")
        if not a_title:
            continue
        title = a_title.get_text(strip=True)
        link  = a_title["href"]
        a_desc = item.select_one("a.dsc_link")
        summary = a_desc.get_text(strip=True) if a_desc else ""
        span_date = item.select_one("span.sub")
        date = span_date.get_text(strip=True) if span_date else ""
        posts.append({
            "date":    date,
            "title":   title,
            "link":    link,
            "summary": summary
        })
    return posts

# --- 4) 룰 기반 감성 분석 ---
POSITIVE_KEYWORDS = {
    "좋았", "즐거웠", "행복", "추천", "감동", "최고", "멋졌",
    "만족", "기뻤", "유익", "재미있", "편안", "힐링", "환상",
    "대박", "감탄", "사랑했", "인상적", "즐겼", "훌륭했",
    "깔끔", "청결", "안전했", "풍성", "특별했"
}

NEGATIVE_KEYWORDS = {
    "아쉬웠", "불편", "힘들", "실망", "별로", "싫었",
    "짜증", "지루했", "부족", "답답", "고장", "불만",
    "불친절", "버거웠", "어려웠", "곤란했", "후회", "슬펐",
    "혼잡", "위험", "피곤", "비싸"
}

def rule_sentiment(text: str) -> str:
    score = 0
    for w in POSITIVE_KEYWORDS:
        if w in text:
            score += 1
    for w in NEGATIVE_KEYWORDS:
        if w in text:
            score -= 1
    if score > 0:
        return "positive"
    if score < 0:
        return "negative"
    return "neutral"

def split_by_sentiment(posts: list[dict]):
    positive = [p for p in posts if rule_sentiment(p["summary"]) == "positive"]
    negative = [p for p in posts if rule_sentiment(p["summary"]) == "negative"]
    neutral  = [p for p in posts if rule_sentiment(p["summary"]) == "neutral"]
    return positive, negative, neutral

def sentiment_analysis(request):
    query = request.GET.get("q", "")
    view_type = request.GET.get("view", "")  # 전체 보기 타입 (positive, negative, neutral)
    results = None

    if query:
        url = build_search_url(query)
        html = fetch_html(url)
        posts = parse_posts(html)
        positive, negative, neutral = split_by_sentiment(posts)

        # 전체 보기 타입에 따라 표시할 포스트 선택
        if view_type == "positive":
            display_posts = positive
        elif view_type == "negative":
            display_posts = negative
        elif view_type == "neutral":
            display_posts = neutral
        else:
            # 기본적으로 상위 5개씩만 표시
            display_posts = None
            pos_sel = positive[:5] if positive else neutral[:5]
            neg_sel = negative[:5] if negative else neutral[:5]
            neu_sel = neutral[:5]

        results = {
            "total": len(posts),
            "positive_count": len(positive),
            "negative_count": len(negative),
            "neutral_count": len(neutral),
            "positive_list": pos_sel if not view_type else positive,
            "negative_list": neg_sel if not view_type else negative,
            "neutral_list": neu_sel if not view_type else neutral,
            "all_posts": posts,
            "positive_posts": positive,
            "negative_posts": negative,
            "neutral_posts": neutral,
            "view_type": view_type,  # 현재 보기 타입
        }

    return render(request, "sentiment_analysis.html", {
        "query": query,
        "results": results
    })
