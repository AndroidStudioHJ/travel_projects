# travel_input/urls.py
from django.urls import path
from . import views  # travel_input/views.py에서 함수들을 불러옵니다.
from .views import (
    home, travel_survey, smart_schedule, recommendations, 
    budget_planning, group_travel, schedule_create, schedule_list,
    schedule_detail, schedule_update, schedule_delete, confirm_delete_all,
    GroupTravelListView, GroupTravelDetailView, GroupTravelCreateView,
    GroupTravelUpdateView, GroupTravelDeleteView, join_group, leave_group,
    send_message, ai_budget_view, ai_recommend_view, ai_summarize_view,
    get_participants, get_schedules, export_all_data
)
from .views.api import get_participants, get_schedules, export_all_data  # export_all_data import 확인

app_name = 'travel_input'

urlpatterns = [
    path('', views.home, name='home'),
    path('schedule/', views.schedule_list, name='schedule_list'),
    path('schedule/create/', views.schedule_create, name='schedule_create'),
    path('schedule/<int:pk>/', views.schedule_detail, name='schedule_detail'),
    path('schedule/<int:pk>/update/', views.schedule_update, name='schedule_update'),
    path('schedule/<int:pk>/delete/', views.schedule_delete, name='schedule_delete'),
    path('schedule/delete-all/', confirm_delete_all, name='schedule_delete_all'),
    path('smart-schedule/', views.smart_schedule, name='smart_schedule'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('budget-planning/', views.budget_planning, name='budget_planning'),
    path('group-travel/', GroupTravelListView.as_view(), name='group_travel_list'),
    path('group-travel/create/', GroupTravelCreateView.as_view(), name='group_travel_create'),
    path('group-travel/<int:pk>/', GroupTravelDetailView.as_view(), name='group_travel_detail'),
    path('group-travel/<int:pk>/update/', GroupTravelUpdateView.as_view(), name='group_travel_update'),
    path('group-travel/<int:pk>/delete/', GroupTravelDeleteView.as_view(), name='group_travel_delete'),
    path('group-travel/<int:pk>/join/', join_group, name='join_group'),
    path('group-travel/<int:pk>/leave/', leave_group, name='leave_group'),
    path('group-travel/<int:pk>/send-message/', send_message, name='send_message'),
    path('survey/', views.travel_survey, name='travel_survey'),
    path('culture/', views.culture, name='culture'),
    path('lodging/', views.lodging, name='lodging'),
    path('ai_budget/', ai_budget_view, name='ai_budget'),
    path('ai_recommend/', ai_recommend_view, name='ai_recommend'),
    path('ai_summarize/', ai_summarize_view, name='ai_summarize'),
    
    # API endpoints
    path('api/participants/', get_participants, name='api_participants'),
    path('api/schedules/', get_schedules, name='api_schedules'),
    path('api/participants/export/', get_participants, {'export': True}, name='export_participants'),
    path('api/schedules/export/', get_schedules, {'export': True}, name='export_schedules'),
    path('api/export/all/', export_all_data, name='export_all_data'),
]
