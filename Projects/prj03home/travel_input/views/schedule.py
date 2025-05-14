from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import date, timedelta, datetime
import random
from faker import Faker
import openai
from django.conf import settings
import markdown

from travel_input.forms import ScheduleForm
from travel_input.models import Schedule, Destination

STYLE_LABELS = {
    'nature': '자연경관',
    'city': '도시 탐방',
    'culture': '문화 체험',
    'activity': '액티비티',
    'relax': '휴식과 힐링',
}

FACTOR_LABELS = {
    'stay': '숙소',
    'food': '음식',
    'weather': '날씨',
    'schedule': '일정',
    'culture': '문화',
}


@login_required
def schedule_list(request):
    schedules = Schedule.objects.filter(user=request.user).order_by('-created_at')
    # 달력에 넘길 데이터 생성
    schedules_calendar = [
        {
            "id": s.id,
            "title": s.title,
            "start_date": s.start_date.isoformat() if s.start_date else None,
            "end_date": s.end_date.isoformat() if s.end_date else None,
        }
        for s in schedules
        if s.start_date and s.end_date and s.title  # 필수값만
    ]
    return render(
        request,
        'travel_input/schedule_list.html',
        {
            'schedules': schedules,
            'schedules_calendar': schedules_calendar,
        }
    )


@login_required
def schedule_detail(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    
    # 세션에서 AI 답변 가져오기
    ai_answers = request.session.get('ai_answers', [])
    
    # 세션 초기화 요청이 있는 경우
    if request.GET.get('clear_answers'):
        request.session['ai_answers'] = []
        return redirect('travel_input:schedule_detail', pk=pk)

    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        if question:
            # OpenAI API 호출
            openai.api_key = settings.OPENAI_API_KEY
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # 일정의 모든 관련 정보를 포함
            schedule_info = f"""
일정 제목: {schedule.title}
여행 기간: {schedule.start_date} ~ {schedule.end_date}
여행지: {schedule.destination}
참가자 정보: {schedule.participant_info}
연령대: {schedule.age_group}
여행 동행 형태: {schedule.group_type}
방문 장소: {schedule.place_info}
선호 활동: {schedule.preferred_activities}
이벤트/축제 관심: {'있음' if schedule.event_interest else '없음'}
교통 정보: {schedule.transport_info}
이동 관련 요구: {schedule.mobility_needs}
음식 선호: {schedule.meal_preference}
언어 지원: {'필요' if schedule.language_support else '불필요'}
희망 계절: {schedule.season}
재방문 여부: {'재방문' if schedule.repeat_visitor else '첫 방문'}
여행자 보험: {'가입 예정' if schedule.travel_insurance else '미가입'}
추가 메모: {schedule.notes}
"""
            
            prompt = f"""일정 정보:
{schedule_info}

질문: {question}

답변 형식:
1. 답변은 3-5개의 항목으로 구성해주세요.
2. 각 항목은 마크다운 형식으로 작성해주세요:
   ```markdown
   ### [장소/활동 이름]
   
   **방문 정보**
   - 방문 시간: [구체적인 시간대]
   - 소요 시간: [정확한 시간]
   - 추천 이유: [일정의 특성과 연관지어 설명]
   
   **참가자 정보**
   - 연령대: [적합한 연령대]
   - 동행 형태: [추천 동행 형태]
   - 이동 관련: [이동 요구사항 반영]
   
   **음식 정보**
   - 추천 음식점: [지역 특색 음식점]
   - 대표 메뉴:
     * [메뉴1] - [가격]
     * [메뉴2] - [가격]
   - 식사 시간: [추천 시간대]
   - 팁: [예약, 인기 시간대 등]
   
   **추가 정보**
   - 주의사항: [구체적인 팁이나 주의사항]
   - 연락처: [있는 경우]
   - 웹사이트: [있는 경우]
   ```

3. 각 추천은 반드시 다음 정보를 고려해서 작성해주세요:
   - 여행 기간 ({schedule.start_date} ~ {schedule.end_date})
   - 희망 계절 ({schedule.season})
   - 선호 활동 ({schedule.preferred_activities})
   - 이동 관련 요구 ({schedule.mobility_needs})
   - 음식 선호 ({schedule.meal_preference})
   - 언어 지원 필요 여부 ({'필요' if schedule.language_support else '불필요'})

4. 마지막에 "더 궁금한 점이 있으시다면 언제든 물어보세요!"라는 문구로 마무리해주세요."""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"""당신은 여행 일정 전문가입니다. 
다음 정보를 반드시 고려해서 답변해주세요:
- 여행 기간: {schedule.start_date} ~ {schedule.end_date}
- 참가자: {schedule.participant_info} ({schedule.age_group})
- 동행 형태: {schedule.group_type}
- 선호 활동: {schedule.preferred_activities}
- 이동 관련 요구: {schedule.mobility_needs}
- 음식 선호: {schedule.meal_preference}
- 언어 지원: {'필요' if schedule.language_support else '불필요'}

각 추천은 반드시 위 정보를 고려하여 개인화된 답변을 제공해주세요.
특히 음식 관련 정보는 다음을 반드시 포함해주세요:
1. 지역 특색 음식점 위주로 추천
2. 전통 음식과 현대적 해석이 된 음식 모두 포함
3. 식사 시간대별 추천 메뉴
4. 예약이나 방문 시 주의사항
5. 현지인들이 추천하는 숨은 맛집 정보

답변은 반드시 마크다운 형식으로 작성해주세요."""},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
            )
            ai_answer = response.choices[0].message.content
            # 마크다운을 HTML로 변환
            ai_answer_html = markdown.markdown(ai_answer)
            # 답변이 3개 이상이면 가장 오래된 답변 제거
            if len(ai_answers) >= 3:
                ai_answers.pop()
            # 새로운 답변을 리스트 앞에 추가 (HTML로)
            ai_answers.insert(0, ai_answer_html)
            request.session['ai_answers'] = ai_answers

    return render(request, 'travel_input/schedule_detail.html', {
        'schedule': schedule,
        'ai_answers': ai_answers,
    })


