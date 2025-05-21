from django.urls import path
from .views import blog_sentiment, travel_survey

urlpatterns = [
    path("", travel_survey, name="home"),
    path("travel-survey/", travel_survey, name="travel_survey"),
    path("blog-sentiment/", blog_sentiment, name="blog_sentiment"),
]

