from django.contrib import admin
from .models import Schedule, Destination

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'start_date', 'end_date', 'created_at', 'num_people')
    list_filter = ('start_date', 'end_date', 'group_type', 'season', 'repeat_visitor', 'event_interest', 'travel_insurance')
    search_fields = ('title', 'destination', 'participant_info', 'place_info', 'transport_info', 'preferred_activities', 'meal_preference')
    date_hierarchy = 'start_date'
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'destination', 'start_date', 'end_date', 'budget', 'notes', 'num_people')
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
        ('추가 상세 정보', {
            'fields': ('meal_preference', 'language_support', 'season', 'repeat_visitor', 'travel_insurance')
        }),
    )
