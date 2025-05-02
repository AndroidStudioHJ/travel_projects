from django.contrib import admin 
from .models import Destination, Schedule, Budget, Participant, \
                    Place, Transport, TravelOptionCategory, TravelOption, GroupTravel, GroupMember, GroupMessage, City, TravelStyle, ImportantFactor

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
    fields = ('gender', 'num_people', 'age_type', 'age_range', 'is_family', 'is_elderly')
    classes = ('collapse',)

class PlaceInline(admin.TabularInline):
    model = Place
    extra = 1
    verbose_name = '방문지'
    verbose_name_plural = '방문지들'

class TransportInline(admin.TabularInline):
    model = Transport
    extra = 1
    verbose_name = '교통수단'
    verbose_name_plural = '교통수단들'

class TravelStyleInline(admin.TabularInline):
    model = TravelStyle
    extra = 1
    verbose_name = '여행 스타일'
    verbose_name_plural = '여행 스타일들'

class ImportantFactorInline(admin.TabularInline):
    model = ImportantFactor
    extra = 1
    verbose_name = '중요 요소'
    verbose_name_plural = '중요 요소들'

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'start_date', 'end_date', 'total_participants', 'family_groups')
    list_filter = ('destination', 'start_date')
    search_fields = ('title', 'destination__name')
    inlines = [ParticipantInline, BudgetInline, TransportInline, TravelStyleInline, ImportantFactorInline]
    
    def total_participants(self, obj):
        return sum(p.num_people for p in obj.participants.all())
    total_participants.short_description = '총 참여자 수'
    
    def family_groups(self, obj):
        return obj.participants.filter(is_family=True).count()
    family_groups.short_description = '가족 그룹 수'

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
    list_display = ('schedule', 'gender', 'num_people', 'age_type', 'age_range', 'is_family', 'is_elderly')
    list_filter = ('gender', 'age_type', 'is_family', 'is_elderly')
    search_fields = ('schedule__title',)
    ordering = ('schedule', 'age_type')

    fieldsets = (
        ('기본 정보', {
            'fields': ('schedule', 'is_family', 'is_elderly')
        }),
        ('참여자 정보', {
            'fields': ('gender', 'num_people', 'age_type', 'age_range')
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
    list_display = ('schedule', 'type')
    list_filter = ('type',)
    search_fields = ('schedule__title', 'type')
    fieldsets = (
        ('교통 정보', {
            'fields': ('schedule', 'type')
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

@admin.register(TravelStyle)
class TravelStyleAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'style')
    list_filter = ('style',)
    search_fields = ('schedule__title', 'style')
    fieldsets = (
        ('여행 스타일 정보', {
            'fields': ('schedule', 'style')
        }),
    )

@admin.register(ImportantFactor)
class ImportantFactorAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'factor')
    list_filter = ('factor',)
    search_fields = ('schedule__title', 'factor')
    fieldsets = (
        ('중요 요소 정보', {
            'fields': ('schedule', 'factor')
        }),
    )