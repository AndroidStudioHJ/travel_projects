# home/models.py

from django.db import models
from django.contrib.auth.models import User

class Destination(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    tags = models.JSONField(default=list)  # ['해변', '문화', '산']

    def __str__(self):
        return self.name

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # null 허용
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    content = models.TextField()
    sentiment = models.CharField(max_length=10, blank=True)  # '긍정', '부정', '중립'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.destination.name}"
