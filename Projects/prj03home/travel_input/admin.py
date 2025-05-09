from django.contrib import admin
from .models import (
    Destination, Schedule, Budget, Participant, Place, Transport,
    TravelOptionCategory, TravelOption, GroupTravel, GroupMember,
    GroupMessage, City, Category, CultureCategory  # ✅ 포함됨
)

class BudgetInline(admin.TabularInline):
    model = Budget
    extra = 1

class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 1

class PlaceInline(admin.TabularInline):
    model = Place
    extra = 1

class TransportInline(admin.TabularInline):
    model = Transport
    extra = 1

class GroupMemberInline(admin.TabularInline):
    model = GroupMember
    extra = 1

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'start_date', 'budget', 'user', 'created_at')
    list_filter = ('destination', 'start_date', 'user')
    search_fields = ('title', 'destination', 'notes')
    date_hierarchy = 'start_date'
    ordering = ('-created_at', '-start_date')
    inlines = [BudgetInline, ParticipantInline, PlaceInline]
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'destination', 'start_date', 'end_date', 'budget', 'notes', 'tag', 'user')
        }),
        ('생성/수정 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TravelOptionCategory)
class TravelOptionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(TravelOption)
class TravelOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'category', 'amount')
    list_filter = ('category',)
    search_fields = ('schedule__title', 'category')

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'schedule')
    list_filter = ('age',)
    search_fields = ('name', 'schedule__title')

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'visit_date', 'schedule')
    list_filter = ('visit_date',)
    search_fields = ('name', 'schedule__title')

@admin.register(Transport)
class TransportAdmin(admin.ModelAdmin):
    list_display = ('type', 'departure', 'arrival', 'time', 'schedule')
    list_filter = ('type',)
    search_fields = ('departure', 'arrival', 'schedule__title')

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name', 'country')

@admin.register(GroupTravel)
class GroupTravelAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'created_by__username')
    inlines = [GroupMemberInline]
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'description', 'created_by', 'schedule')
        }),
        ('생성/수정 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

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

# ✅ 문화 카테고리 등록
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(CultureCategory)
class CultureCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
