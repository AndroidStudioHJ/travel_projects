from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import date, timedelta
import random
from faker import Faker
from openai import OpenAI
from django.conf import settings

from travel_input.forms import ScheduleForm
from travel_input.models import Schedule, Destination

TRAVEL_PURPOSE_LABELS = {
    'healing': '휴식', 'sightseeing': '관광', 'adventure': '모험',
    'photo': '사진 촬영', 'family': '가족 여행', 'couple': '커플 여행',
    'culture': '문화 체험', 'food': '먹거리 탐방', 'selfdev': '자기 개발', 'shopping': '쇼핑'
}
TRAVEL_STYLE_LABELS = {
    'nature': '자연경관', 'city': '도시 탐방', 'culture': '문화 체험',
    'activity': '액티비티', 'relax': '휴식과 힐링'
}
IMPORTANT_FACTOR_LABELS = {
    'stay': '숙소', 'food': '음식', 'weather': '날씨',
    'schedule': '일정 편의성', 'culture': '현지 문화'
}

@login_required
def schedule_create(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = request.user
            schedule.save()

            purposes = ', '.join(schedule.travel_purpose or [])
            styles = ', '.join(schedule.travel_style or [])
            factors = ', '.join(schedule.important_factors or [])

            prompt = f"""당신은 여행 일정 전문가입니다. 다음 정보를 바탕으로 여행 계획을 날짜별로 구성해 주세요.

- 여행 제목: {schedule.title}
- 여행지: {schedule.destination}
- 여행 날짜: {schedule.start_date} ~ {schedule.end_date}
- 여행 목적: {purposes or '없음'}
- 여행 스타일: {styles or '없음'}
- 중요 요소: {factors or '없음'}
- 메모(특이사항): {schedule.notes or '없음'}

각 날짜별로 추천 일정과 장소, 활동을 포함해 주세요."""

            try:
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "당신은 여행 일정 전문가입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=800,
                    temperature=0.7,
                )
                ai_answer = response.choices[0].message.content.strip()
            except Exception as e:
                ai_answer = f"AI 응답 오류: {str(e)}"

            return render(request, 'travel_input/schedule_detail.html', {
                'schedule': schedule,
                'ai_answer': ai_answer,
                'travel_purpose_labels': TRAVEL_PURPOSE_LABELS,
                'travel_style_labels': TRAVEL_STYLE_LABELS,
                'important_factor_labels': IMPORTANT_FACTOR_LABELS
            })
    else:
        form = ScheduleForm()

    return render(request, 'travel_input/schedule_form.html', {'form': form})

@login_required
def schedule_list(request):
    schedules = Schedule.objects.filter(user=request.user).order_by('-created_at')
    schedules_calendar = [
        {
            "id": s.id,
            "title": s.title,
            "start_date": s.start_date.isoformat() if s.start_date else None,
            "end_date": s.end_date.isoformat() if s.end_date else None,
        }
        for s in schedules if s.start_date and s.end_date and s.title
    ]
    return render(request, 'travel_input/schedule_list.html', {
        'schedules': schedules,
        'schedules_calendar': schedules_calendar,
    })

@login_required
def schedule_detail(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    ai_answer = None

    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        if question:
            try:
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                prompt = f"""일정 정보:
- 제목: {schedule.title}
- 날짜: {schedule.start_date} ~ {schedule.end_date}
- 목적지: {schedule.destination}
- 비고: {schedule.notes}

질문: {question}
"""
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 여행 일정 전문가입니다. 사용자의 여행 정보에 맞는 조언을 해주세요."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7,
                )
                ai_answer = response.choices[0].message.content.strip()
            except Exception as e:
                ai_answer = f"AI 응답 오류: {str(e)}"

    return render(request, 'travel_input/schedule_detail.html', {
        'schedule': schedule,
        'ai_answer': ai_answer,
        'travel_purpose_labels': TRAVEL_PURPOSE_LABELS,
        'travel_style_labels': TRAVEL_STYLE_LABELS,
        'important_factor_labels': IMPORTANT_FACTOR_LABELS
    })

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
        messages.success(request, '모든 일정이 삭제되었습니다.')
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
def generate_dummy_schedules(request):
    if request.method == 'POST':
        for _ in range(10):
            Schedule.objects.create(
                user=request.user,
                title='기본 더미 일정',
                destination=Destination.objects.order_by('?').first(),
                start_date=date.today(),
                end_date=date.today() + timedelta(days=3),
                notes='자동 생성된 기본 일정입니다.',
                travel_style=['city'],
                important_factors=['food']
            )
        messages.success(request, "✅ 기본 더미 일정 10개 생성 완료!")
        return redirect('travel_input:schedule_list')

    return render(request, 'travel_input/generate_dummy.html')

@login_required
def migrate_schedules(request):
    messages.info(request, "⏳ 일정 복제 기능은 아직 구현되지 않았습니다.")
    return redirect('travel_input:schedule_list')

@login_required
def api_schedules(request):
    schedules = Schedule.objects.filter(user=request.user).values(
        'id', 'title', 'destination__name', 'start_date', 'end_date'
    )
    return JsonResponse(list(schedules), safe=False)
