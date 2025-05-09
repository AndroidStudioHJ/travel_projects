from django.urls import path
from . import views
from .views.base import generate_dummy_view  # 🔹 더미 뷰 import

from .views.schedule import (
    api_schedules,
    schedule_create, schedule_list, schedule_detail,
    schedule_update, schedule_delete, confirm_delete_all,
    toggle_favorite, favorite_schedules,
    calendar_view, calendar_events,
    migrate_schedules,             # ✅ 일정 복제
    generate_dummy_schedules,     # ✅ 더미 일정 생성
    generate_ai_style_schedules   # ✅ AI 스타일 더미 일정 생성
)

from .views import (
    home, travel_survey, smart_schedule, recommendations,
    budget_planning, group_travel,
    GroupTravelListView, GroupTravelDetailView, GroupTravelCreateView,
    GroupTravelUpdateView, GroupTravelDeleteView, join_group, leave_group,
    send_message, ai_budget_view, ai_recommend_view, ai_summarize_view
)

app_name = 'travel_input'

urlpatterns = [
    # 기본 홈
    path('', home, name='home'),

    # 일정 관리
    path('schedule/', schedule_list, name='schedule_list'),
    path('schedule/create/', schedule_create, name='schedule_create'),
    path('schedule/<int:pk>/', schedule_detail, name='schedule_detail'),
    path('schedule/<int:pk>/update/', schedule_update, name='schedule_update'),
    path('schedule/<int:pk>/delete/', schedule_delete, name='schedule_delete'),
    path('schedule/delete-all/', confirm_delete_all, name='schedule_delete_all'),
    path('schedule/migrate/', migrate_schedules, name='schedule_migrate'),                # ✅ 일정 복제
    path('schedule/generate-dummy/', generate_dummy_schedules, name='generate_dummy'),     # ✅ 더미 생성
    path('schedule/generate-ai/', generate_ai_style_schedules, name='generate_ai_style_schedules'),  # ✅ AI 스타일 더미 일정 생성

    # 즐겨찾기 기능
    path('schedule/<int:schedule_id>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('schedule/favorites/', favorite_schedules, name='favorite_list'),

    # FullCalendar 이벤트
    path('schedule/calendar/', calendar_view, name='calendar_view'),
    path('schedule/events/', calendar_events, name='calendar_events'),

    # AI 및 추천 기능
    path('smart-schedule/', smart_schedule, name='smart_schedule'),
    path('recommendations/', recommendations, name='recommendations'),
    path('budget-planning/', budget_planning, name='budget_planning'),
    path('ai_budget/', ai_budget_view, name='ai_budget'),
    path('ai_recommend/', ai_recommend_view, name='ai_recommend'),
    path('ai_summarize/', ai_summarize_view, name='ai_summarize'),

    # 그룹 여행
    path('group-travel/', GroupTravelListView.as_view(), name='group_travel_list'),
    path('group-travel/create/', GroupTravelCreateView.as_view(), name='group_travel_create'),
    path('group-travel/<int:pk>/', GroupTravelDetailView.as_view(), name='group_travel_detail'),
    path('group-travel/<int:pk>/update/', GroupTravelUpdateView.as_view(), name='group_travel_update'),
    path('group-travel/<int:pk>/delete/', GroupTravelDeleteView.as_view(), name='group_travel_delete'),
    path('group-travel/<int:pk>/join/', join_group, name='join_group'),
    path('group-travel/<int:pk>/leave/', leave_group, name='leave_group'),
    path('group-travel/<int:pk>/send-message/', send_message, name='send_message'),

    # 일반 정보
    path('survey/', travel_survey, name='travel_survey'),
    path('culture/', views.culture, name='culture'),
    path('lodging/', views.lodging, name='lodging'),

    # 🔹 더미 뷰 페이지
    path('generate-dummy-view/', generate_dummy_view, name='generate_dummy_view'),

    # 🔹 API: 일정 목록 반환
    path('api/schedules/', api_schedules, name='api_schedules'),
]
