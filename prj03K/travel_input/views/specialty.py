from django.shortcuts import render
from travel_input.models import Region

def regional_specialty_view(request):
    regions = Region.objects.prefetch_related('specialties').all()
    return render(request, 'travel_input/regional_specialty.html', {'regions': regions})
