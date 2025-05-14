from django import forms
from .models import Schedule, Destination

# 여행 목적 선택지
TRAVEL_PURPOSE_CHOICES = [
    ('healing', '휴식'),
    ('sightseeing', '관광'),
    ('adventure', '모험'),
    ('photo', '사진 촬영'),
    ('family', '가족 여행'),
    ('couple', '커플 여행'),
    ('culture', '문화 체험'),
    ('food', '먹거리 탐방'),
    ('selfdev', '자기 개발'),
    ('shopping', '쇼핑'),
]

# 여행 스타일 선택지
TRAVEL_STYLE_CHOICES = [
    ('nature', '자연경관'),
    ('city', '도시 탐방'),
    ('culture', '문화 체험'),
    ('activity', '액티비티'),
    ('relax', '휴식과 힐링'),
]

# 여행 시 중요 요소
IMPORTANT_CHOICES = [
    ('stay', '숙소'),
    ('food', '음식'),
    ('weather', '날씨'),
    ('schedule', '일정 편의성'),
    ('culture', '현지 문화'),
]

class ScheduleForm(forms.ModelForm):
    # JSONField와 매핑될 체크박스 필드들
    travel_purpose = forms.MultipleChoiceField(
        choices=TRAVEL_PURPOSE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="여행 목적 (복수 선택 가능)"
    )
    travel_style = forms.MultipleChoiceField(
        choices=TRAVEL_STYLE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="여행 스타일 (복수 선택 가능)"
    )
    important_factors = forms.MultipleChoiceField(
        choices=IMPORTANT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="중요 요소 (복수 선택 가능)"
    )

    class Meta:
        model = Schedule
        fields = [
            'title',
            'destination',
            'start_date',
            'end_date',
            'travel_purpose',
            'travel_style',
            'important_factors',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'destination': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['destination'].empty_label = "여행지를 선택하세요"

    def clean_travel_purpose(self):
        return self.cleaned_data.get('travel_purpose', [])

    def clean_travel_style(self):
        return self.cleaned_data.get('travel_style', [])

    def clean_important_factors(self):
        return self.cleaned_data.get('important_factors', [])
