from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from ..models import Participant, Schedule
from django.core import serializers
from django.forms.models import model_to_dict
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@require_GET
@login_required
def get_participants(request, export=False):
    participants = Participant.objects.filter(schedule__user=request.user)
    data = [{
        'schedule': participant.schedule.title,
        'gender': participant.gender,
        'num_people': participant.num_people,
        'age_type': participant.age_type,
        'age_range': participant.age_range,
        'is_elderly': participant.is_elderly,
        'is_family': participant.is_family
    } for participant in participants]
    
    if export:
        response = HttpResponse(
            json.dumps({'participants': data}, indent=2, ensure_ascii=False),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="participants_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
        return response
    
    return JsonResponse({'participants': data}, json_dumps_params={'ensure_ascii': False})

@require_GET
@login_required
def get_schedules(request, export=False):
    schedules = Schedule.objects.filter(user=request.user)
    logger.info(f"[DEBUG] Found {schedules.count()} schedules")
    
    data = []
    for schedule in schedules:
        logger.info(f"[DEBUG] Processing schedule: {schedule.title} (ID: {schedule.id})")
        
        # 참여자 데이터를 직접 쿼리하고 SQL 쿼리 출력
        participants = Participant.objects.filter(schedule=schedule)
        logger.info(f"[DEBUG] SQL Query: {str(participants.query)}")
        logger.info(f"[DEBUG] 일정 '{schedule.title}'의 참여자 수: {participants.count()}")
        
        # 참여자 데이터 상세 정보 출력
        for p in participants:
            logger.info(f"[DEBUG] Participant details: {model_to_dict(p)}")
        
        schedule_data = {
            'id': schedule.id,
            'title': schedule.title,
            'destination': schedule.destination,
            'start_date': schedule.start_date.strftime('%Y-%m-%d') if schedule.start_date else None,
            'end_date': schedule.end_date.strftime('%Y-%m-%d') if schedule.end_date else None,
            'budget': str(schedule.budget) if schedule.budget else None,
            'user': schedule.user.username,
            'travel_styles': [style.style for style in schedule.travel_styles.all()],
            'important_factors': [factor.factor for factor in schedule.important_factors.all()],
            'transports': [transport.type for transport in schedule.transports.all()],
            'participants': []
        }
        
        # 참여자 정보 추가
        for participant in participants:
            participant_info = {
                'id': participant.id,
                'gender': participant.gender,
                'num_people': participant.num_people,
                'age_type': participant.age_type,
                'age_range': participant.age_range,
                'is_elderly': participant.is_elderly,
                'is_family': participant.is_family
            }
            schedule_data['participants'].append(participant_info)
            logger.info(f"[DEBUG] Added participant info: {participant_info}")
        
        data.append(schedule_data)
        logger.info(f"[DEBUG] Added schedule data: {json.dumps(schedule_data, ensure_ascii=False)}")
    
    response_data = {'schedules': data}
    
    if export:
        response = HttpResponse(
            json.dumps(response_data, indent=2, ensure_ascii=False),
            content_type='application/json; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="schedules_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
        return response
    
    return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False, 'indent': 2})

