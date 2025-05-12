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
    # 기본 정보
    title = models.CharField(max_length=200, verbose_name='일정 제목')
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="여행지")
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(null=True, blank=True, verbose_name='종료일')
    budget = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name='예산')
    notes = models.TextField(max_length=5000, null=True, blank=True, verbose_name='메모')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules', verbose_name='사용자')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 참가자 정보
    participant_info = models.TextField(
        verbose_name='참가자', 
        help_text='참가자 이름과 나이를 입력하세요 (예: 홍길동(30), 김철수(25))',
        null=True,
        blank=True,
        default=''
    )

    # 장소 정보
    place_info = models.TextField(
        verbose_name='방문 장소', 
        help_text='방문할 장소와 날짜를 입력하세요 (예: 남산타워(2024-03-20), 경복궁(2024-03-21))',
        null=True,
        blank=True,
        default=''
    )

    # 교통 정보
    transport_info = models.TextField(
        verbose_name='교통 정보', 
        help_text='교통편, 출발지, 도착지, 시간을 입력하세요 (예: KTX, 서울역, 부산역, 2024-03-20 09:00)',
        null=True,
        blank=True,
        default=''
    )

    # 추가 상세 정보
    age_group = models.CharField(
        max_length=50,
        verbose_name='연령대',
        help_text='예: 20대, 30대, 60대 이상 등',
        null=True,
        blank=True,
        default=''
    )

    group_type = models.CharField(
        max_length=50,
        verbose_name='여행 동행 형태',
        help_text='가족, 친구, 커플, 혼자 등',
        null=True,
        blank=True,
        default=''
    )

    preferred_activities = models.TextField(
        verbose_name='선호 활동',
        help_text='예: 온천, 쇼핑, 등산, 박물관 등',
        null=True,
        blank=True,
        default=''
    )

    meal_preference = models.TextField(
        verbose_name='음식 선호',
        help_text='예: 한식, 채식, 미식 여행 등',
        null=True,
        blank=True,
        default=''
    )

    language_support = models.BooleanField(
        verbose_name='언어 지원 필요',
        help_text='영어 가능 가이드 요청 등',
        default=False
    )

    season = models.CharField(
        max_length=50,
        verbose_name='희망 계절',
        help_text='봄, 여름, 가을, 겨울 등',
        null=True,
        blank=True,
        default=''
    )

    repeat_visitor = models.BooleanField(
        verbose_name='재방문 여부',
        help_text='해당 지역 방문 경험 (처음/재방문)',
        default=False
    )

    mobility_needs = models.TextField(
        verbose_name='이동 관련 요구',
        help_text='예: 휠체어 접근성, 편안한 이동 동선 등',
        null=True,
        blank=True,
        default=''
    )

    event_interest = models.BooleanField(
        verbose_name='현지 이벤트/축제 관심',
        default=False
    )

    travel_insurance = models.BooleanField(
        verbose_name='여행자 보험 가입',
        help_text='여행자 보험 가입 여부 또는 희망 여부',
        default=False
    )

    class Meta:
        ordering = ['-created_at', '-start_date']
        verbose_name = '여행 일정'
        verbose_name_plural = '여행 일정들'

    def __str__(self):
        return f"{self.title} - {self.destination} ({self.start_date})"


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
