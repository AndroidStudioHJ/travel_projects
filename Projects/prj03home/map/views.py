from django.shortcuts import render
from .models import TravelPlan
import folium

# Create your views here.

def travel_map(request):
    # 로그인한 사용자의 일정만 가져옴
    plans = TravelPlan.objects.filter(user=request.user)

    m = folium.Map(location=[36.5, 127.5], zoom_start=7)

    for plan in plans:
        folium.Marker(
            location=[plan.latitude, plan.longitude],
            popup=f"{plan.title} ({plan.date})",
            tooltip=plan.location_name
        ).add_to(m)

    m.save('templates/travel/travel_map.html')
    return render(request, 'travel/map_wrap.html')
