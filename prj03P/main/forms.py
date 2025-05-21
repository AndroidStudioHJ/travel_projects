from django import forms

class PetTravelForm(forms.Form):
    PET_CHOICES = [
        ('dog', '강아지'),
        ('cat', '고양이'),
        ('other', '기타'),
    ]

    ACTIVITY_CHOICES = [
        ('low', '낮음'),
        ('medium', '보통'),
        ('high', '높음'),
    ]

    SEASON_CHOICES = [
        ('spring', '봄'),
        ('summer', '여름'),
        ('fall', '가을'),
        ('winter', '겨울'),
    ]

    pet_type = forms.ChoiceField(choices=PET_CHOICES, label="반려동물 종류")
    activity_level = forms.ChoiceField(choices=ACTIVITY_CHOICES, label="활동 수준")
    season = forms.ChoiceField(choices=SEASON_CHOICES, label="여행 시기")
