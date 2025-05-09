from django import forms
from .models import TravelPlan

class TravelPlanForm(forms.ModelForm):
    class Meta:
        model = TravelPlan
        fields = ['title', 'location_name', 'latitude', 'longitude', 'date']
