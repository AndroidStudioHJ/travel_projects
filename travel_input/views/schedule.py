from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from ..forms import ScheduleForm, ParticipantFormSet
from ..models import Schedule
from django.db.models import Q

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
        form = ScheduleForm(request.POST)
        participant_formset = ParticipantFormSet(request.POST)
        
        if form.is_valid() and participant_formset.is_valid():
            with transaction.atomic():
                schedule = form.save(commit=False)
                schedule.user = request.user
                schedule.save()
                
                # 여행 스타일, 중요 요소, 교통수단 저장
                form.save_m2m()
                
                # 참여자 정보 저장
                participant_formset.instance = schedule
                participant_formset.save()
                
                messages.success(request, '일정이 성공적으로 생성되었습니다.')
                return redirect('travel_input:schedule_detail', pk=schedule.pk)
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
        form = ScheduleForm(request.POST, instance=schedule)
        participant_formset = ParticipantFormSet(request.POST, instance=schedule)
        
        if form.is_valid() and participant_formset.is_valid():
            with transaction.atomic():
                schedule = form.save()
                participant_formset.save()
                messages.success(request, '일정이 성공적으로 수정되었습니다.')
                return redirect('travel_input:schedule_detail', pk=schedule.pk)
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