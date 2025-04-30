from django.shortcuts import render, redirect, get_object_or_404
from .forms import TravelSurveyForm, ScheduleForm 
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Schedule, Destination, GroupTravel, GroupMember, GroupMessage, Budget
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
import os
from django.views.decorators.csrf import csrf_exempt
from langchain_openai import ChatOpenAI
from django.conf import settings
import pandas as pd
import openai  # OpenAI API 사용을 위한 import

def home(request):
    return render(request, 'travel_input/home.html')

# 여행 설문 뷰
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

def summarize_text_with_openai(text):
    """
    OpenAI API를 사용해 입력 텍스트를 한국어로 3줄로 요약합니다.
    환경변수 OPENAI_API_KEY 필요.
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return 'OpenAI API 키가 설정되어 있지 않습니다.'
    openai.api_key = api_key
    prompt = (
        "아래 내용을 한국어로 3줄로 요약해줘. "
        "각 줄은 줄바꿈(\\n)으로 구분해서 출력해줘. "
        "반드시 3줄로 만들어줘.\n"
        f"{text}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.5,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"요약 실패: {e}"

# 문화 정보 뷰
def culture(request):
    # CSV 경로
    csv_path = os.path.join(settings.BASE_DIR, '전체관광지_최종분류.csv')
    try:
        df = pd.read_csv(csv_path)
        # 랜덤 3개 추천
        recommendations = df.sample(3).to_dict('records')
        # 각 추천 설명을 3줄 요약
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
    import os
    from django.conf import settings
    csv_path = os.path.join(settings.BASE_DIR, '전체관광지_최종분류.csv')
    try:
        df = pd.read_csv(csv_path)
        # 필터: GET 파라미터(region, category)로 필터링
        region = request.GET.get('region')
        category = request.GET.get('category')
        filtered = df
        if region:
            filtered = filtered[filtered['광역지역'].str.contains(region, na=False)]
        if category:
            filtered = filtered[filtered['분류'].str.contains(category, na=False)]
        # 최대 10개만 요약
        place_list = filtered.head(10).to_dict('records')
        for place in place_list:
            desc = place.get('설명', '')
            if desc:
                place['설명_3줄요약'] = summarize_text_with_openai(desc)
            else:
                place['설명_3줄요약'] = ''
        # 랜덤 3개 추천
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
def budget_planning(request):
    schedule = Schedule.objects.filter(user=request.user).order_by('-created_at').first()
    categories = ['숙박', '식비', '교통', '관광']
    budgets = {cat: 0 for cat in categories}
    percents = {cat: 0 for cat in categories}
    total_budget = 0
    if schedule:
        total_budget = schedule.budget or 0
        for b in Budget.objects.filter(schedule=schedule):
            budgets[b.category] = b.amount
    if request.method == 'POST':
        total_budget = int(request.POST.get('total_budget', 0))
        if not schedule:
            # 일정이 없으면 새로 생성
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
        for cat in categories:
            amount_str = request.POST.get(cat, '0')
            try:
                amount = int(amount_str) if amount_str else 0
            except ValueError:
                amount = 0
            budget_obj, created = Budget.objects.get_or_create(
                schedule=schedule,
                category=cat,
                defaults={'amount': amount}
            )
            if not created:
                budget_obj.amount = amount
                budget_obj.save()
        allocated = sum(budgets[cat] for cat in categories)
        remaining = total_budget - allocated
        return redirect('travel_input:budget_planning')
    # 카테고리별 비율 계산
    if total_budget > 0:
        for cat in categories:
            try:
                percents[cat] = int(budgets[cat] / total_budget * 100)
            except Exception:
                percents[cat] = 0
    allocated = sum(budgets[cat] for cat in categories)
    remaining = total_budget - allocated
    return render(request, 'travel_input/budget_planning.html', {
        'total_budget': total_budget,
        'budgets': budgets,
        'categories': categories,
        'percents': percents,
        'allocated': allocated,
        'remaining': remaining,
    })

def group_travel(request):
    return render(request, 'travel_input/group_travel.html')

class ScheduleView(TemplateView): 
    template_name = 'travel_input/schedule_form.html'

class LodgingView(TemplateView): 
    template_name = 'travel_input/lodging.html'

# 일정 CRUD 뷰
@login_required
def schedule_list(request):
    schedules = Schedule.objects.filter(user=request.user)
    return render(request, 'travel_input/schedule_list.html', {'schedules': schedules})

@login_required
def schedule_detail(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    return render(request, 'travel_input/schedule_detail.html', {'schedule': schedule})

@login_required
def schedule_create(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = request.user
            
            # 여행 스타일을 문자열로 변환하여 저장
            travel_styles = form.cleaned_data.get('travel_style', [])
            num_people = form.cleaned_data.get('num_people', 1)
            budget = form.cleaned_data.get('budget', 0)
            
            if travel_styles:
                schedule.notes = f"""선호 여행 스타일: {', '.join(travel_styles)}
