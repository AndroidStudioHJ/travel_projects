from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import json

from openai import OpenAI  # openai>=1.0.0 방식

from travel_input.forms import AITravelConsultForm
from ..models import Schedule, Budget
from .utils import summarize_text_with_openai

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@login_required
def travel_ai_consult(request):
    """
    AI 맞춤 여행 일정 상담 뷰
    """
    result = None
    if request.method == "POST":
        form = AITravelConsultForm(request.POST)
        if form.is_valid():
            prompt = generate_prompt(form.cleaned_data)

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
            )
            result = response.choices[0].message.content
    else:
        form = AITravelConsultForm()

    return render(request, 'travel_input/ai_consult.html', {'form': form, 'result': result})


def generate_prompt(data):
    """
    여행 일정 생성을 위한 프롬프트 생성
    """
    return f"""
여행 일정을 계획하려고 해요. 아래 정보를 참고해서 맞춤 일정을 제안해주세요:

- 목적지: {data['destination']}
- 여행 기간: {data['duration']}
- 출발지: {data['departure']}
- 동행자: {data['companions']}
- 여행 시기: {data['date']}
- 테마: {data['theme']}
- 여행 스타일: {data['style']}

이 정보를 바탕으로 날짜별 여행 일정을 추천해 주세요. 활동 추천도 포함해 주세요. 
그리고 이에 해당하는 검색 키워드를 추가해 주세요.
"""


@csrf_exempt
@login_required
def ai_budget_view(request):
    """
    AI 예산 분배 API
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            total_budget = data.get('total_budget', 0)
            categories = ['숙박', '식비', '교통', '관광']

            if not settings.OPENAI_API_KEY:
                return JsonResponse({'error': 'OpenAI API 키가 설정되지 않았습니다.'}, status=400)

            prompt = f"""
한국 여행 예산을 다음 네 가지 카테고리로 합리적으로 분배해줘.
- 총 예산: {total_budget:,}원
- 카테고리: 숙박, 식비, 교통, 관광

각 카테고리별로 얼마씩 배정할지 JSON 형식으로 알려줘.
예시: {{"숙박": 100000, "식비": 80000, "교통": 60000, "관광": 60000}}

다음 사항을 고려해줘:
1. 숙박은 전체 예산의 30-40% 정도로 배정
2. 식비는 전체 예산의 20-30% 정도로 배정
3. 교통은 전체 예산의 15-25% 정도로 배정
4. 관광은 전체 예산의 15-25% 정도로 배정
5. 모든 카테고리의 합이 총 예산과 정확히 일치해야 함
"""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 여행 예산 전문가입니다. 주어진 예산을 카테고리별로 합리적으로 분배해주세요. 반드시 JSON 형식으로만 응답해주세요."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            # 누락된 카테고리 확인
            for category in categories:
                if category not in result:
                    return JsonResponse({'error': f'필수 카테고리 {category}가 누락되었습니다.'}, status=500)

            # 예산 합계 맞추기
            total_allocated = sum(result.values())
            if total_allocated != total_budget:
                diff = total_budget - total_allocated
                result['숙박'] += diff  # 숙박에 조정분 반영

            # 최신 스케줄에 예산 저장
            schedule = Schedule.objects.filter(user=request.user).order_by('-created_at').first()
            if not schedule:
                schedule = Schedule.objects.create(
                    title='예산 계획',
                    destination='',
                    start_date=None,
                    end_date=None,
                    budget=total_budget,
                    user=request.user
                )
            else:
                schedule.budget = total_budget
                schedule.save()

            for category, amount in result.items():
                budget_obj, created = Budget.objects.get_or_create(
                    schedule=schedule,
                    category=category,
                    defaults={'amount': amount}
                )
                if not created:
                    budget_obj.amount = amount
                    budget_obj.save()

            return JsonResponse(result)

        except Exception as e:
            return JsonResponse({'error': f'AI 예산 분배 중 오류가 발생했습니다: {str(e)}'}, status=500)

    return JsonResponse({'error': 'POST 요청만 지원합니다.'}, status=405)


@csrf_exempt
@login_required
def ai_recommend_view(request):
    """
    AI 추천 장소 API (단순 예시)
    """
    if request.method == 'POST':
        return JsonResponse({
            "추천장소": [
                "경복궁",
                "남산타워",
                "광화문광장",
                "북촌한옥마을",
                "한강공원"
            ]
        })
    return JsonResponse({'error': 'POST 요청만 지원합니다.'}, status=405)


@csrf_exempt
def ai_summarize_view(request):
    """
    AI 텍스트 요약 API
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            if not text:
                return JsonResponse({'error': '요약할 텍스트가 없습니다.'}, status=400)

            summary = summarize_text_with_openai(text)
            return JsonResponse({'summary': summary})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'POST 요청만 지원합니다.'}, status=405)