@require_GET
@login_required
def export_all_data(request):
    schedules = Schedule.objects.filter(user=request.user).prefetch_related(
        'participants', 'travel_styles', 'important_factors', 'transports'
    )
    
    all_data = []
    for schedule in schedules:
        # 기본 데이터 준비 (get_schedules 함수와 동일한 방식)
        schedule_data = {
            'id': schedule.id,
            'title': schedule.title,
            'destination': schedule.destination,
            'start_date': schedule.start_date.strftime('%Y-%m-%d') if schedule.start_date else None,
            'end_date': schedule.end_date.strftime('%Y-%m-%d') if schedule.end_date else None,
            'budget': str(schedule.budget) if schedule.budget else None,
            'user': schedule.user.username,
            'travel_styles': [style.style for style in schedule.travel_styles.all()],
            'important_factors': [factor.factor for factor in schedule.important_factors.all()],
            'transports': [transport.type for transport in schedule.transports.all()],
            'participants': []
        }
        
        # 참여자 정보 추가
        for participant in schedule.participants.all():
            participant_info = {
                'id': participant.id,
                'gender': participant.gender,
                'num_people': participant.num_people,
                'age_type': participant.age_type,
                'age_range': participant.age_range,
                'is_elderly': participant.is_elderly,
                'is_family': participant.is_family
            }
            schedule_data['participants'].append(participant_info)
        
        # 모든 정보를 하나의 문자열로 합치기
        combined_info = (
            f"id:{schedule_data['id']}, "
            f"title:{schedule_data['title']}, "
            f"destination:{schedule_data['destination']}, "
            f"start_date:{schedule_data['start_date']}, "
            f"end_date:{schedule_data['end_date']}, "
            f"budget:{schedule_data['budget']}, "
            f"user:{schedule_data['user']}, "
            f"travel_styles:{schedule_data['travel_styles']}, "
            f"important_factors:{schedule_data['important_factors']}, "
            f"transports:{schedule_data['transports']}, "
            f"participants:{schedule_data['participants']}"
        )
        
        
        all_data.append({"combined_data": combined_info})
    
    response = HttpResponse(
        json.dumps({'all_data': all_data}, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="all_travel_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response

@require_GET
@login_required
def export_combined_data(request):
    try:
        schedules = Schedule.objects.filter(user=request.user).prefetch_related(
            'participants', 'travel_styles', 'important_factors', 'transports'
        )
        
        all_data = []
        for schedule in schedules:
            # 참여자 정보 문자열로 합치기
            participants_str = "; ".join(
                f"id:{p.id}, gender:{p.gender}, num_people:{p.num_people}, age_type:{p.age_type}, age_range:{p.age_range}, is_elderly:{p.is_elderly}, is_family:{p.is_family}"
                for p in schedule.participants.all()
            )
            
            # travel_styles, important_factors, transports 문자열로 합치기
            travel_styles_str = ", ".join([style.style for style in schedule.travel_styles.all()])
            important_factors_str = ", ".join([factor.factor for factor in schedule.important_factors.all()])
            transports_str = ", ".join([transport.type for transport in schedule.transports.all()])

            # 날짜와 예산을 안전하게 문자열로 변환
            start_date_str = schedule.start_date.strftime('%Y-%m-%d') if schedule.start_date else "None"
            end_date_str = schedule.end_date.strftime('%Y-%m-%d') if schedule.end_date else "None"
            budget_str = str(schedule.budget) if schedule.budget else "None"

            # 모든 필드를 한 문자열로 합치기
            combined_data = (
                f"schedule_id:{schedule.id}, "
                f"title:{schedule.title}, "
                f"destination:{schedule.destination}, "
                f"start_date:{start_date_str}, "
                f"end_date:{end_date_str}, "
                f"budget:{budget_str}, "
                f"user:{schedule.user.username}, "
                f"travel_styles:[{travel_styles_str}], "
                f"important_factors:[{important_factors_str}], "
                f"transports:[{transports_str}], "
                f"participants:[{participants_str}]"
            )
            all_data.append({"combined_data": combined_data})
        
        return JsonResponse({'all_data': all_data}, json_dumps_params={'ensure_ascii': False, 'indent': 2})
    
    except Exception as e:
        print(f"Error: {str(e)}")  # 디버깅을 위한 출력
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
@login_required
def get_schedules_combined(request):
    schedules = Schedule.objects.filter(user=request.user)
    data = []
    
    for schedule in schedules:
        # 참여자 정보를 문자열로 변환
        participants = schedule.participants.all()
        participants_str = "; ".join(
            f"{p.gender}({p.age_type}, {p.age_range}, {p.num_people}명)"
            for p in participants
        )
        
        # 기타 정보들을 문자열로 변환
        travel_styles = schedule.travel_styles.all()
        important_factors = schedule.important_factors.all()
        transports = schedule.transports.all()
        
        travel_styles_str = ", ".join([style.style for style in travel_styles])
        important_factors_str = ", ".join([factor.factor for factor in important_factors])
        transports_str = ", ".join([transport.type for transport in transports])
        
        # 날짜 형식 변환
        start_date = schedule.start_date.strftime('%Y-%m-%d') if schedule.start_date else 'None'
        end_date = schedule.end_date.strftime('%Y-%m-%d') if schedule.end_date else 'None'
        
        # 하나의 문자열로 합치기
        combined_str = (
            f"일정: {schedule.title} | "
            f"목적지: {schedule.destination} | "
            f"기간: {start_date} ~ {end_date} | "
            f"예산: {schedule.budget or 'None'} | "
            f"여행스타일: [{travel_styles_str}] | "
            f"중요요소: [{important_factors_str}] | "
            f"교통수단: [{transports_str}] | "
            f"참여자: [{participants_str}]"
        )
        
        data.append({"combined_info": combined_str})
    
    return JsonResponse({"schedules": data}, json_dumps_params={'ensure_ascii': False})

@require_GET
@login_required
def test_api(request):
    """테스트용 API 엔드포인트"""
    return JsonResponse({
        'message': 'API is working',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@require_GET
@login_required
def simple_schedules(request):
    """간단한 일정 목록 반환"""
    schedules = Schedule.objects.filter(user=request.user)
    data = [{
        'id': s.id,
        'title': s.title,
        'destination': s.destination
    } for s in schedules]
    return JsonResponse({'schedules': data}, json_dumps_params={'ensure_ascii': False}) 