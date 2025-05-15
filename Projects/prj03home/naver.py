import requests
import urllib.parse

# 🔑 파일에서 API 키 정보 불러오기
with open('key_client.txt', 'r') as file:
    client_id = file.readline().strip()
    client_secret = file.readline().strip()



# 검색할 키워드
keyword = '부동산 투자'
encoded_keyword = urllib.parse.quote(keyword)


# 검색 요청 URL
url = f"https://openapi.naver.com/v1/search/blog?query={encoded_keyword}&display=10&start=1&sort=sim"

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
    for idx, item in enumerate(data['items'], 1):
        print(f"[{idx}] 제목: {item['title']}")
        print(f"    블로그명: {item['bloggername']}")
        print(f"    링크: {item['link']}")
        print(f"    요약: {item['description']}")
        print()
else:
    print(f"요청 실패: {response.status_code}")
    print(response.text)