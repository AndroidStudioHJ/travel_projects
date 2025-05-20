from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # 루트 경로
    path('destination/<int:dest_id>/comment/', views.write_comment, name='write_comment'),
    path('recommend/', views.recommend, name='recommend'),
]
