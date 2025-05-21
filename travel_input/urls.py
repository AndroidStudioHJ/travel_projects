from django.urls import path
from .views import (
    # 기본 및 설문/추천
    home, travel_survey, smart_schedule, recommendations,
    
    # 일정 기능
    schedule_list, schedule_detail, schedule_create, schedule_update, 
    schedule_delete, confirm_delete_all, toggle_favorite, favorite_schedules,
    generate_ai_style_schedules, generate_dummy_schedules, migrate_schedules,
    
    # 캘린더
    calendar_view, calendar_events,

    # AI 기능
    ai_budget_view, ai_recommend_view, ai_summarize_view,

    # 예산 계획
    budget_planning,

    # API
    api_schedules,
)

app_name = 'travel_input'

urlpatterns = [
    # 🏠 기본 홈
    path('', home, name='home'),

    # 📅 일정 관리
    path('schedule/', schedule_list, name='schedule_list'),
    path('schedule/create/', schedule_create, name='schedule_create'),
    path('schedule/<int:pk>/', schedule_detail, name='schedule_detail'),
    path('schedule/<int:pk>/update/', schedule_update, name='schedule_update'),
    path('schedule/<int:pk>/delete/', schedule_delete, name='schedule_delete'),
    path('schedule/delete-all/', confirm_delete_all, name='schedule_delete_all'),
    path('schedule/migrate/', migrate_schedules, name='schedule_migrate'),
    path('schedule/generate-dummy/', generate_dummy_schedules, name='generate_dummy'),
    path('schedule/generate-ai/', generate_ai_style_schedules, name='generate_ai_style_schedules'),

    # ⭐ 즐겨찾기
    path('schedule/<int:pk>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('schedule/favorites/', favorite_schedules, name='favorite_list'),

    # 🗓 FullCalendar
    path('schedule/calendar/', calendar_view, name='calendar_view'),
    path('schedule/events/', calendar_events, name='calendar_events'),

    # 🤖 AI 기능
    path('smart-schedule/', smart_schedule, name='smart_schedule'),
    path('recommendations/', recommendations, name='recommendations'),
    path('budget-planning/', budget_planning, name='budget_planning'),
    path('ai_budget/', ai_budget_view, name='ai_budget'),
    path('ai_recommend/', ai_recommend_view, name='ai_recommend'),
    path('ai_summarize/', ai_summarize_view, name='ai_summarize'),

    # 🔗 API
    path('api/schedules/', api_schedules, name='api_schedules'),
]
