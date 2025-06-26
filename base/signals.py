from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, GroupTask, GroupInvite, NotificationInvite
from django.conf import settings
import shutil
import os


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    
    instance.profile.save()

@receiver(post_save, sender=GroupInvite)
def create_or_update_invite(sender, instance, **kwargs):
    if instance.accepted == False and instance.rejected == False:
        title = f'New Invite, for Group: {instance.group.name}'
        description = f'Group leader: "{instance.inviting_user}" sent you an invite to the Group: "{instance.group.name}"'
        receipient = instance.invited_user
        not_type = 'invite'

        link = True

        NotificationInvite.objects.create(user=receipient, related_to=instance, title=title, description=description, not_type=not_type, link=link)

    elif instance.accepted == True and instance.rejected == False:
        title = f'Your Invite was accepted'
        description = f'Your invite sent to: "{instance.invited_user}" for the group: "{instance.group.name}" was accepted'
        receipient = instance.inviting_user
        not_type = 'invite'
        link = True

        NotificationInvite.objects.create(user=receipient, related_to=instance, title=title, description=description, not_type=not_type, link=link)

    elif instance.accepted == False and instance.rejected == True:
        title = f'Your Invite was rejected'
        description = f'Your invite sent to: "{instance.invited_user}" for the group: "{instance.group.name}" was rejected'
        receipient = instance.inviting_user
        not_type = 'invite'
        link = True

        NotificationInvite.objects.create(user=receipient, related_to=instance, title=title, description=description, not_type=not_type, link=link)


@receiver(post_delete, sender=GroupTask)
def delete_files_in_group_task_upon_delete(sender, instance, **kwargs):

    directory = os.path.join(settings.MEDIA_ROOT, f'documents/group_task_{instance.id}')
    if os.path.exists(directory):
        shutil.rmtree(directory)
    
    


# @receiver(post_save, sender=GroupTask)
# def update_status(sender, instance, **kwargs):
#     if instance.status != instance.original_status:
#         instance.save()