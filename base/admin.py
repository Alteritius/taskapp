from django.contrib import admin
from .models import Task, Profile, CustomGroup, GroupMember, GroupInvite, GroupTask, CheckScheduleActivation
from .models import NotificationTask, NotificationInvite, NotificationGroupTask, NotificationGroup, NotificationDaily


from django.core.mail import EmailMessage

# from django_q.models import Task as TaskDQ
# from django_q.models import Schedule

# from .models import GroupSubtask

# Register your models here.

admin.site.register(Task)

admin.site.register(Profile)

admin.site.register(CustomGroup)

admin.site.register(GroupMember)

admin.site.register(GroupInvite)

admin.site.register(GroupTask)

admin.site.register(NotificationGroupTask)
admin.site.register(NotificationGroup)
admin.site.register(NotificationTask)
admin.site.register(NotificationInvite)
admin.site.register(NotificationDaily)


admin.site.register(CheckScheduleActivation)
# admin.site.register(EmailMessage)
# admin.site.register(GroupSubtask)