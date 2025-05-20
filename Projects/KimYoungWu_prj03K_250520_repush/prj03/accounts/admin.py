from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # 사용자 목록에 표시할 필드
    list_display = ('username', 'email', 'gender', 'phone_number', 'is_staff', 'is_active')
    
    # 사용자 상세 페이지에서 필드 설정
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('gender', 'phone_number')}),
    )
    
    # 사용자 추가 페이지에서 필드 설정
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('추가 정보', {'fields': ('gender', 'phone_number')}),
    )
    
    # 사용자 목록 필터링
    list_filter = ('is_active', 'is_staff', 'gender')

    # 사용자 검색할 때 사용할 필드 설정
    search_fields = ('username', 'email', 'phone_number')

    # 사용자 목록에서 필드 순서 설정
    ordering = ('username',)
