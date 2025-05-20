import os
import django
import requests
from bs4 import BeautifulSoup

# Django 환경 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prj03S.settings")
django.setup()

from home.models import Comment, Destination

def crawl_and_save():
    # Destination이 하나 이상 있어야 함
    destination = Destination.objects.first()
    if not destination:
        print("Destination 데이터가 없습니다. 먼저 생성해주세요.")
        return

    url = "https://travel.naver.com/region/100000000"  # 실제 후기 URL로 바꾸기
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    reviews = soup.find_all("div", class_="review_text")

    for review in reviews:
        content = review.get_text(strip=True)
        Comment.objects.create(
            user=None,
            destination=destination,
            content=content,
            sentiment=""
        )
        print(f"저장 완료: {content[:30]}...")

if __name__ == "__main__":
    crawl_and_save()
