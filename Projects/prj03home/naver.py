import requests
import urllib.parse
from datetime import datetime

def search_naver_blog(keyword):
    """
    네이버 블로그 검색 API 호출
    """
    # 🔑 파일에서 API 키 정보 불러오기
    with open('key_client.txt', 'r') as file:
        client_id = file.readline().strip()
        client_secret = file.readline().strip()

    # 검색 키워드 인코딩
    encoded_keyword = urllib.parse.quote(keyword)

    # 검색 요청 URL
    url = f"https://openapi.naver.com/v1/search/blog?query={encoded_keyword}&display=10&start=1&sort=date"

    # 요청 헤더 설정
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

    # API 요청
    response = requests.get(url, headers=headers)

    # 응답 확인
    if response.status_code == 200:
        data = response.json()
        return data['items']
    return []

def save_results_to_html(results, keyword):
    """
    검색 결과를 HTML 파일로 저장
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>AI 관련 블로그 검색 결과</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .result {{ margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; }}
            .title {{ color: #1a0dab; font-size: 18px; }}
            .blogger {{ color: #006621; }}
            .date {{ color: #666; }}
        </style>
    </head>
    <body>
        <h1>'{keyword}' 검색 결과</h1>
    """
    
    for idx, item in enumerate(results, 1):
        html_content += f"""
        <div class="result">
            <div class="title">{idx}. {item['title']}</div>
            <div class="blogger">블로거: {item['bloggername']}</div>
            <div class="date">작성일: {item['postdate']}</div>
            <div><a href="{item['link']}" target="_blank">링크</a></div>
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    # 현재 시간을 파일명에 포함
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"search_results_{timestamp}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filename

if __name__ == "__main__":
    # AI 관련 키워드 리스트
    ai_keywords = [
        "인공지능",
        "머신러닝",
        "딥러닝",
        "AI 기술",
        "인공지능 개발"
    ]
    
    # 각 키워드로 검색 실행
    for keyword in ai_keywords:
        print(f"\n'{keyword}' 검색 중...")
        results = search_naver_blog(keyword)
        
        if results:
            filename = save_results_to_html(results, keyword)
            print(f"검색 결과가 {filename} 파일에 저장되었습니다.")
        else:
            print("검색 결과가 없습니다.")