from django.db import models
from django.conf import settings

class CultureCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Destination(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="\uc5ec\ud589\uc9c0\uba85")
    def __str__(self):
        return self.name

class TravelPurpose(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class TravelStyle(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class ImportantFactor(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Schedule(models.Model):
    title = models.CharField(max_length=200, verbose_name='\uc77c\uc815 \uc81c\ubaa9')
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="\uc5ec\ud589\uc9c0")
    start_date = models.DateField(verbose_name='\uc2dc\uc791\uc77c')
    end_date = models.DateField(null=True, blank=True, verbose_name='\uc885\ub8cc\uc77c')
    budget = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name='\uc608\uc0b0')
    notes = models.TextField(max_length=5000, null=True, blank=True, verbose_name='\uba54\ubaa8')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules', verbose_name='\uc0ac\uc6a9\uc790')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    favorite = models.BooleanField(default=False, verbose_name='\uc990\uaca8\ucc3e\uae30 \uc720\ubb34')

    travel_purpose = models.ManyToManyField(TravelPurpose, blank=True, verbose_name="\uc5ec\ud589 \ubaa9\uc801")
    travel_style = models.ManyToManyField(TravelStyle, blank=True, verbose_name="\uc5ec\ud589 \uc2a4\ud0c0\uc77c")
    important_factors = models.ManyToManyField(ImportantFactor, blank=True, verbose_name="\uc911\uc694 \uc694\uc18c")

    participant_info = models.TextField(null=True, blank=True, default='', verbose_name='\ucc38\uac00\uc790')
    place_info = models.TextField(null=True, blank=True, default='', verbose_name='\ubc29\ubb38 \uc7a5\uc18c')
    transport_info = models.TextField(null=True, blank=True, default='', verbose_name='\uad50\ud1b5 \uc815\ubcf4')
    age_group = models.CharField(max_length=50, null=True, blank=True, default='', verbose_name='\uc5f0\ub839\ub300')
    group_type = models.CharField(max_length=50, null=True, blank=True, default='', verbose_name='\uc5ec\ud589 \ub3d9\ud589 \ud615\ud0dc')
    preferred_activities = models.TextField(null=True, blank=True, default='', verbose_name='\uc120\ud638 \ud65c\ub3d9')
    meal_preference = models.TextField(null=True, blank=True, default='', verbose_name='\uc74c\uc2dd \uc120\ud638')
    language_support = models.BooleanField(default=False, verbose_name='\uc5b8\uc5b4 \uc9c0\uc6d0 \ud544\uc694')
    season = models.CharField(max_length=50, null=True, blank=True, default='', verbose_name='\ud76c\ub9dd \uacc4\uc808')
    repeat_visitor = models.BooleanField(default=False, verbose_name='\uc7ac\ubc29\ubb38 \uc720\ubb34')
    mobility_needs = models.TextField(null=True, blank=True, default='', verbose_name='\uc774\ub3d9 \uad00\ub828 \uc694\uad6c')
    event_interest = models.BooleanField(default=False, verbose_name='\ud604\uc9c0 \uc774\ubca4\ud2b8/\ucd95\uc81c \uad00\uc2ec')
    travel_insurance = models.BooleanField(default=False, verbose_name='\uc5ec\ud589\uc790 \ubcf4\ud5d8 \uac00\uc785')

    ai_response = models.TextField(null=True, blank=True, verbose_name='AI \uc0dd\uc131 \uacb0\uacfc')
    user_feedback = models.TextField(null=True, blank=True, verbose_name='\uc0ac\uc6a9\uc790 \ud53c\ub4dc\ub9bd')
    ai_feedback_response = models.TextField(null=True, blank=True, verbose_name='AI \uac1c\uc804 \uc81c\uc548')

    class Meta:
        ordering = ['-created_at', '-start_date']
        verbose_name = '\uc5ec\ud589 \uc77c\uc815'
        verbose_name_plural = '\uc5ec\ud589 \uc77c\uc815\ub4e4'

    def __str__(self):
        return f"{self.title} - {self.destination} ({self.start_date})"

class Budget(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"[{self.schedule.title}] {self.category} - \u20a9{self.amount}"

class Participant(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='participants')
    name = models.CharField(max_length=100)
    age = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return f"{self.name} ({self.schedule.title})"

class Place(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='places')
    name = models.CharField(max_length=200)
    visit_date = models.DateField()
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='\uce74\ud14c\uace0\ub9ac')
    def __str__(self):
        return f"{self.name} - {self.visit_date}"

class Transport(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='transports')
    type = models.CharField(max_length=50)
    departure = models.CharField(max_length=100)
    arrival = models.CharField(max_length=100)
    time = models.DateTimeField()
    def __str__(self):
        return f"{self.type} ({self.departure} \u2192 {self.arrival})"

class TravelOptionCategory(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class TravelOption(models.Model):
    category = models.ForeignKey(TravelOptionCategory, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.category.name} - {self.name}"

class GroupTravel(models.Model):
    name = models.CharField(max_length=100, verbose_name='\uadf8\ub8f9\uba85')
    description = models.TextField(verbose_name='\uadf8\ub8f9 \uc124\uba85')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='joined_groups', through='GroupMember')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='group_travels')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class GroupMember(models.Model):
    group = models.ForeignKey(GroupTravel, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('group', 'user')

class GroupMessage(models.Model):
    group = models.ForeignKey(GroupTravel, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"

class City(models.Model):
    name = models.CharField(max_length=50, verbose_name='\ub3c4\uc2dc\uba85')
    slug = models.SlugField(unique=True, verbose_name='\uc2ac\ub7ec\uadf8')
    is_active = models.BooleanField(default=True, verbose_name='\ud65c\uc131\ud654 \uc720\ubb34')
    order = models.IntegerField(default=0, verbose_name='\uc815\ub82c \uc21c\uc11c')
    class Meta:
        verbose_name = '\ub3c4\uc2dc'
        verbose_name_plural = '\ub3c4\uc2dc'
        ordering = ['order', 'name']
    def __str__(self):
        return self.name