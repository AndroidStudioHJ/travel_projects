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
    data = {
        'schedules': [{
            'title': s.title,
            'destination': s.destination,
            'start_date': s.start_date,
            'end_date': s.end_date,
            'budget': str(s.budget) if s.budget else None,
            'user': s.user.username,
            'travel_styles': [style.style for style in s.travel_styles.all()],
            'important_factors': [factor.factor for factor in s.important_factors.all()],
            'transports': [transport.type for transport in s.transports.all()],
            'participants': [{
                'gender': p.gender,
                'num_people': p.num_people,
                'age_type': p.age_type,
                'age_range': p.age_range,
                'is_elderly': p.is_elderly,
                'is_family': p.is_family
            } for p in s.participants.all()]
        } for s in schedules]
    }
    
    response = HttpResponse(
        json.dumps(data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="travel_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
    return response 