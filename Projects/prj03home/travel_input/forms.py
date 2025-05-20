from django import forms
from .models import Schedule, Destination

# 여행 스타일 선택
TRAVEL_STYLE_CHOICES = [
    ('nature', '자연경관'),
    ('city', '도시 탐방'),
    ('culture', '문화 체험'),
    ('activity', '액티비티'),
    ('relax', '휴식과 힐링'),
]

# 중요 요소 선택
IMPORTANT_CHOICES = [
    ('stay', '숙소'),
    ('food', '음식'),
    ('weather', '날씨'),
    ('schedule', '일정 편의성'),
    ('culture', '현지 문화'),
]

# 1. AI 맞춤 질문 기반 폼
class AITravelConsultForm(forms.Form):
    destination = forms.CharField(
        label="어디로 가고 싶으신가요?",
        max_length=100
    )
    duration = forms.CharField(
        label="여행 기간은 어떻게 되시나요? (예: 당일치기, 1박 2일 등)",
        max_length=100
    )
    departure = forms.CharField(
        label="어디에서 출발하시나요?",
        max_length=100
    )
    companions = forms.CharField(
        label="누구와 함께 여행하시나요?",
        max_length=100
    )
    date = forms.CharField(
        label="여행 예정일은 언제인가요?",
        max_length=100
    )
    theme = forms.CharField(
        label="가장 중요하게 생각하는 테마나 활동은 무엇인가요?",
        max_length=200
    )
    style = forms.CharField(
        label="여행은 여유롭게? 아니면 다양한 곳을 둘러보기?",
        max_length=100
    )

# 2. 기존 설문 폼
class TravelSurveyForm(forms.Form):
    travel_style = forms.MultipleChoiceField(
        choices=TRAVEL_STYLE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="선호하는 여행 스타일 (복수 선택 가능)"
    )
    important_factors = forms.MultipleChoiceField(
        choices=IMPORTANT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="여행 시 중요 요소 (복수 선택 가능)"
    )
    num_people = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=1,
        label="여행 인원수"
    )
    budget = forms.DecimalField(
        min_value=0,
        max_digits=10,
        decimal_places=0,
        label="예산 (원)"
    )

# 3. 기존 일정 생성 폼
class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = [
            'title', 'destination', 'start_date', 'end_date',
            'budget', 'notes', 'participant_info', 'age_group', 'group_type',
            'place_info', 'preferred_activities', 'event_interest',
            'transport_info', 'mobility_needs',
            'meal_preference', 'language_support', 'season',
            'repeat_visitor', 'travel_insurance'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'budget': forms.NumberInput(attrs={
                'placeholder': '예: 300000',
                'step': '1000',
                'min': 0,
            }),
            'participant_info': forms.Textarea(attrs={'rows': 3, 'placeholder': '참가자 이름과 나이를 입력하세요 (예: 홍길동(30), 김철수(25))'}),
            'place_info': forms.Textarea(attrs={'rows': 3, 'placeholder': '방문할 장소와 날짜를 입력하세요 (예: 남산타워(2024-03-20), 경복궁(2024-03-21))'}),
            'transport_info': forms.Textarea(attrs={'rows': 3, 'placeholder': '교통편, 출발지, 도착지, 시간을 입력하세요 (예: KTX, 서울역, 부산역, 2024-03-20 09:00)'}),
            'preferred_activities': forms.Textarea(attrs={'rows': 3, 'placeholder': '예: 온천, 쇼핑, 등산, 박물관 등'}),
            'meal_preference': forms.Textarea(attrs={'rows': 3, 'placeholder': '예: 한식, 채식, 미식 여행 등'}),
            'mobility_needs': forms.Textarea(attrs={'rows': 3, 'placeholder': '예: 휠체어 접근성, 편안한 이동 동선 등'}),
            'age_group': forms.Select(choices=[
                ('', '선택하세요'),
                ('10대', '10대'),
                ('20대', '20대'),
                ('30대', '30대'),
                ('40대', '40대'),
                ('50대', '50대'),
                ('60대 이상', '60대 이상'),
            ]),
            'group_type': forms.Select(choices=[
                ('', '선택하세요'),
                ('혼자', '혼자'),
                ('가족', '가족'),
                ('친구', '친구'),
                ('커플', '커플'),
                ('단체', '단체'),
            ]),
            'season': forms.Select(choices=[
                ('', '선택하세요'),
                ('봄', '봄'),
                ('여름', '여름'),
                ('가을', '가을'),
                ('겨울', '겨울'),
            ]),
            'destination': forms.Select(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'budget': '예산은 천 원 단위로 입력해주세요. 예: 300000 → 300,000원',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['destination'].empty_label = "여행지를 선택하세요"

    def clean_budget(self):
        budget = self.cleaned_data.get('budget')
        if budget:
            return round(budget, -3)  # 천 단위 반올림
        return 0
