from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null = True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null = True, blank=True)
    complete = models.BooleanField(default=False)
    create = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True, blank=True) #in the future - change it to (null=True, blank=True) and change not to add seconds
    end_time = models.DateTimeField(null=True, blank=True) #in the future - change it to (null=True, blank=True) (default=timezone.now)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = [ 'complete','start_time'] 