여행 인원수: {num_people}명
예산: {budget:,}원

"""
            
            schedule.save()
            
            # 더미 AI 응답 생성
            try:
                # 목적지와 여행 스타일에 따른 더미 응답 선택
                destination = schedule.destination.lower()
                travel_style = travel_styles[0] if travel_styles else 'culture'
                
                # 예산에 따른 추천 추가
                budget_level = "고급" if budget >= 1000000 else "중급" if budget >= 500000 else "저렴"
                
                dummy_responses = {
                    "서울": {
                        "nature": f"""
1. 북한산과 남산
   - 북한산 등반
   - 남산 공원 산책
   - 서울 전망대 방문
   - 예상 비용: {budget_level} 레벨에 맞는 활동

2. 한강 공원
   - 자전거 대여
   - 피크닉
   - 야경 감상
   - {num_people}명이 함께 즐길 수 있는 활동

3. 서울숲과 올림픽공원
   - 자연 산책
   - 사진 촬영
   - 휴식
   - 총 예산 {budget:,}원 내에서 즐길 수 있는 활동
""",
                        "city": f"""
1. 명동과 홍대
   - 쇼핑
   - 카페 투어
   - 스트리트 푸드
   - {num_people}명이 함께 즐길 수 있는 장소

2. 강남과 이태원
   - 쇼핑몰 방문
   - 레스토랑 체험
   - 나이트라이프
   - 예상 비용: {budget_level} 레벨에 맞는 장소

3. 동대문과 인사동
   - 전통 시장
   - 공예품 쇼핑
   - 전통 음식
   - 총 예산 {budget:,}원 내에서 즐길 수 있는 장소
""",
                        "culture": f"""
1. 경복궁과 북촌한옥마을
   - 전통 한복 체험
   - 한옥 카페
   - 전통 공예 체험
   - {num_people}명이 함께 즐길 수 있는 체험

2. 국립중앙박물관
   - 한국 역사 체험
   - 전통 문화 전시
   - 문화 공연
   - 예상 비용: {budget_level} 레벨에 맞는 체험

3. 남대문시장과 광장시장
   - 전통 시장 체험
   - 전통 음식 시식
   - 전통 공예품
   - 총 예산 {budget:,}원 내에서 즐길 수 있는 체험
"""
                    },
                    "부산": {
                        "nature": """
1. 해운대와 광안리
   - 해변 산책
   - 해수욕
   - 야경 감상

2. 태종대와 오륙도
   - 해안 절경
   - 등산로
   - 전망대

3. 금정산
   - 등산
   - 자연 탐방
   - 휴식
""",
                        "city": """
1. 해운대와 광안리
   - 쇼핑몰
   - 레스토랑
   - 나이트라이프

2. 서면과 남포동
   - 쇼핑
   - 카페
   - 스트리트 푸드

3. 센텀시티
   - 쇼핑몰
   - 영화관
   - 레스토랑
""",
                        "culture": """
