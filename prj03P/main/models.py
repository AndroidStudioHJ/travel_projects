from django.db import models

class PetProfile(models.Model):
    name = models.CharField(max_length=100)
    animal_type = models.CharField(max_length=50)  # 예: 강아지, 고양이
    personality = models.CharField(max_length=100)  # 예: 활발함, 차분함

    def __str__(self):
        return f"{self.name} ({self.animal_type})"