@login_required
def schedule_create(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = request.user
            schedule.save()
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
            return redirect('travel_input:schedule_detail', pk=schedule.pk)
    else:
        form = ScheduleForm(instance=schedule)
    return render(request, 'travel_input/schedule_form.html', {'form': form})


@login_required
def schedule_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, '일정이 삭제되었습니다.')
        return redirect('travel_input:schedule_list')
    return render(request, 'travel_input/schedule_confirm_delete.html', {'schedule': schedule})


@login_required
def confirm_delete_all(request):
    if request.method == 'POST':
        Schedule.objects.filter(user=request.user).delete()
        return redirect('travel_input:schedule_list')
    return render(request, 'travel_input/schedule_confirm_delete_all.html')


@login_required
def toggle_favorite(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    schedule.favorite = not schedule.favorite
    schedule.save()
    return redirect('travel_input:schedule_detail', pk=pk)


@login_required
def favorite_schedules(request):
    schedules = Schedule.objects.filter(user=request.user, favorite=True)
    return render(request, 'travel_input/favorite_schedules.html', {'schedules': schedules})


@login_required
def generate_dummy_schedules(request):
    if request.method == 'POST':
        for _ in range(10):
            Schedule.objects.create(
                user=request.user,
                title='기본 더미 일정',
                destination='서울',
                start_date=date.today(),
                end_date=date.today() + timedelta(days=3),
                notes='자동 생성된 기본 일정입니다.',
                num_people=2,
                budget=500000,
                tag='기본',
                lodging_request='도심 호텔',
                people_composition='본인',
                pet_friendly=False,
                travel_style='city',
                important_factors='food'
            )
        messages.success(request, "✅ 일반 더미 일정 10개 생성 완료!")
        return redirect('travel_input:schedule_list')
    return render(request, 'travel_input/generate_dummy.html')


@login_required
def generate_ai_style_schedules(request):
    if request.method == 'POST':
        fake = Faker('ko_KR')
        destinations = ['산속', '제주', '부산', '서울', '강릉', '전주', '속초']

        count = int(request.POST.get('count', 100))

        for _ in range(count):
            start = date.today() + timedelta(days=random.randint(1, 30))
            end = start + timedelta(days=random.randint(2, 5))
            dest_name = random.choice(destinations)
            dest_obj, _ = Destination.objects.get_or_create(name=dest_name)

            Schedule.objects.create(
                user=request.user,
                title=fake.catch_phrase(),
                destination=dest_obj,
                start_date=start,
                end_date=end,
                budget=random.randint(300000, 5000000),
                notes=fake.sentence(),
                participant_info=fake.name(),
                age_group=random.choice(['10대', '20대', '30대', '40대', '50대', '60대 이상']),
                group_type=random.choice(['가족', '친구', '커플', '혼자', '단체']),
                place_info=fake.address(),
                preferred_activities=fake.word(),
                event_interest=random.choice([True, False]),
                transport_info=fake.word(),
                mobility_needs=fake.word(),
                meal_preference=fake.word(),
                language_support=random.choice([True, False]),
                season=random.choice(['봄', '여름', '가을', '겨울']),
                repeat_visitor=random.choice([True, False]),
                travel_insurance=random.choice([True, False]),
            )

        messages.success(request, f"✅ AI 스타일 더미 일정 {count}개 생성 완료!")
        return redirect('travel_input:schedule_list')

    return render(request, 'travel_input/generate_ai_dummy.html')


@login_required
def calendar_view(request):
    return render(request, 'travel_input/calendar.html')


@login_required
def calendar_events(request):
    schedules = Schedule.objects.filter(user=request.user)
    events = []
    for s in schedules:
        events.append({
            'title': s.title,
            'start': s.start_date.isoformat(),
            'end': s.end_date.isoformat() if s.end_date else s.start_date.isoformat(),
            'url': f'/travel/schedule/{s.id}/'
        })
    return JsonResponse(events, safe=False)


def api_schedules(request):
    schedules = Schedule.objects.all().values('id', 'title', 'destination', 'start_date', 'end_date')
    return JsonResponse(list(schedules), safe=False)


@login_required
def migrate_schedules(request):
    messages.info(request, "⏳ 일정 복제 기능은 아직 구현되지 않았습니다.")
    return redirect('travel_input:schedule_list')
