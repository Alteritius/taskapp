from django_q.brokers import get_broker
from django_q.conf import Conf
from django_q.models import Schedule
from django_q.models import Task as TaskDQ
from django_q.tasks import async_task
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Task, GroupTask, GroupMember, CheckScheduleActivation, NotificationDaily


from django.core.mail import EmailMessage


from .notifications import create_notification_task, create_notification_group_task

from datetime import date
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware
from django.utils import timezone
from datetime import datetime
from zoneinfo import ZoneInfo

import time



def check_background_workers_running():
    try:
        broker = get_broker()
        broker.ping()
        return True
    except Exception:
        return False

def simple_async_task():
    print("task is running")
    time.sleep(5)
    print("Task completed")
    print("olaaaaaaa Senioritaaaa")



def get_timezone():

    return ZoneInfo('Europe/Warsaw')


def get_localized_time_now():

    time_now = timezone.now()

    my_timezone = get_timezone()
    localized_time = time_now.astimezone(my_timezone)

    return localized_time

"""
Function that checks which tasks or group_tasks should get which status value,
it's usage is needed before the user get into the page displaying them, so the tasks are properly ordered,

In group_tasks case the function also changes BooleanField overdue, its value is necessary to display additional information in place where the task is displayed about it being late

doesn't return anything, just checks and saves status of the tasks and group_tasks

"""


def check_tasks_status(user):

    today_date = date.today()
    user_tasks = Task.objects.filter(user=user)

    group_member = GroupMember.objects.filter(Q(user=user, status='accepted'))
    leader_group_tasks = GroupTask.objects.filter(Q(creator = user))
    member_group_tasks = GroupTask.objects.filter(Q(member__in = group_member))
    user_group_tasks = leader_group_tasks | member_group_tasks

    for task in user_tasks:
        if task.complete == True:
            task.status = 'completed'
        else:
            if task.start_time.date() < today_date and task.end_time.date() < today_date:
                
                task.status = 'overdue'
            
            elif task.start_time.date() <= today_date and task.end_time.date() >= today_date or task.start_time.date() >= today_date and task.end_time.date() >= today_date:

                task.status = 'pending' 

        task.save()

    for task in user_group_tasks:
        if task.status == "pending" or task.status == "initiated":

            if task.start_time.date() < today_date and task.end_time.date() < today_date:

                task.status = 'overdue'
                task.overdue = True

        elif task.status == "verified":

            task.overdue = False

        else:

            if task.start_time.date() < today_date and task.end_time.date() < today_date:

                task.overdue = True

        task.save()


def regular_tasks_status_check():

    user_list = User.objects.all()

    for user in user_list:
        today_date = date.today()
        user_tasks = Task.objects.filter(user=user)

        time_now = get_localized_time_now()

        group_member = GroupMember.objects.filter(Q(user=user, status='accepted'))
        leader_group_tasks = GroupTask.objects.filter(Q(creator = user))
        member_group_tasks = GroupTask.objects.filter(Q(member__in = group_member))
        user_group_tasks = leader_group_tasks | member_group_tasks

        for task in user_tasks:
            if task.complete == True:
                task.status = 'completed'
            else:
                if task.start_time < time_now and task.end_time < time_now:
                    
                    task.status = 'overdue'
                
                elif task.start_time <= time_now and task.end_time >= time_now or task.start_time >= time_now and task.end_time >= time_now:

                    task.status = 'pending' 

            task.save()

        for task in user_group_tasks:
            if task.status == "pending" or task.status == "initiated":

                if task.start_time < time_now and task.end_time < time_now:

                    task.status = 'overdue'
                    task.overdue = True

            elif task.status == "verified":

                task.overdue = False

            else:

                if task.start_time < time_now and task.end_time < time_now:

                    task.overdue = True

            task.save()

def create_regular_task_check_schedule():
    
    today_time = datetime.now()

    schedule = Schedule.objects.filter(name="Regular Task Check")

    if not schedule.exists():

        Schedule.objects.create(
                name="Regular Task Check",
                func="base.background.regular_tasks_status_check",
                schedule_type=Schedule.HOURLY,
            )






def notification_task(id, group_task_check):
    if group_task_check:
        task = GroupTask.objects.get(id=id)
        if task.deadline_already_notified == False:
            create_notification_group_task(task, 'deadline creator')
            create_notification_group_task(task, 'deadline member')
            task.deadline_already_notified = True
            task.save()
    else:
        task = Task.objects.get(id=id)
        if task.deadline_already_notified == False:
            create_notification_task(task, 'deadline')
            task.deadline_already_notified = True
            task.save()


def create_deadline_notification(instance):
    start = instance.end_time - relativedelta(hours=1)

    group_task_check = instance.is_group_task()

    localized_time_now = get_localized_time_now()

    print("start: " + str(start))
    # print("time_now: " + str(time_now))
    print("datetime: " + str(datetime.now()))
    print("localized: " + str(localized_time_now))

    # print(start < time_now)
    # print(start > time_now)
    # print(start < datetime.now())
    # print(start > datetime.now())

    if start > localized_time_now:
        print("create Schedule")

        if group_task_check:
            schedule_name = f"Notification for group task: {instance.title} {instance.id}"
        else:
            schedule_name = f"Notification for task: {instance.title} {instance.id}"

        schedule_check = Schedule.objects.filter(name=schedule_name)

        if not schedule_check.exists():

            Schedule.objects.create(
                name=schedule_name,
                func="base.background.notification_task",
                schedule_type=Schedule.ONCE,
                next_run=start,
                args=(instance.id, group_task_check),
            )
    else:
        if start < localized_time_now < instance.end_time:
            print("create async_task")
            if instance.deadline_already_notified == False:
                async_task('base.background.notification_task', instance.id, group_task_check)


