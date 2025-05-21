from django.urls import path
from . import views

app_name = 'travel'

urlpatterns = [
    path('map/', views.travel_map, name='map'),                 # 지도 + 일정 목록
]