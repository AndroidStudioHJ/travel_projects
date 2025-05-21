from django.contrib import admin
from .models import (
    Schedule, Destination,
    TravelPurpose, TravelStyle, ImportantFactor
)

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'start_date', 'end_date', 'created_at')
    list_filter = ('start_date', 'end_date', 'group_type', 'season', 'repeat_visitor', 'event_interest', 'travel_insurance')
    search_fields = ('title', 'destination__name', 'participant_info', 'place_info')
    filter_horizontal = ('travel_purpose', 'travel_style', 'important_factors')  # ✅ ManyToMany 체크박스 UI

    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'destination', 'start_date', 'end_date', 'budget', 'notes')
        }),
        ('카테고리', {
            'fields': ('travel_purpose', 'travel_style', 'important_factors')
        }),
        ('참가자 정보', {
            'fields': ('participant_info', 'age_group', 'group_type')
        }),
        ('장소 정보', {
            'fields': ('place_info', 'preferred_activities', 'event_interest')
        }),
        ('교통 정보', {
            'fields': ('transport_info', 'mobility_needs')
        }),
        ('기타 정보', {
            'fields': ('meal_preference', 'language_support', 'season', 'repeat_visitor', 'travel_insurance')
        }),
        ('AI 관련', {
            'fields': ('ai_response', 'user_feedback', 'ai_feedback_response')
        }),
    )

admin.site.register(TravelPurpose)
admin.site.register(TravelStyle)
admin.site.register(ImportantFactor)