def daily_task_check():

    today = date.today()
    tasks_for_today = Task.objects.filter(end_time__date=today)

    group_tasks_for_today = GroupTask.objects.filter(end_time__date=today)
    if tasks_for_today:

        for task in tasks_for_today:
            create_deadline_notification(task)

    if group_tasks_for_today:

        for task in group_tasks_for_today:
            create_deadline_notification(task)

    
    schedule = Schedule.objects.filter(name="Daily Task Check")
    if schedule.exists():

        schedule_tasks = Schedule.objects.get(name="Daily Task Check")
        check_schedule = CheckScheduleActivation.objects.filter(schedule=schedule_tasks, date=today)
        if not check_schedule.exists():
            CheckScheduleActivation.objects.create(schedule=schedule_tasks, date=today)
    
    
    print(tasks_for_today)
    print(group_tasks_for_today)




"""
Creation of 2 daily schedules
"""



def create_task_schedule():

    today = date.today()

    schedule = Schedule.objects.filter(name="Daily Task Check")

    if not schedule.exists():
        
        Schedule.objects.create(
            name="Daily Task Check",
            func="base.background.daily_task_check",
            schedule_type=Schedule.DAILY,
            next_run=f'{today} 08:00:00', 
        )

    else:

        schedule_tasks = Schedule.objects.get(name="Daily Task Check")

        check_schedule = CheckScheduleActivation.objects.filter(schedule=schedule_tasks, date=today)

        localized_time_now = get_localized_time_now()

        # schedule_cron = schedule.cron

        schedule_time = datetime(today.year, today.month, today.day, 8, 0)

        my_timezone = get_timezone()

        time_compare = make_aware(schedule_time, my_timezone)


        if not check_schedule.exists() and localized_time_now > time_compare:

            CheckScheduleActivation.objects.create(schedule=schedule_tasks, date=today)

            async_task(schedule_tasks.func)


    


def daily_email():

    today = date.today()

    # zobaczyc czy dziala - wysyla tylko jeden mail

    schedule = Schedule.objects.filter(name="Daily Email")

    print(schedule)

    if schedule.exists():
        schedule_email = Schedule.objects.get(name="Daily Email")

        check_schedule = CheckScheduleActivation.objects.filter(schedule=schedule_email, date=today)

        print(check_schedule)

        if not check_schedule.exists():

            CheckScheduleActivation.objects.create(schedule=schedule_email, date=today)

            print("created checkscheduleactivation")

            for user in User.objects.all():

                user_tasks = Task.objects.filter(user=user).exclude(status="completed")

                group_member = GroupMember.objects.filter(user=user, status='accepted')

                user_group_tasks_creator = GroupTask.objects.filter(creator=user).exclude(status="verified")
                user_group_tasks_member = GroupTask.objects.filter(member__in = group_member).exclude(status="verified")

                user_group_tasks = user_group_tasks_creator | user_group_tasks_member

                count_total = user_tasks.count() + user_group_tasks.count()

                count_today = user_tasks.filter(end_time__date=today).count() + user_group_tasks.filter(end_time__date=today).count()

                title = f'Tasks for day: {today.day}.{today.month}.{today.year}'
                description = f'Daily Reminder for {user.username}, \nNumber of total incompleted tasks: {count_total}, \nNumber of incompleted tasks for the day: {count_today}'
                not_type='daily'

                

                NotificationDaily.objects.create(user=user, related_to=user, title=title, description=description, not_type=not_type)

                if user.email:

                    email = EmailMessage(title, description, to=[user.email])
                    email.send()

                print("created notification and email")




        



def create_email_schedule():

    today = date.today()


    schedule = Schedule.objects.filter(name="Daily Email")

    if not schedule.exists():
        
        Schedule.objects.create(
            name="Daily Email",
            func="base.background.daily_email",
            schedule_type=Schedule.DAILY,
            next_run=f'{today} 08:00:00', 
        )

    else:

        schedule_email = Schedule.objects.get(name="Daily Email")

        check_schedule = CheckScheduleActivation.objects.filter(schedule=schedule_email, date=today)

        localized_time_now = get_localized_time_now()

        schedule_time = datetime(today.year, today.month, today.day, 8, 0)

        my_timezone = get_timezone()

        time_compare = make_aware(schedule_time, my_timezone)


        if not check_schedule.exists() and localized_time_now > time_compare:

            # CheckScheduleActivation.objects.create(schedule=schedule_email, date=today)

            async_task(schedule_email.func)


def delete_schedule_checks():

    today = date.today()

    schedule_tasks_existance = Schedule.objects.filter(name="Daily Task Check")

    schedule_email_existance = Schedule.objects.filter(name="Daily Email")

    if schedule_tasks_existance.exists():

        schedule_tasks = Schedule.objects.get(name="Daily Task Check")

        check_schedule_tasks = CheckScheduleActivation.objects.filter(schedule=schedule_tasks)

        if check_schedule_tasks.exists():

            for check in check_schedule_tasks:

                if check.date < today:

                    check.delete()


    if schedule_email_existance.exists():

        schedule_email = Schedule.objects.get(name="Daily Email")

        check_schedule_email = CheckScheduleActivation.objects.filter(schedule=schedule_email)

        if check_schedule_email.exists():

            for check in check_schedule_email:

                if check.date < today:

                    check.delete()