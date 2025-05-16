import os
import requests
import urllib.parse
from django.conf import settings
from django.shortcuts import render

def blog_search(request):
    keyword = request.GET.get('q', '').strip()
    # 현재 페이지, 1~5 사이로 클램핑
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    page = max(1, min(page, 5))

    results, error = [], None
    total_results = 0

    if keyword:
        display = 10
        start = (page - 1) * display + 1
        encoded = urllib.parse.quote(keyword)
        url = (
            f"https://openapi.naver.com/v1/search/blog"
            f"?query={encoded}&display={display}&start={start}&sort=sim"
        )

        key_path = os.path.join(settings.BASE_DIR, 'key_client.txt')
        with open(key_path, 'r', encoding='utf-8') as f:
            client_id = f.readline().strip()
            client_secret = f.readline().strip()

        headers = {
            'X-Naver-Client-Id': client_id,
            'X-Naver-Client-Secret': client_secret,
        }
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('items', [])
            total_results = data.get('total', 0)
        else:
            error = resp.text

    # 총 페이지 수 (최대 5)
    total_pages = min((total_results + 9) // 10, 5) if total_results else 0
    pages = list(range(1, total_pages + 1))

    return render(request, 'travel_input/blog_search.html', {
        'keyword': keyword,
        'results': results,
        'error': error,
        'page': page,
        'pages': pages,
    })
