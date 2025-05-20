#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

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

# --- 5) 문장 출력 및 상위 5개 링크 (없으면 중립 후기로 대체) ---
def print_results(posts, positive, negative, neutral):
    total     = len(posts)
    pos_count = len(positive)
    neg_count = len(negative)
    neu_count = len(neutral)

    # 문장 형태로 통계 출력
    print(f"전체 후기 수는 {total}개입니다.")
    print(f"긍정 후기 수는 {pos_count}개입니다.")
    print(f"부정 후기 수는 {neg_count}개입니다.")
    print(f"중립 후기 수는 {neu_count}개입니다.\n")

    # 긍정 후기 상위 5개 (없으면 중립으로 대체)
    print("=== 긍정 후기 상위 5개 ===")
    if positive:
        selected = positive
    else:
        print("긍정 후기가 없어 중립 후기를 대신 보여드립니다.")
        selected = neutral

    for i, p in enumerate(selected[:5], 1):
        print(f"{i}. {p['date']} | {p['title']}")
        print(f"   {p['link']}")
    print()

    # 부정 후기 상위 5개 (없으면 중립으로 대체)
    print("=== 부정 후기 상위 5개 ===")
    if negative:
        selected = negative
    else:
        print("부정 후기가 없어 중립 후기를 대신 보여드립니다.")
        selected = neutral

    for i, p in enumerate(selected[:5], 1):
        print(f"{i}. {p['date']} | {p['title']}")
        print(f"   {p['link']}")
    print()

def main():
    print("=== 네이버 블로그 감성분석 ===")
    while True:
        query = input("검색어를 입력하세요 (종료: 빈 입력 후 엔터): ").strip()
        if not query:
            print("프로그램을 종료합니다.")
            break

        url   = build_search_url(query)
        html  = fetch_html(url)
        posts = parse_posts(html)
        pos, neg, neu = split_by_sentiment(posts)
        print_results(posts, pos, neg, neu)

if __name__ == "__main__":
    main()
