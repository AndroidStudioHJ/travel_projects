from django.db import models

# Create your models here.

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    link = models.URLField()
    summary = models.TextField()
    date = models.CharField(max_length=50)
    sentiment = models.CharField(max_length=10, choices=[
        ('positive', '긍정'),
        ('negative', '부정'),
        ('neutral', '중립')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
