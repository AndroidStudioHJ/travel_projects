from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from .models import Participant, Schedule
from .sentiment import build_search_url, fetch_html, parse_posts, split_by_sentiment
from django.shortcuts import render

@require_GET
@login_required
def get_participants(request):
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
    return JsonResponse({'participants': data})

@require_GET
@login_required
def get_schedules(request):
    schedules = Schedule.objects.filter(user=request.user)
    data = [{
        'title': schedule.title,
        'destination': schedule.destination,
        'start_date': schedule.start_date,
        'end_date': schedule.end_date,
        'budget': str(schedule.budget) if schedule.budget else None,
        'user': schedule.user.username
    } for schedule in schedules]
    return JsonResponse({'schedules': data}) 