1. 감천문화마을
   - 전통 마을 탐방
   - 공예 체험
   - 전통 음식

2. 자갈치시장과 국제시장
   - 전통 시장 체험
   - 해산물 시식
   - 전통 공예품

3. 부산타워와 용두산공원
   - 전통 공원
   - 전망대
   - 문화 공연
"""
                    },
                    "제주": {
                        "nature": """
1. 한라산과 오름
   - 등산
   - 자연 탐방
   - 전망대

2. 성산일출봉과 우도
   - 일출 감상
   - 자전거 투어
   - 해변 산책

3. 협재와 금능해수욕장
   - 해수욕
   - 스노클링
   - 휴식
""",
                        "city": """
1. 제주시와 서귀포
   - 쇼핑몰
   - 레스토랑
   - 카페

2. 중문관광단지
   - 테마파크
   - 쇼핑
   - 레스토랑

3. 제주올레
   - 카페
   - 레스토랑
   - 쇼핑
""",
                        "culture": """
1. 성읍민속마을
   - 전통 마을 탐방
   - 전통 체험
   - 전통 음식

2. 제주민속촌
   - 전통 문화 체험
   - 전통 공예
   - 전통 공연

3. 해녀박물관
   - 해녀 문화 체험
   - 전통 공예
   - 전통 음식
"""
                    }
                }
                
                # 목적지에 따른 더미 응답 선택
                if "서울" in destination:
                    response = dummy_responses["서울"].get(travel_style, dummy_responses["서울"]["culture"])
                elif "부산" in destination:
                    response = dummy_responses["부산"].get(travel_style, dummy_responses["부산"]["culture"])
                elif "제주" in destination:
                    response = dummy_responses["제주"].get(travel_style, dummy_responses["제주"]["culture"])
                else:
                    response = f"""
1. 주요 관광지 방문
   - 지역 대표 명소 탐방
   - 전통 문화 체험
   - 현지 음식 시식
   - {num_people}명이 함께 즐길 수 있는 활동

2. 자연 경관 감상
   - 산책로 트레킹
   - 전망대 방문
   - 공원에서 휴식
   - 예상 비용: {budget_level} 레벨에 맞는 활동

3. 쇼핑과 휴식
   - 전통 시장 방문
   - 특산품 쇼핑
   - 카페에서 휴식
   - 총 예산 {budget:,}원 내에서 즐길 수 있는 활동
