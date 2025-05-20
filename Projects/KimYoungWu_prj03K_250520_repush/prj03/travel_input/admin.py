from django.contrib import admin
from .models import (
    Schedule, Destination, AIRecommendation,
    Budget, Participant, Place, Transport,
    Category, CultureCategory, GroupTravel,
    GroupMember, GroupMessage, TravelOption,
    TravelOptionCategory, City, Region, Specialty
)

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'start_date', 'end_date', 'created_at')
    list_filter = ('start_date', 'end_date', 'group_type', 'season', 'repeat_visitor', 'event_interest', 'travel_insurance')
    search_fields = ('title', 'destination__name', 'participant_info', 'place_info', 'transport_info', 'preferred_activities', 'meal_preference')
    date_hierarchy = 'start_date'
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'destination', 'start_date', 'end_date', 'budget', 'notes')
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


@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'recommendation_type', 'created_at')
    list_filter = ('recommendation_type', 'created_at')
    search_fields = ('title', 'prompt', 'result_text', 'user__username')
    readonly_fields = ('created_at',)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['name', 'region']
    search_fields = ['name', 'region__name']
    list_filter = ['region']

# ✅ 나머지 모델 간단 등록
admin.site.register(Budget)
admin.site.register(Participant)
admin.site.register(Place)
admin.site.register(Transport)
admin.site.register(Category)
admin.site.register(CultureCategory)
admin.site.register(GroupTravel)
admin.site.register(GroupMember)
admin.site.register(GroupMessage)
admin.site.register(TravelOption)
admin.site.register(TravelOptionCategory)
admin.site.register(City)
