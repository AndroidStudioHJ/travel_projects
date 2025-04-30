from django.contrib import admin 
from .models import Destination, Schedule, Budget, Participant, \
                    Place, Transport, TravelOptionCategory, TravelOption, GroupTravel, GroupMember, GroupMessage, City

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
    list_display = ('title', 'destination', 'start_date', 'budget', 'user', 'created_at')
    list_filter = ('destination', 'start_date', 'user')
    search_fields = ('title', 'destination', 'notes')
    date_hierarchy = 'start_date'
    ordering = ('-created_at', '-start_date')
    inlines = [BudgetInline, ParticipantInline, PlaceInline]
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'destination', 'start_date', 'budget', 'notes', 'user')
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
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
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
    list_display = ('name', 'age', 'schedule')
    list_filter = ('age',)
    search_fields = ('name', 'schedule__title')
    fieldsets = (
        ('참여자 정보', {
            'fields': ('schedule', 'name', 'age')
        }),
    )

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'visit_date', 'schedule')
    list_filter = ('visit_date',)
    search_fields = ('name', 'schedule__title')
    fieldsets = (
        ('방문지 정보', {
            'fields': ('schedule', 'name', 'visit_date')
        }),
    )

@admin.register(Transport)
class TransportAdmin(admin.ModelAdmin):
    list_display = ('type', 'departure', 'arrival', 'time', 'schedule')
    list_filter = ('type',)
    search_fields = ('departure', 'arrival', 'schedule__title')
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

class GroupMemberInline(admin.TabularInline):
    model = GroupMember
    extra = 1
    verbose_name = '그룹 멤버'
    verbose_name_plural = '그룹 멤버들'

@admin.register(GroupTravel)
class GroupTravelAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'created_by__username')
    inlines = [GroupMemberInline]
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'description', 'created_by', 'schedule')
        }),
        ('생성/수정 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'is_admin', 'joined_at')
    list_filter = ('is_admin', 'joined_at')
    search_fields = ('group__name', 'user__username')

@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'group__name', 'user__username')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}