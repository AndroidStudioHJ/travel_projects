from django.urls import path
from .views import SentimentAnalysisView

app_name = 'blog'

urlpatterns = [
    path('sentiment/', SentimentAnalysisView.as_view(), name='sentiment_analysis'),
] 