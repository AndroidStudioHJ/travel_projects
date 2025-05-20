from django.urls import path
from .views import (
    home, travel_survey, smart_schedule, recommendations,
    schedule_list, schedule_detail, schedule_create, schedule_update, 
    schedule_delete, confirm_delete_all, toggle_favorite, favorite_schedules,
    calendar_view, calendar_events, generate_ai_style_schedules,
    generate_dummy_schedules, migrate_schedules, api_schedules,
    ai_budget_view, ai_recommend_view, ai_summarize_view,
    budget_planning, blog_search
)

# ✅ 새로 추가된 뷰 (AI 질문 기반 여행 추천)
from .views.ai import travel_ai_consult

app_name = 'travel_input'

urlpatterns = [
    # 홈
    path('', home, name='home'),

    # 여행 일정
    path('schedule/', schedule_list, name='schedule_list'),
    path('schedule/create/', schedule_create, name='schedule_create'),
    path('schedule/<int:pk>/', schedule_detail, name='schedule_detail'),
    path('schedule/<int:pk>/update/', schedule_update, name='schedule_update'),
    path('schedule/<int:pk>/delete/', schedule_delete, name='schedule_delete'),
    path('schedule/delete-all/', confirm_delete_all, name='schedule_delete_all'),
    path('schedule/migrate/', migrate_schedules, name='schedule_migrate'),
    path('schedule/generate-dummy/', generate_dummy_schedules, name='generate_dummy'),
    path('schedule/generate-ai/', generate_ai_style_schedules, name='generate_ai_style_schedules'),

    # 즐겨찾기
    path('schedule/<int:schedule_id>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('schedule/favorites/', favorite_schedules, name='favorite_list'),

    # 캘린더
    path('schedule/calendar/', calendar_view, name='calendar_view'),
    path('schedule/events/', calendar_events, name='calendar_events'),

    # 스마트 추천 및 예산
    path('smart-schedule/', smart_schedule, name='smart_schedule'),
    path('recommendations/', recommendations, name='recommendations'),
    path('budget-planning/', budget_planning, name='budget_planning'),

    # ✅ OpenAI 기반 AI 기능 (JSON 또는 텍스트 출력)
    path('ai_budget/', ai_budget_view, name='ai_budget'),                  # 예산 분배
    path('ai_recommend/', ai_recommend_view, name='ai_recommend'),        # 장소 추천
    path('ai_summarize/', ai_summarize_view, name='ai_summarize'),        # 텍스트 요약
    path('ai_consult/', travel_ai_consult, name='travel_ai_consult'),     # 맞춤 상담

    # 설문 → AI 추천
    path('survey/', travel_survey, name='travel_survey'),

    # API: 일정 데이터 반환용
    path('api/schedules/', api_schedules, name='api_schedules'),
    
    path('blog_search/', blog_search, name='blog_search'),
]
