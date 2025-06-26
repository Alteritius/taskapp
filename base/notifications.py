from .models import NotificationTask, NotificationGroup, NotificationGroupTask, NotificationGroupTaskHistory, NotificationInvite
from django.contrib.auth.models import User



def create_notification_task(object, type_of_not):

    if type_of_not == 'deadline':
        title = f'Task "{object.title}" deadline is  near'
        description = f'Task "{object.title}" deadline is drawing near. Try to complete it as fast as possible.'
        not_type='task'

        link=True

        NotificationTask.objects.create(user=object.user, related_to=object, title=title, description=description, not_type=not_type, link=link)


def create_notification_group(object, type_of_not, second_object=[]):
    if type_of_not == 'delete':
        title = f'Deleted Group: {object.name}'
        description = f'The Group called: "{object.name}" related to you was deleted by its leader: "{object.leader.username}"'
        not_type = 'group'

        for participant in object.participants.all():
            print(participant)
            NotificationGroup.objects.create(user=participant, related_to=object, title=title, description=description, not_type=not_type)
    
    elif type_of_not == 'delete member':
        title = f'You were removed from the Group: {object.name}'
        description = f'The Group leader "{object.leader}" removed you from the list of participants in the Group called: "{object.name}"'
        not_type = 'group'
        print(second_object)
        member = second_object[0]
        participant = member.user


        NotificationGroup.objects.create(user=participant, related_to=object, title=title, description=description, not_type=not_type)

def create_notification_group_task(object, type_of_not, changed=''):
    if type_of_not == 'create':
        title = f'New Group Task: {object.title}'
        description = f'New Group Task called: "{object.title}" related to you was added in a group: "{object.group.name}"'
        member = User.objects.filter(id=object.member.user.id).first()
        not_type = 'group_task'

        link = True

        NotificationGroupTask.objects.create(user=member, related_to=object, title=title, description=description, not_type=not_type, link=link)
    
    elif type_of_not == 'update creator':
        title = f'Update to Group Task: {object.title}'
        description = f'Group Task called: "{object.title}" in a group: "{object.group.name}" related to you was updated by: "{object.creator.username}"'
        member = User.objects.filter(id=object.member.user.id).first()
        not_type = 'group_task'
        # changed_items = changed.split(', ')
        # print(changed_items)

        link = True

        NotificationGroupTask.objects.create(user=member, related_to=object, title=title, description=description, not_type=not_type, changed=changed, link=link)

    elif type_of_not == 'update member':
        title = f'Update to Group Task: {object.title}'
        description = f'Group Task called: "{object.title}" in a group: "{object.group.name}" related to you  was updated by: "{object.member.user.username}"'
        creator = object.creator
        not_type = 'group_task'
        # changed_items = changed.split(', ')
        # print(changed_items)

        link = True

        NotificationGroupTask.objects.create(user=creator, related_to=object, title=title, description=description, not_type=not_type, changed=changed, link=link)

    elif type_of_not == 'delete':
        title = f'Group Task: {object.title}'
        description = f'Group Task called: "{object.title}" in a group: "{object.group.name}" related to you was deleted'
        member = object.member.user
        not_type = 'group_task'

        link = False

        NotificationGroupTask.objects.create(user=member, related_to=object, title=title, description=description, not_type=not_type, link=link)

    elif type_of_not == 'delete file':
        title = f'Group Task: {object.title}, file deleted'
        description = f'Group Task called: "{object.title}" in a group: "{object.group.name}" - one of the files was deleted by the supervisor.'
        member = object.member.user
        not_type = 'group_task'

        link = True

        NotificationGroupTask.objects.create(user=member, related_to=object, title=title, description=description, not_type=not_type, link=link)

    elif type_of_not == 'deadline creator':
        title = f'Group Task "{object.title}" deadline is  near'
        description = f'Group Task "{object.title}" deadline is drawing near. Member working on this project still has not completed given task. Consider delaying deadline of this Group Task.'
        not_type='group_task'

        link=True

        NotificationGroupTask.objects.create(user=object.creator, related_to=object, title=title, description=description, not_type=not_type, link=link)

    elif type_of_not == 'deadline member':
        title = f'Group Task "{object.title}" deadline is  near'
        description = f'Group Task "{object.title}" deadline is drawing near. Try to complete the Group Task as fast as possible.'
        not_type='group_task'

        link=True

        NotificationGroupTask.objects.create(user=object.member.user, related_to=object, title=title, description=description, not_type=not_type, link=link)

def create_notification_group_task_history(object, type_of_not, changed=''):
    if type_of_not == 'create':
        title = f'Group Task: {object.title} was created'
        description = f'Supervisor: {object.creator}, Member working on the Task: {object.member.user}'
        creator = object.creator
        not_type = 'group_task_history'

        NotificationGroupTaskHistory.objects.create(user=creator, related_to=object, title=title, description=description, not_type=not_type)
    
    elif type_of_not == 'update creator':
        title = f'Update made by: {object.creator}'
        description = f'Group Task was updated'
        creator = object.creator
        not_type = 'group_task_history'

        NotificationGroupTaskHistory.objects.create(user=creator, related_to=object, title=title, description=description, not_type=not_type, changed=changed)

    elif type_of_not == 'update member':
        title = f'Update made by: {object.member.user}'
        description = f'Group Task was updated'
        creator = object.creator
        not_type = 'group_task_history'

        NotificationGroupTaskHistory.objects.create(user=creator, related_to=object, title=title, description=description, not_type=not_type, changed=changed)

    elif type_of_not == 'delete file':
        title = f'Group Task: {object.title}, file deleted'
        description = f'Group Task called: "{object.title}" in a group: "{object.group.name}" - one of the files was deleted by the supervisor.'
        creator = object.creator
        not_type = 'group_task_history'

        NotificationGroupTaskHistory.objects.create(user=creator, related_to=object, title=title, description=description, not_type=not_type, changed=changed)
        
#def create_notification_invite(object, type_of_not):
#     return 0 