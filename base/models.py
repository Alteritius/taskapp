from django.db import models
from django.contrib.auth.models import User

from django_q.models import Schedule


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null = True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null = True, blank=True)
    complete = models.BooleanField(default=False)
    create = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    deadline_already_notified = models.BooleanField(default=False)

    STATUS_CHOICES =[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('initiated', 'Initiated'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.title
    
    def is_group_task(self):
        return False
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        from datetime import date
        from django.utils.timezone import make_aware, localdate
        from .background import get_localized_time_now, create_deadline_notification
        

        today_date = date.today()

        localized_time_now = get_localized_time_now()

        end_time_date = localdate(self.end_time)

        if self.deadline_already_notified == False:

            if end_time_date == today_date and self.end_time > localized_time_now:

                name = f"Notification for task: {self.title} {self.id}"

                task_schedule = Schedule.objects.filter(name=name)

                if task_schedule.exists():

                    task_schedule.delete()

                    create_deadline_notification(self)

                else:

                    create_deadline_notification(self)
    
    class Meta:
        ordering = [ 'complete','end_time'] 




def profile_picture_directory_path(instance, filename):

    return f'images/user_{instance.user.id}/{filename}'



class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True) 
    profile_picture = models.ImageField(null=True, default="avatar.svg", upload_to=profile_picture_directory_path)



"""

Groups 

"""



class CustomGroup(models.Model):
    leader = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    participants = models.ManyToManyField(User, related_name='participants', through='GroupMember')
    description = models.TextField(null = True, blank=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [ '-updated', '-created' ]


class GroupMember(models.Model):
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES =[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.user.username


class GroupInvite(models.Model):
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE)
    inviting_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites')
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='obtained_invites')

    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    hidden = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']



def group_files_directory_path(instance, filename):

    print("files updated")

    if instance.id is None:

        return f'temporary/{filename}'

    return f'documents/group_task_{instance.id}/{filename}'

    
class GroupTask(models.Model):
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    member = models.ForeignKey(GroupMember, on_delete=models.CASCADE, related_name="worker", default=None)
    title = models.CharField(max_length=200)
    description = models.TextField(null = True, blank=True)
    overdue = models.BooleanField(default=False)

    group_files = models.FileField(null=True, blank=True, upload_to=group_files_directory_path)

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    deadline_already_notified = models.BooleanField(default=False)

    STATUS_CHOICES =[
        ('pending', 'Pending'),
        ('initiated', 'Initiated'),
        ('finished', 'Finished'),
        ('overdue', 'Overdue'),
        ('need adjustments', 'Need Adjustments'),
        ('verified', 'Verified'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def is_group_task(self):
        return True
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from datetime import date
        from django.utils.timezone import make_aware, localdate
        from .background import get_localized_time_now, create_deadline_notification

        today_date = date.today()
        localized_time_now = get_localized_time_now()
        end_time_date = localdate(self.end_time)
        if self.deadline_already_notified == False:

            if end_time_date == today_date and self.end_time > localized_time_now:

                name = f"Notification for group task: {self.title} {self.id}"
                task_schedule = Schedule.objects.filter(name=name)
                if task_schedule.exists():

                    task_schedule.delete()

                    create_deadline_notification(self)

                else:

                    create_deadline_notification(self)
    
    class Meta:
        ordering = ['end_time'] 



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    seen = models.BooleanField(default=False)
    not_type = models.CharField(max_length=50, default='')
    
    link = models.BooleanField(default=False)
    changed = models.CharField(max_length=200, null=True, blank=True)




    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class NotificationTask(Notification):
    related_to = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)


class NotificationGroupTask(Notification):
    related_to = models.ForeignKey(GroupTask, on_delete=models.SET_NULL, null=True)


class NotificationGroupTaskHistory(Notification):
    related_to = models.ForeignKey(GroupTask, on_delete=models.CASCADE)
    

class NotificationGroup(Notification):
    related_to = models.ForeignKey(CustomGroup, on_delete=models.SET_NULL, null=True)


class NotificationInvite(Notification):
    related_to = models.ForeignKey(GroupInvite, on_delete=models.SET_NULL, null=True)

    
class NotificationDaily(Notification):
    related_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="related_to")



class CheckScheduleActivation(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    date = models.DateField()



