# forms.py
from django import forms
from .models import Schedule

TRAVEL_STYLE_CHOICES = [
    ('nature', '자연경관'),
    ('city', '도시 탐방'),
    ('culture', '문화 체험'),
    ('activity', '액티비티'),
    ('relax', '휴식과 힐링'),
]

IMPORTANT_CHOICES = [
    ('stay', '숙소'),
    ('food', '음식'),
    ('weather', '날씨'),
    ('schedule', '일정 편의성'),
    ('culture', '현지 문화'),
]

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

class ScheduleForm(forms.ModelForm):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['destination'].empty_label = "여행지를 선택하세요"

    class Meta:
        model = Schedule
        fields = ['title', 'destination', 'start_date', 'end_date', 'num_people', 'budget']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }



