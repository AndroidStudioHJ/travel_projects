from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

# 여행 스타일 선택지
TRAVEL_STYLE_CHOICES = [
    ('자연경관', '자연경관'),
    ('문화 체험', '문화 체험'),
    ('도시 탐방', '도시 탐방'),
    ('액티비티', '액티비티'),
    ('휴식', '휴식'),
]

# 중요 요소 선택지
IMPORTANT_CHOICES = [
    ('숙소', '숙소'),
    ('음식', '음식'),
    ('날씨', '날씨'),
    ('일정 편의성', '일정 편의성'),
    ('현지 문화', '현지 문화'),
]

# Create your models here.

class Destination(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name}, {self.country}"


class Schedule(models.Model):
    title = models.CharField(max_length=200, verbose_name='일정 제목')
    destination = models.CharField(max_length=200, verbose_name='여행지')
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(null=True, blank=True, verbose_name='종료일')
    budget = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name='예산')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules', verbose_name='사용자')
    
    # 여행 정보
    departure_region = models.CharField(max_length=50, null=True, blank=True, verbose_name='출발 지역')
    purpose = models.CharField(max_length=50, null=True, blank=True, verbose_name='여행 목적')
    pet_friendly = models.CharField(max_length=10, null=True, blank=True, verbose_name='반려동물 동반 여부')
    
    # 숙박 정보
    lodging_request = models.CharField(max_length=200, null=True, blank=True, verbose_name='숙소 요청사항')
    
    # 메모 및 요청사항
    notes = models.TextField(max_length=5000, null=True, blank=True, verbose_name='AI 추천 및 메모')
    
    # 시간 정보
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-start_date']
        verbose_name = '여행 일정'
        verbose_name_plural = '여행 일정들'

    def __str__(self):
        return f"{self.title} - {self.destination} ({self.start_date})"


class Budget(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=100)  # 예: 숙박, 교통, 식비 등
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"[{self.schedule.title}] {self.category} - ₩{self.amount}"


class Participant(models.Model):
    AGE_TYPE_CHOICES = [
        ('성인', '성인'),
        ('아동', '아동'),
    ]
    
    AGE_RANGE_CHOICES = [
        ('10대', '10대'),
        ('20대', '20대'),
        ('30대', '30대'),
        ('40대', '40대'),
        ('50대', '50대'),
        ('60대', '60대'),
        ('70대', '70대'),
        ('80대', '80대'),
    ]
    
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='participants')
    gender = models.CharField(max_length=10, choices=[
        ('남자', '남자'),
        ('여자', '여자')
    ], verbose_name='성별', default='남자')
    num_people = models.IntegerField(verbose_name='인원수', default=1)
    age_type = models.CharField(max_length=10, choices=AGE_TYPE_CHOICES, verbose_name='구분', default='성인')
    age_range = models.CharField(max_length=10, choices=AGE_RANGE_CHOICES, verbose_name='연령대', default='20대')
    is_elderly = models.BooleanField(default=False, verbose_name='고령자 여부')
    is_family = models.BooleanField(default=False, verbose_name='가족 여부')

    def __str__(self):
        return f"{self.gender} ({self.num_people}명, {self.age_type}, {self.age_range})"


class Place(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='places')
    name = models.CharField(max_length=200)
    visit_date = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.visit_date}"


class TravelStyle(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='travel_styles')
    style = models.CharField(max_length=50, choices=TRAVEL_STYLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '여행 스타일'
        verbose_name_plural = '여행 스타일'
        unique_together = ('schedule', 'style')

    def __str__(self):
        return f"{self.schedule.title} - {self.style}"


class ImportantFactor(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='important_factors')
    factor = models.CharField(max_length=50, choices=IMPORTANT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '중요 요소'
        verbose_name_plural = '중요 요소'
        unique_together = ('schedule', 'factor')

    def __str__(self):
        return f"{self.schedule.title} - {self.factor}"


class Transport(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='transports')
    type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '교통수단'
        verbose_name_plural = '교통수단'

    def __str__(self):
        return f"{self.schedule.title} - {self.type}"


class TravelOptionCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TravelOption(models.Model):
    category = models.ForeignKey(TravelOptionCategory, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class GroupTravel(models.Model):
    name = models.CharField(max_length=100, verbose_name='그룹명')
    description = models.TextField(verbose_name='그룹 설명')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='joined_groups', through='GroupMember')
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE, related_name='group_travels')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class GroupMember(models.Model):
    group = models.ForeignKey(GroupTravel, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')


class GroupMessage(models.Model):
    group = models.ForeignKey(GroupTravel, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"


class City(models.Model):
    name = models.CharField(max_length=50, verbose_name='도시명')
    slug = models.SlugField(unique=True, verbose_name='슬러그')
    is_active = models.BooleanField(default=True, verbose_name='활성화 여부')
    order = models.IntegerField(default=0, verbose_name='정렬 순서')

    class Meta:
        verbose_name = '도시'
        verbose_name_plural = '도시'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

