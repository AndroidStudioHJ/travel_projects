from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import date, timedelta, datetime
import random
from faker import Faker
import openai
from django.conf import settings
import re

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


def json_to_markdown(data):
    lines = [f"### {data.get('title', '여행 추천')}\n"]

    def section(title, items):
        if not items:
            return ""
        result = [f"**{title}**"]
        for item in items:
            if isinstance(item["value"], list):  # 메뉴 등 리스트
                result.append(f"- {item['label']}:")
                for sub in item["value"]:
                    result.append(f"  * {sub[0]} - {sub[1]}")
            else:
                result.append(f"- {item['label']}: {item['value']}")
        return "\n".join(result) + "\n"

    lines.append(section("방문 정보", data.get("visit_info")))
    lines.append(section("참가자 정보", data.get("participant_info")))
    lines.append(section("음식 정보", data.get("food_info")))
    lines.append(section("추가 정보", data.get("additional_info")))
    lines.append("\n더 궁금한 점이 있으시다면 언제든 물어보세요!")

    return "\n\n".join(lines)

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

def format_all_sections(text):
    """
    여러 개 일정(1. ~ 또는 ### 제목 등)이 있을 경우 각 블록을 나눈 뒤,
    방문 정보 / 음식 정보 등 각 섹션의 항목을 줄 단위로 나누고 마크다운 포맷으로 재구성
    """
    # 일정 블록 기준 분리 (1. 제목 or ### 제목)
    blocks = re.split(r'(?=\n?\d+\.\s|^### )', text.strip())

    def fix_block(block):
        def fix_section(section, text_in):
            pattern = rf'(\*\*{section}\*\*)(.*?)(?=(\*\*|$))'
            matches = re.findall(pattern, text_in, re.DOTALL)
            for header, content, _ in matches:
                # ⚠️ 메뉴 줄바꿈 없이 이어진 경우 처리
                # 예: - 추천 장소: * A * B * C → → 줄 단위로 쪼개기
                content = re.sub(r'(?<!\n)([*-])\s+', r'\n\1 ', content)
                content = re.sub(r'(?<=\n)([가-힣A-Za-z0-9\s\(\)]+)\n(\d{1,3}(,\d{3})*원)', r'*\1 - \2', content)

                lines = content.strip().split('\n')
                fixed_lines = []

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith(('-', '*')):
                        fixed_lines.append(line)
                    elif ':' in line:
                        fixed_lines.append(f"- {line}")
                    else:
                        fixed_lines.append(f"  {line}")  # 가격 같은 보조 정보 들여쓰기

                new_block = header + '\n' + '\n'.join(fixed_lines) + '\n\n'
                text_in = text_in.replace(header + content, new_block)
            return text_in

        for sec in ['방문 정보', '참가자 정보', '음식 정보', '추가 정보']:
            block = fix_section(sec, block)
        return block

    return "\n".join([fix_block(b) for b in blocks if b.strip()])


def fix_markdown_newlines(text):
    text = re.sub(r'(### )', r'\n\n\g<1>', text)
    for section in ['방문 정보', '참가자 정보', '음식 정보', '추가 정보']:
        text = re.sub(rf'(\*\*{section}\*\*)', r'\n\n\g<1>', text)
    text = re.sub(r'(?<!\n)- ', r'\n- ', text)
    text = re.sub(r'(?<!\n)\* ', r'\n* ', text)
    text = re.sub(r'\n{3,}', r'\n\n', text)
    return text

@login_required
def schedule_detail(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    ai_answers = request.session.get('ai_answers', [])

    if request.GET.get('clear_answers'):
        request.session['ai_answers'] = []
        return redirect('travel_input:schedule_detail', pk=pk)

    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        if question:
            openai.api_key = settings.OPENAI_API_KEY
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

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

            prompt = f"""다음 여행 정보와 질문에 기반해, 아래와 같은 JSON 형식으로 응답해 주세요.

일정 정보:
{schedule_info}

질문: {question}

다음 여행 정보를 기반으로 추천 일정을 작성해주세요. 
출력은 반드시 마크다운 형식을 따르고, 아래 가이드를 지켜주세요:

1. 제목은 `### 여행 제목` 형식으로 출력  
2. 항목은 `**방문 정보**`, `**참가자 정보**`, `**음식 정보**`, `**추가 정보**` 순서로 작성  
3. 각 항목은 `- 항목명: 내용` 으로 줄바꿈하여 작성  
4. 메뉴나 리스트는 `* 메뉴명 - 가격` 형식으로 작성  
5. 모든 줄은 마크다운 파서에서 정확히 인식되도록 줄마다 줄바꿈  
6. 절대 JSON 형식이나 설명 문장을 섞지 마세요. 출력은 마크다운만 하세요.  
7. 마지막 줄은 `더 궁금한 점이 있으시다면 언제든 물어보세요!`로 마무리  

단, 반드시 올바른 마크다운으로 출력하세요.
"""


            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 여행 일정 추천 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
            )

            ai_answer = response.choices[0].message.content
            ai_answer = format_all_sections(ai_answer)
            ai_answer = fix_markdown_newlines(ai_answer)

            if len(ai_answers) >= 3:
                ai_answers.pop()
            ai_answers.insert(0, ai_answer)
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

