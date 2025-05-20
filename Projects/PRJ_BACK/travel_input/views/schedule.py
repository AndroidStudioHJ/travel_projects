from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from ..forms import ScheduleForm, ParticipantFormSet
from ..models import Schedule, Participant
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

@login_required
def schedule_list(request):
    schedules = Schedule.objects.filter(user=request.user)
    
    # 검색 기능
    search_query = request.GET.get('search')
    if search_query:
        schedules = schedules.filter(
            Q(title__icontains=search_query) |
            Q(destination__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # 필터링
    destination = request.GET.get('destination')
    if destination:
        schedules = schedules.filter(destination=destination)
        
    start_date = request.GET.get('start_date')
    if start_date:
        schedules = schedules.filter(start_date__gte=start_date)
        
    return render(request, 'travel_input/schedule_list.html', {
        'schedules': schedules,
        'search_query': search_query,
        'destinations': Schedule.objects.values_list('destination', flat=True).distinct()
    })

@login_required
def schedule_detail(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    return render(request, 'travel_input/schedule_detail.html', {'schedule': schedule})

@login_required
def schedule_create(request):
    if request.method == 'POST':
        logger.info("[DEBUG] Processing schedule creation POST request")
        form = ScheduleForm(request.POST)
        participant_formset = ParticipantFormSet(request.POST)
        
        logger.info(f"[DEBUG] Form data: {request.POST}")
        logger.info(f"[DEBUG] Form is valid: {form.is_valid()}")
        logger.info(f"[DEBUG] Participant formset is valid: {participant_formset.is_valid()}")
        
        if form.is_valid() and participant_formset.is_valid():
            try:
                with transaction.atomic():
                    # 일정 저장
                    schedule = form.save(commit=False)
                    schedule.user = request.user
                    schedule.save()
                    logger.info(f"[DEBUG] Created schedule: {schedule.id} - {schedule.title}")
                    
                    # 여행 스타일, 중요 요소, 교통수단 저장
                    form.save_m2m()
                    
                    # 참여자 정보 저장
                    participants = []
                    for participant_form in participant_formset:
                        if participant_form.cleaned_data and not participant_form.cleaned_data.get('DELETE', False):
                            participant = participant_form.save(commit=False)
                            participant.schedule = schedule
                            participant.save()
                            participants.append(participant)
                            logger.info(f"[DEBUG] Saved participant: {participant.id} - {participant.gender}, {participant.age_type}")
                    
                    # 저장된 참여자 확인
                    saved_participants = Participant.objects.filter(schedule=schedule)
                    logger.info(f"[DEBUG] Confirmed saved participants: {[p.id for p in saved_participants]}")
                    
                    messages.success(request, '일정이 성공적으로 생성되었습니다.')
                    return redirect('travel_input:schedule_detail', pk=schedule.pk)
            except Exception as e:
                logger.error(f"[ERROR] Failed to save schedule: {str(e)}")
                messages.error(request, f'일정 저장 중 오류가 발생했습니다: {str(e)}')
        else:
            logger.error("[ERROR] Form validation failed")
            logger.error(f"[ERROR] Form errors: {form.errors}")
            logger.error(f"[ERROR] Participant formset errors: {participant_formset.errors}")
            if not form.is_valid():
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{form.fields[field].label}: {error}')
            if not participant_formset.is_valid():
                for form in participant_formset:
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f'참여자 정보: {error}')
    else:
        form = ScheduleForm()
        participant_formset = ParticipantFormSet()
    
    return render(request, 'travel_input/schedule_form.html', {
        'form': form,
        'participant_formset': participant_formset
    })

@login_required
def schedule_update(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    if request.method == 'POST':
        logger.info(f"[DEBUG] Processing schedule update POST request for schedule {pk}")
        form = ScheduleForm(request.POST, instance=schedule)
        participant_formset = ParticipantFormSet(request.POST, instance=schedule)
        
        logger.info(f"[DEBUG] Form data: {request.POST}")
        logger.info(f"[DEBUG] Form is valid: {form.is_valid()}")
        logger.info(f"[DEBUG] Participant formset is valid: {participant_formset.is_valid()}")
        
        if form.is_valid() and participant_formset.is_valid():
            try:
                with transaction.atomic():
                    # 일정 업데이트
                    schedule = form.save()
                    logger.info(f"[DEBUG] Updated schedule: {schedule.id} - {schedule.title}")
                    
                    # 기존 참여자 정보 삭제
                    Participant.objects.filter(schedule=schedule).delete()
                    logger.info("[DEBUG] Deleted existing participants")
                    
                    # 새로운 참여자 정보 저장
                    participants = []
                    for participant_form in participant_formset:
                        if participant_form.cleaned_data and not participant_form.cleaned_data.get('DELETE', False):
                            participant = participant_form.save(commit=False)
                            participant.schedule = schedule
                            participant.save()
                            participants.append(participant)
                            logger.info(f"[DEBUG] Saved participant: {participant.id} - {participant.gender}, {participant.age_type}")
                    
                    # 저장된 참여자 확인
                    saved_participants = Participant.objects.filter(schedule=schedule)
                    logger.info(f"[DEBUG] Confirmed saved participants: {[p.id for p in saved_participants]}")
                    
                    messages.success(request, '일정이 성공적으로 수정되었습니다.')
                    return redirect('travel_input:schedule_detail', pk=schedule.pk)
            except Exception as e:
                logger.error(f"[ERROR] Failed to update schedule: {str(e)}")
                messages.error(request, f'일정 수정 중 오류가 발생했습니다: {str(e)}')
        else:
            logger.error("[ERROR] Form validation failed")
            logger.error(f"[ERROR] Form errors: {form.errors}")
            logger.error(f"[ERROR] Participant formset errors: {participant_formset.errors}")
            messages.error(request, '입력 내용을 확인해주세요.')
    else:
        form = ScheduleForm(instance=schedule)
        participant_formset = ParticipantFormSet(instance=schedule)
    
    return render(request, 'travel_input/schedule_form.html', {
        'form': form,
        'participant_formset': participant_formset
    })

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