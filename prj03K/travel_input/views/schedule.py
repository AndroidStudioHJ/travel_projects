from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import date, timedelta, datetime
import random
from faker import Faker

from travel_input.forms import ScheduleForm
from travel_input.models import Schedule, Destination, Specialty  # Specialty 추가

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
    schedules_calendar = [
        {
            "id": s.id,
            "title": s.title,
            "start_date": s.start_date.isoformat() if s.start_date else None,
            "end_date": s.end_date.isoformat() if s.end_date else None,
        }
        for s in schedules
        if s.start_date and s.end_date and s.title
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
    return render(request, 'travel_input/schedule_detail.html', {'schedule': schedule})

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

# ✅ AI 추천 결과 저장 함수
def save_ai_result(user, ai_data):
    """
    AI 추천 데이터를 받아서 Schedule로 저장합니다.

    ai_data 예시:
    {
        'title': '힐링 제주 여행',
        'destination': '제주',
        'start_date': date(2025, 7, 1),
        'end_date': date(2025, 7, 4),
        'budget': 1000000,
        ...
    }
    """
    dest_name = ai_data.get('destination', '서울')
    destination_obj, _ = Destination.objects.get_or_create(name=dest_name)

    schedule = Schedule.objects.create(
        user=user,
        title=ai_data.get('title', 'AI 추천 일정'),
        destination=destination_obj,
        start_date=ai_data.get('start_date', date.today()),
        end_date=ai_data.get('end_date', date.today() + timedelta(days=3)),
        notes=ai_data.get('notes', ''),
        budget=ai_data.get('budget', 500000),
        participant_info=ai_data.get('participant_info', ''),
        age_group=ai_data.get('age_group', ''),
        group_type=ai_data.get('group_type', ''),
        place_info=ai_data.get('place_info', ''),
        preferred_activities=ai_data.get('preferred_activities', ''),
        event_interest=ai_data.get('event_interest', False),
        transport_info=ai_data.get('transport_info', ''),
        mobility_needs=ai_data.get('mobility_needs', ''),
        meal_preference=ai_data.get('meal_preference', ''),
        language_support=ai_data.get('language_support', False),
        season=ai_data.get('season', ''),
        repeat_visitor=ai_data.get('repeat_visitor', False),
        travel_insurance=ai_data.get('travel_insurance', False),
    )
    return schedule

@login_required
def regional_specialty_view(request):
    specialties = Specialty.objects.all()
    return render(request, 'travel_input/regional_specialty.html', {
        'specialties': specialties,
    })

# ✅ 지역 특산물 뷰 (전체, 지역 또는 권역별 필터링)
@login_required
def regional_specialty_view(request, region_name=None, group_name=None):
    specialties_by_region = {
        '서울': ['경복궁 전통주', '광장시장 육회'],
        '부산': ['기장 미역', '부산 어묵', '대구탕'],
        '대구': ['막창', '누룽지통닭', '사과'],
        '인천': ['강화 인삼', '새우젓', '강화 순무'],
        '광주': ['광주 떡갈비', '무등산 수박'],
        '대전': ['대전 성심당 튀김소보로', '칼국수'],
        '울산': ['울산 고래고기', '울산 회국수'],
        '세종': ['세종 쌀국수', '세종 로컬 허브'],
        '경기도': ['이천 쌀', '양평 한우', '안성 마춤한과'],
        '강원도': ['횡성 한우', '춘천 닭갈비', '감자전'],
        '충청북도': ['청주 육거리 곱창', '괴산 대학찰옥수수'],
        '충청남도': ['서산 마늘', '금산 인삼', '논산 딸기'],
        '전라북도': ['전주 비빔밥', '익산 국수', '정읍 쌍화차'],
        '전라남도': ['순천만 꼬막', '보성 녹차', '여수 갓김치'],
        '경상북도': ['안동 찜닭', '문경 오미자', '영주 한우'],
        '경상남도': ['밀양 대추', '하동 녹차', '진주 비빔밥'],
        '제주도': ['제주 흑돼지', '옥돔', '한라봉'],
    }

    REGION_GROUPS = {
        '수도권': ['서울', '인천', '경기도'],
        '충청권': ['대전', '세종', '충청북도', '충청남도'],
        '전라권': ['광주', '전라북도', '전라남도'],
        '경상권': ['부산', '대구', '울산', '경상북도', '경상남도'],
        '강원권': ['강원도'],
        '제주권': ['제주도'],
    }

    all_regions = list(specialties_by_region.keys())
    all_groups = list(REGION_GROUPS.keys())

    if region_name:
        if region_name not in specialties_by_region:
            raise Http404("존재하지 않는 지역입니다.")
        filtered = {region_name: specialties_by_region[region_name]}
    elif group_name:
        if group_name not in REGION_GROUPS:
            raise Http404("존재하지 않는 권역입니다.")
        regions = REGION_GROUPS[group_name]
        filtered = {r: specialties_by_region[r] for r in regions if r in specialties_by_region}
    else:
        filtered = specialties_by_region

    return render(request, 'travel_input/regional_specialty.html', {
        'specialties_by_region': filtered,
        'current_region': region_name,
        'current_group': group_name,
        'all_regions': all_regions,
        'all_groups': all_groups,
    })