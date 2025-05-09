from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..forms import TravelSurveyForm
import pandas as pd
import os
from django.conf import settings
from .utils import summarize_text_with_openai


def home(request):
    return render(request, 'travel_input/home.html')


def travel_survey(request):
    culture = {
        'name': '한국의 전통 문화',
        'description': '한국의 문화와 역사, 전통을 살펴보세요.',
        'important_places': ['경복궁', '창덕궁', '한옥마을']
    }
    if request.method == 'POST':
        form = TravelSurveyForm(request.POST)
        if form.is_valid():
            return render(request, 'travel_input/thank_you.html')
    else:
        form = TravelSurveyForm()
    return render(request, 'travel_input/travel_list.html', {'form': form, 'culture': culture})


def culture(request):
    csv_path = os.path.join(settings.BASE_DIR, '전체관광지_최종분류.csv')
    try:
        df = pd.read_csv(csv_path)
        recommendations = df.sample(3).to_dict('records')
        for rec in recommendations:
            desc = rec.get('설명', '')
            if desc:
                rec['설명_3줄요약'] = summarize_text_with_openai(desc)
            else:
                rec['설명_3줄요약'] = ''
    except Exception as e:
        recommendations = []
    culture_info = {
        'name': '한국의 전통 문화',
        'description': '한국의 전통적인 문화와 역사적 장소들을 소개합니다.',
        'important_places': ['경복궁', '창덕궁', '한옥마을', '국립중앙박물관', '인사동'],
        'festivals': ['설날', '추석', '단오', '정월대보름'],
        'traditional_food': ['김치', '비빔밥', '불고기', '한정식'],
        'activities': ['한복체험', '전통공예', 'templestay', '전통음악공연']
    }
    return render(request, 'travel_input/culture.html', {'culture': culture_info, 'recommendations': recommendations})


def lodging(request):
    lodging_info = {
        'categories': [
            {
                'name': '호텔',
                'description': '럭셔리한 숙박과 최상의 서비스',
                'options': ['그랜드 하얏트', '롯데호텔', '웨스틴조선'],
                'price_range': '200,000원 ~ 500,000원'
            },
            {
                'name': '한옥스테이',
                'description': '전통 한옥에서 즐기는 특별한 경험',
                'options': ['북촌 한옥마을', '전주 한옥마을', '경주 한옥호텔'],
                'price_range': '100,000원 ~ 300,000원'
            },
            {
                'name': '게스트하우스',
                'description': '현지인과 교류하며 즐기는 경제적인 숙박',
                'options': ['홍대 게스트하우스', '부산 해변 게스트하우스'],
                'price_range': '20,000원 ~ 50,000원'
            }
        ],
        'popular_areas': ['명동', '홍대', '강남', '부산 해운대', '제주 서귀포'],
        'booking_tips': [
            '성수기에는 최소 1달 전 예약 권장',
            '주요 관광지와의 접근성 고려',
            '후기 꼼꼼히 확인하기',
            '추가 요금 사항 체크하기'
        ]
    }
    return render(request, 'travel_input/lodging.html', {'lodging': lodging_info})


def smart_schedule(request):
    return render(request, 'travel_input/smart_schedule.html')


def recommendations(request):
    csv_path = os.path.join(settings.BASE_DIR, '전체관광지_최종분류.csv')
    try:
        df = pd.read_csv(csv_path)
        region = request.GET.get('region')
        category = request.GET.get('category')
        filtered = df
        if region:
            filtered = filtered[filtered['광역지역'].str.contains(region, na=False)]
        if category:
            filtered = filtered[filtered['분류'].str.contains(category, na=False)]
        place_list = filtered.head(10).to_dict('records')
        for place in place_list:
            desc = place.get('설명', '')
            if desc:
                place['설명_3줄요약'] = summarize_text_with_openai(desc)
            else:
                place['설명_3줄요약'] = ''
        if len(filtered) >= 3:
            random_recommend = filtered.sample(3).to_dict('records')
        else:
            random_recommend = filtered.to_dict('records')
    except Exception as e:
        place_list = []
        random_recommend = []
    return render(request, 'travel_input/recommendations.html', {
        'place_list': place_list,
        'random_recommend': random_recommend,
    })


@login_required
def generate_dummy_view(request):
    return render(request, 'travel_input/generate_dummy.html')
