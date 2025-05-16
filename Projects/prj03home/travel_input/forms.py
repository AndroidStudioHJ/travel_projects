from django import forms
from .models import Schedule, Destination, TravelPurpose, TravelStyle, ImportantFactor

class ScheduleForm(forms.ModelForm):
    travel_purpose = forms.ModelMultipleChoiceField(
        queryset=TravelPurpose.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="여행 목적"
    )

    travel_style = forms.ModelMultipleChoiceField(
        queryset=TravelStyle.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="여행 스타일"
    )

    important_factors = forms.ModelMultipleChoiceField(
        queryset=ImportantFactor.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="중요 요소"
    )

    class Meta:
        model = Schedule
        fields = [
            'title', 'destination', 'start_date', 'end_date',
            'travel_purpose', 'travel_style', 'important_factors',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['destination'].empty_label = "여행지를 선택하세요"
