from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
import os
from openai import OpenAI
from ..models import Schedule, Budget
from .utils import summarize_text_with_openai

@csrf_exempt
@login_required
def ai_budget_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        total_budget = data.get('total_budget', 0)
        categories = ['숙박', '식비', '교통', '관광']
        
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
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
        
        try:
            client = OpenAI(api_key=openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 여행 예산 전문가입니다. 주어진 예산을 카테고리별로 합리적으로 분배해주세요. 반드시 JSON 형식으로만 응답해주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={ "type": "json_object" }
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            required_categories = ['숙박', '식비', '교통', '관광']
            for category in required_categories:
                if category not in result:
                    return JsonResponse({'error': f'필수 카테고리 {category}가 누락되었습니다.'}, status=500)
            
            total_allocated = sum(result.values())
            if total_allocated != total_budget:
                diff = total_budget - total_allocated
                result['숙박'] += diff
            
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