"""
                
                schedule.notes += f"\nAI 여행 추천:\n{response}"
                schedule.save()
                
                messages.success(request, 'AI가 여행 계획을 추천했습니다.')
            except Exception as e:
                messages.warning(request, 'AI 응답 생성 중 오류가 발생했습니다.')
            
            return redirect('travel_input:schedule_detail', pk=schedule.pk)
    else:
        form = ScheduleForm()
    
    return render(request, 'travel_input/schedule_form.html', {'form': form})

@login_required
def schedule_update(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            schedule = form.save()
            messages.success(request, '일정이 성공적으로 수정되었습니다.')
            return redirect('travel_input:schedule_detail', pk=schedule.pk)
    else:
        form = ScheduleForm(instance=schedule)
    return render(request, 'travel_input/schedule_form.html', {'form': form})

@login_required
def schedule_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, '일정이 성공적으로 삭제되었습니다.')
        return redirect('travel_input:schedule_list')
    return render(request, 'travel_input/schedule_confirm_delete.html', {'schedule': schedule})

@login_required
def confirm_delete_all(request):
    if request.method == 'POST':
        Schedule.objects.filter(user=request.user).delete()
        messages.success(request, '모든 일정이 성공적으로 삭제되었습니다.')
        return redirect('travel_input:schedule_list')
    return render(request, 'travel_input/confirm_delete_all.html')

class GroupTravelListView(LoginRequiredMixin, ListView):
    model = GroupTravel
    template_name = 'travel_input/group_travel_list.html'
    context_object_name = 'groups'

    def get_queryset(self):
        return GroupTravel.objects.filter(members=self.request.user)

class GroupTravelDetailView(LoginRequiredMixin, DetailView):
    model = GroupTravel
    template_name = 'travel_input/group_travel_detail.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = GroupMessage.objects.filter(group=self.object).order_by('created_at')
        context['is_admin'] = self.object.created_by == self.request.user
        return context

class GroupTravelCreateView(LoginRequiredMixin, CreateView):
    model = GroupTravel
    template_name = 'travel_input/group_travel_form.html'
    fields = ['name', 'description', 'schedule']
    success_url = reverse_lazy('travel_input:group_travel_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_schedules'] = Schedule.objects.filter(user=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        GroupMember.objects.create(group=form.instance, user=self.request.user, is_admin=True)
        return response

class GroupTravelUpdateView(LoginRequiredMixin, UpdateView):
    model = GroupTravel
    template_name = 'travel_input/group_travel_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('travel_input:group_travel_list')

    def get_queryset(self):
        return GroupTravel.objects.filter(created_by=self.request.user)

class GroupTravelDeleteView(LoginRequiredMixin, DeleteView):
    model = GroupTravel
    success_url = reverse_lazy('travel_input:group_travel_list')

    def get_queryset(self):
        return GroupTravel.objects.filter(created_by=self.request.user)

@login_required
def join_group(request, pk):
    group = get_object_or_404(GroupTravel, pk=pk)
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        GroupMember.objects.create(group=group, user=request.user)
    return redirect('travel_input:group_travel_detail', pk=pk)

@login_required
def leave_group(request, pk):
    group = get_object_or_404(GroupTravel, pk=pk)
    GroupMember.objects.filter(group=group, user=request.user).delete()
    return redirect('travel_input:group_travel_list')

@login_required
def send_message(request, pk):
    if request.method == 'POST':
        group = get_object_or_404(GroupTravel, pk=pk)
        content = request.POST.get('content')
        if content:
            GroupMessage.objects.create(
                group=group,
                user=request.user,
                content=content
            )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required
def ai_budget_view(request):
    if request.method == 'POST':
        if settings.DEBUG:
            # 개발/테스트 환경에서는 더미 데이터 반환 (OpenAI 호출 X)
            return JsonResponse({"숙박": 100000, "식비": 80000, "교통": 60000, "관광": 60000})
        import json
        data = json.loads(request.body)
        total_budget = data.get('total_budget', 0)
        categories = ['숙박', '식비', '교통', '관광']
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            print('OPENAI_API_KEY 환경변수 없음')
            return JsonResponse({'error': 'OpenAI API 키가 설정되지 않았습니다.'}, status=400)
        prompt = f"""
        한국 여행 예산을 다음 네 가지 카테고리로 합리적으로 분배해줘.
        - 총 예산: {total_budget}원
        - 카테고리: 숙박, 식비, 교통, 관광
        각 카테고리별로 얼마씩 배정할지 JSON 형식으로 알려줘. (예: {{"숙박": 100000, "식비": 80000, ...}})
        """
        try:
            llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0.2)
            response = llm.invoke(prompt)
            print('OpenAI 응답:', response)
            import ast
            json_text = response.content  # content 속성에 실제 JSON 문자열이 있음
            try:
                result = ast.literal_eval(json_text)
                return JsonResponse(result)
            except Exception as e:
                print('JSON 파싱 에러:', e)
                return JsonResponse({'error': 'AI 응답 파싱 실패', 'raw_response': json_text}, status=500)
        except Exception as e:
            print('OpenAI 호출 에러:', e)
            return JsonResponse({'error': f'OpenAI 호출 에러: {e}'}, status=500)
    return JsonResponse({'error': 'POST 요청만 지원합니다.'}, status=405)

@csrf_exempt
@login_required
def ai_recommend_view(request):
    if request.method == 'POST':
        # 샘플 더미 추천 결과 반환
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
    POST로 'text'를 받아 OpenAI로 3줄 요약 후 JSON 반환
    """
    import json
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
