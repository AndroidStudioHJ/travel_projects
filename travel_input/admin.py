from django.contrib import admin 
from .models import Destination, Schedule, Budget, Participant, \
                    Place, Transport, TravelOptionCategory, TravelOption

# Register your models here.
class BudgetInline(admin.TabularInline):
    model = Budget
    extra = 1
    verbose_name = '예산 항목'
    verbose_name_plural = '예산 항목들'

class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 1
    verbose_name = '참여자'
    verbose_name_plural = '참여자들'

class PlaceInline(admin.TabularInline):
    model = Place
    extra = 1
    verbose_name = '방문지'
    verbose_name_plural = '방문지들'

class TransportInline(admin.TabularInline):
    model = Transport
    extra = 1


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'start_date', 'end_date', 'budget', 'user', 'created_at')
    list_display_links = ('title',)
    search_fields = ('title', 'destination', 'user__username')
    list_filter = ('start_date', 'end_date', 'user')
    inlines = [BudgetInline, ParticipantInline, PlaceInline]
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'destination', 'start_date', 'end_date', 'budget', 'notes', 'user')
        }),
        ('생성/수정 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


class TravelOptionInline(admin.TabularInline):
    model = TravelOption
    extra = 1

@admin.register(TravelOptionCategory)
class TravelOptionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    fieldsets = (
        ('여행 옵션 카테고리', {
            'fields': ('name',)
        }),
    )

@admin.register(TravelOption)
class TravelOptionAdmin(admin.ModelAdmin):
    list_display = ('category', 'name')
    list_filter = ('category',)
    search_fields = ('name',)
    fieldsets = (
        ('여행 옵션', {
            'fields': ('category', 'name')
        }),
    )

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'category', 'amount')
    list_filter = ('category',)
    search_fields = ('schedule__title', 'category')
    fieldsets = (
        ('예산 정보', {
            'fields': ('schedule', 'category', 'amount')
        }),
    )

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'name', 'age')
    list_filter = ('schedule',)
    search_fields = ('name',)
    fieldsets = (
        ('참여자 정보', {
            'fields': ('schedule', 'name', 'age')
        }),
    )

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'name', 'visit_date')
    list_filter = ('schedule',)
    search_fields = ('name',)
    fieldsets = (
        ('방문지 정보', {
            'fields': ('schedule', 'name', 'visit_date')
        }),
    )

@admin.register(Transport)
class TransportAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'type', 'departure', 'arrival', 'time')
    list_filter = ('schedule', 'type')
    search_fields = ('departure', 'arrival')
    fieldsets = (
        ('교통 정보', {
            'fields': ('schedule', 'type', 'departure', 'arrival', 'time')
        }),
    )

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name', 'country')
    fieldsets = (
        ('목적지 정보', {
            'fields': ('name', 'country')
        }),
    )