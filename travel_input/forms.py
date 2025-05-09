# forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Schedule, TravelStyle, ImportantFactor, Transport, TRAVEL_STYLE_CHOICES, IMPORTANT_CHOICES, Participant

# 참여자 폼셋 수정
ParticipantFormSet = inlineformset_factory(
    Schedule, 
    Participant,
    fields=('gender', 'num_people', 'age_type', 'age_range', 'is_family', 'is_elderly'),
    extra=1,
    can_delete=True,
    widgets={
        'gender': forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }, choices=[
            ('남자', '남자'),
            ('여자', '여자')
        ]),
        'num_people': forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '10',
            'value': '1'
        }),
        'age_type': forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }, choices=[
            ('성인', '성인'),
            ('청소년', '청소년'),
            ('아동', '아동'),
            ('영유아', '영유아')
        ]),
        'age_range': forms.Select(attrs={
            'class': 'form-select'
        }),
        'is_family': forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        'is_elderly': forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    }
)

class TravelSurveyForm(forms.Form):
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
        label="여행 스타일",
        required=False
    )

    important_factors = forms.MultipleChoiceField(
        choices=IMPORTANT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="여행 시 중요 요소",
        required=False
    )

    departure_region = forms.ChoiceField(
        choices=[
            ('', '지역을 선택하세요'),
            ('서울', '서울'),
            ('경기', '경기'),
            ('부산', '부산'),
            ('광주', '광주'),
            ('대전', '대전'),
            ('기타', '기타'),
        ],
        label="출발 지역",
        required=False
    )

    purpose = forms.ChoiceField(
        choices=[
            ('힐링', '힐링'),
            ('가족', '가족 여행'),
            ('커플', '커플 여행'),
            ('친구', '친구와 여행'),
        ],
        label="여행 목적",
        required=False
    )

    pet_friendly = forms.ChoiceField(
        choices=[
            ('yes', '예'),
            ('no', '아니오'),
        ],
        label="반려동물 동반 여부",
        required=False
    )

    transport = forms.ChoiceField(
        choices=[
            ('', '교통수단을 선택하세요'),
            ('KTX', 'KTX'),
            ('버스', '버스'),
            ('비행기', '비행기'),
            ('자동차', '자동차'),
            ('기타', '기타'),
        ],
        label="선호 교통수단",
        required=False
    )

    lodging_request = forms.CharField(
        max_length=200,
        label="숙소 요청사항",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '예: 반려동물 가능, 전망 좋은 방'})
    )

    notes = forms.CharField(
        max_length=1000,
        label="AI 추천 및 메모",
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': '특별히 원하는 사항이 있다면 입력해주세요.'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['destination'].empty_label = "여행지를 선택하세요"
        
        # 기존 인스턴스가 있는 경우
        if self.instance and self.instance.pk:
            # 여행 스타일 초기화
            travel_styles = list(self.instance.travel_styles.values_list('style', flat=True))
            self.initial['travel_style'] = travel_styles
            
            # 중요 요소 초기화
            important_factors = list(self.instance.important_factors.values_list('factor', flat=True))
            self.initial['important_factors'] = important_factors

    def save(self, commit=True):
        schedule = super().save(commit=False)
        
        if commit:
            schedule.save()
            
            # 여행 스타일 저장
            TravelStyle.objects.filter(schedule=schedule).delete()
            for style in self.cleaned_data.get('travel_style', []):
                TravelStyle.objects.create(schedule=schedule, style=style)
            
            # 중요 요소 저장
            ImportantFactor.objects.filter(schedule=schedule).delete()
            for factor in self.cleaned_data.get('important_factors', []):
                ImportantFactor.objects.create(schedule=schedule, factor=factor)
            
            # 교통수단 저장
            Transport.objects.filter(schedule=schedule).delete()
            if self.cleaned_data.get('transport'):
                Transport.objects.create(schedule=schedule, type=self.cleaned_data['transport'])
        
        return schedule

    class Meta:
        model = Schedule
        fields = [
            'title', 'destination', 'start_date', 'end_date', 'budget',
            'departure_region', 'purpose', 'pet_friendly',
            'transport', 'lodging_request', 'notes'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'lodging_request': forms.TextInput(attrs={'placeholder': '예: 반려동물 가능, 전망 좋은 방'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': '특별히 원하는 사항이 있다면 입력해주세요.'})
        }



