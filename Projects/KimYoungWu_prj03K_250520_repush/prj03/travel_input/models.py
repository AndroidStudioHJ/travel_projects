from django.db import models
from django.conf import settings

# ✅ 문화 카테고리 모델
class CultureCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

# ✅ 장소 카테고리
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Destination(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="여행지명")
    def __str__(self):
        return self.name

class Schedule(models.Model):
    title = models.CharField(max_length=200, verbose_name='일정 제목')
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="여행지")
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(null=True, blank=True, verbose_name='종료일')
    budget = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name='예산')
    notes = models.TextField(max_length=5000, null=True, blank=True, verbose_name='메모')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules', verbose_name='사용자')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    participant_info = models.TextField(verbose_name='참가자', null=True, blank=True, default='')
    place_info = models.TextField(verbose_name='방문 장소', null=True, blank=True, default='')
    transport_info = models.TextField(verbose_name='교통 정보', null=True, blank=True, default='')
    age_group = models.CharField(max_length=50, verbose_name='연령대', null=True, blank=True, default='')
    group_type = models.CharField(max_length=50, verbose_name='여행 동행 형태', null=True, blank=True, default='')
    preferred_activities = models.TextField(verbose_name='선호 활동', null=True, blank=True, default='')
    meal_preference = models.TextField(verbose_name='음식 선호', null=True, blank=True, default='')
    language_support = models.BooleanField(verbose_name='언어 지원 필요', default=False)
    season = models.CharField(max_length=50, verbose_name='희망 계절', null=True, blank=True, default='')
    repeat_visitor = models.BooleanField(verbose_name='재방문 여부', default=False)
    mobility_needs = models.TextField(verbose_name='이동 관련 요구', null=True, blank=True, default='')
    event_interest = models.BooleanField(verbose_name='현지 이벤트/축제 관심', default=False)
    travel_insurance = models.BooleanField(verbose_name='여행자 보험 가입', default=False)

    class Meta:
        ordering = ['-created_at', '-start_date']
        verbose_name = '여행 일정'
        verbose_name_plural = '여행 일정들'

    def __str__(self):
        return f"{self.title} - {self.destination} ({self.start_date})"

    @property
    def budget_rounded(self):
        if self.budget:
            return round(self.budget, -3)
        return 0

class Budget(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"[{self.schedule.title}] {self.category} - ₩{self.amount}"

class Participant(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='participants')
    name = models.CharField(max_length=100)
    age = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return f"{self.name} ({self.schedule.title})"

class Place(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='places')
    name = models.CharField(max_length=200)
    visit_date = models.DateField()
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='카테고리')
    def __str__(self):
        return f"{self.name} - {self.visit_date}"

class Transport(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='transports')
    type = models.CharField(max_length=50)
    departure = models.CharField(max_length=100)
    arrival = models.CharField(max_length=100)
    time = models.DateTimeField()
    def __str__(self):
        return f"{self.type} ({self.departure} → {self.arrival})"

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

class AIRecommendation(models.Model):
    RECOMMEND_TYPE_CHOICES = [
        ('schedule', '일정 추천'),
        ('budget', '예산 분배'),
        ('places', '장소 추천'),
        ('summary', '요약'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    prompt = models.TextField()
    result_text = models.TextField()
    result_json = models.JSONField(null=True, blank=True)
    recommendation_type = models.CharField(max_length=50, choices=RECOMMEND_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.title} - {self.recommendation_type} ({self.user.username})"

# ✅ 지역 및 특산물
class Region(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='지역명')
    def __str__(self):
        return self.name

class Specialty(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='specialties', verbose_name='지역')
    name = models.CharField(max_length=100, verbose_name='특산물명')
    description = models.TextField(blank=True, verbose_name='설명')
    def __str__(self):
        return f"{self.region.name} - {self.name}"
