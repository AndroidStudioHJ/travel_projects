from .base import home, travel_survey, smart_schedule, recommendations
from .schedule import (
    schedule_list, schedule_detail, schedule_create, 
    schedule_update, schedule_delete, confirm_delete_all,
    toggle_favorite, favorite_schedules, calendar_view, calendar_events,
    generate_ai_style_schedules, generate_dummy_schedules, migrate_schedules,
    api_schedules
)
from .ai import ai_budget_view, ai_recommend_view, ai_summarize_view
from .budget import budget_planning

__all__ = [
    'home', 'travel_survey', 'smart_schedule', 'recommendations',
    'schedule_list', 'schedule_detail', 'schedule_create', 'schedule_update', 
    'schedule_delete', 'confirm_delete_all',
    'toggle_favorite', 'favorite_schedules', 'calendar_view', 'calendar_events',
    'generate_ai_style_schedules', 'generate_dummy_schedules', 'migrate_schedules',
    'api_schedules',
    'ai_budget_view', 'ai_recommend_view', 'ai_summarize_view',
    'budget_planning'
]
