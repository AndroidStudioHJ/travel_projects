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

COMPANION_CHOICES = [
    ('alone', '혼자'),
    ('family', '가족'),
    ('friend', '친구'),
    ('lover', '연인'),
    ('group', '단체'),
]

IMPORTANT_CHOICES = [
    ('stay', '숙소'),
    ('food', '음식'),
    ('weather', '날씨'),
    ('schedule', '일정 편의성'),
    ('culture', '현지 문화'),
]

class TravelSurveyForm(forms.Form):
    travel_style = forms.ChoiceField(
        choices=TRAVEL_STYLE_CHOICES,
        widget=forms.RadioSelect,
        label="선호하는 여행 스타일"
    )
    destination = forms.CharField(
        max_length=100,
        label="가고 싶은 여행지",
        widget=forms.TextInput(attrs={'placeholder': '예: 파리, 제주도'})
    )
    companion = forms.ChoiceField(
        choices=COMPANION_CHOICES,
        widget=forms.RadioSelect,
        label="여행 동반자"
    )
    important_factors = forms.MultipleChoiceField(
        choices=IMPORTANT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="여행 시 중요 요소 (복수 선택 가능)"
    )


class ScheduleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['destination'].empty_label = "여행지를 선택하세요"

    class Meta:
        model = Schedule
        fields = ['title', 'destination', 'start_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }



