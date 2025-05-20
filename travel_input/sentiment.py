#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup

# --- 1) 검색 URL 생성 ---
def build_search_url(query: str) -> str:
    """
    네이버 블로그 검색 API URL 생성
    """
    encoded_query = urllib.parse.quote(query)
    return f"https://openapi.naver.com/v1/search/blog?query={encoded_query}&display=100&start=1&sort=date"

# --- 2) HTML 가져오기 ---
def fetch_html(url: str) -> dict:
    """
    네이버 블로그 검색 API 호출
    """
    # 🔑 파일에서 API 키 정보 불러오기
    try:
        with open('key_client.txt', 'r') as file:
            client_id = file.readline().strip()
            client_secret = file.readline().strip()
    except FileNotFoundError:
        print("Warning: key_client.txt not found. Using default keys.")
        client_id = "YOUR_CLIENT_ID"  # 실제 사용시 API 키로 교체 필요
        client_secret = "YOUR_CLIENT_SECRET"  # 실제 사용시 API 키로 교체 필요

    # 요청 헤더 설정
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

    # API 요청
    response = requests.get(url, headers=headers)
    
    # 응답 확인
    if response.status_code == 200:
        return response.json()
    return {"items": []}

# --- 3) 블로그 포스트 파싱 ---
def parse_posts(data: dict) -> list:
    """
    API 응답에서 블로그 포스트 정보 추출
    """
    posts = []
    for item in data.get('items', []):
        post = {
            'title': item['title'].replace('<b>', '').replace('</b>', ''),
            'link': item['link'],
            'blogger': item['bloggername'],
            'date': item['postdate'],
            'summary': item['description'].replace('<b>', '').replace('</b>', '')
        }
        posts.append(post)
    return posts

# --- 4) 감성 분석으로 분류 ---
def split_by_sentiment(posts: list) -> tuple:
    """
    감성 분석으로 포스트 분류
    """
    positive = []
    negative = []
    neutral = []
    
    # 긍정/부정 키워드
    positive_words = ['좋', '최고', '추천', '행복', '만족', '감동', '완벽', '최고', '최상', '최고급']
    negative_words = ['별로', '실망', '불만', '최악', '비추천', '별점', '낮', '부족', '불편', '문제']
    
    for post in posts:
        text = post['title'] + ' ' + post['summary']
        text = text.lower()
        
        # 긍정/부정 단어 카운트
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        if pos_count > neg_count:
            positive.append(post)
        elif neg_count > pos_count:
            negative.append(post)
        else:
            neutral.append(post)
    
    return positive, negative, neutral 