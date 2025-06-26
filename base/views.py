from typing import Any
from django.forms.models import BaseModelForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic import TemplateView
from django.views import View
import calendar
from django.urls import reverse_lazy, reverse
from django.utils.safestring import mark_safe

from django.contrib.auth.models import User

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login 

from django.contrib.auth.decorators import login_required

from django.db.models import Q

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


from django.conf import settings
import os



from .models import Task, CustomGroup, GroupInvite, GroupMember, GroupTask
from .models import NotificationTask, NotificationInvite, NotificationGroupTask, NotificationGroup, NotificationGroupTaskHistory, NotificationDaily
from .models import group_files_directory_path
# from .models import GroupSubtask

from .forms import TaskForm,UserUpdateForm, ProfileUpdateForm, GroupForm, GroupTaskForm

from .html_cal import MyCalendar

from datetime import timedelta, datetime, date

from dateutil.relativedelta import relativedelta

from .notifications import create_notification_task, create_notification_group_task, create_notification_group, create_notification_group_task_history

from .background import check_background_workers_running, simple_async_task, daily_task_check, daily_email, check_tasks_status

from django_q.tasks import async_task
from django_q.models import Schedule





"""
View related to handling logging in, standard view using LoginView,
if the user is authenticated then the app redirects user to the DashboardPage
"""

class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__' #it makes the form on login.html get all fields the user have - username and password
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard')
    



"""
View related to handling registering, based on FormView, 
when authenticated it also redirects to the DashboardPage,
it uses basic Django model - User

Could be changed, maybe adding mail?
"""

class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm #this has to be changed later, I want the registering person to provide mail

    redirect_authenticated_user = True #This doesn't work because FormView doesn't have 'redirect_authenticated_user' attribute
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs): #function to manually override function get to redirect logged in user from RegisterPage  
        if self.request.user.is_authenticated:
            return redirect('dashboard')
        return super(RegisterPage, self).get(*args, **kwargs)
    



"""
View related to the user's profile, 
needs user's id and lists groups in which the user participates
"""


@login_required(login_url='login')
def ProfilePage(request, pk):
    user = User.objects.get(id=pk)

    user_groups = CustomGroup.objects.filter(Q(leader=user) | Q(participants=user)).distinct()

    context = {'user': user,
               'user_groups': user_groups}

    return render(request, 'base/profile.html', context)

"""
View related to updating the user's profile, 
needs two forms form the forms.py file related to updating User model (basic model in Django to create user model) 
and one related to the profile of a User (it contains things that I wanted to add to the User model - it needs a signal in signals.py file to work properly when creating or updating the User model)

"""

@login_required(login_url='login')
def UpdateProfilePage(request):
    user = request.user
    user_form = UserUpdateForm(instance=user)
    profile_form = ProfileUpdateForm(instance=user.profile)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile', pk=user.id)
        
    context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'base/update-profile.html', context)



    

"""
--------------- Calendar
"""



"""
Function used to change its format to a date() format,
datetime.today() in case sth unexpected happens

"""

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split("-"))
        return date(year, month, day=1)
    return datetime.today()


"""
Functions used to change the shown month desired by the user,
it uses function relativedelta() to change the month to the next or previous one,
then it makes a string that is injected into web adress as a parameter, so that the view can later get it form the web adress and display proper month calendar with a changed month,

"""

def prev_month(d):
    prev_month = d + relativedelta(months=-1)
    month = "month=" + str(prev_month.year) + "-" + str(prev_month.month)
    return month


def next_month(d):
    next_month = d + relativedelta(months=+1)
    month = "month=" + str(next_month.year) + "-" + str(next_month.month)
    return month


"""
Function creating calendar - model MyCalendar in html_cal.py,
then it gets one month in html format using .formatmonth() method, then it uses mark_safe() function so the calendar will be properly displayed on the web page.
returns month of a calendar

"""

def create_calendar(year, month, user):
    calendar = MyCalendar(year, month, user)
    html_calendar = calendar.formatmonth()
    html_calendar = mark_safe(html_calendar)
    return html_calendar


"""
View that creates monthly calendar for the user usin create_calendar function,
it also makes a necessary check for user's tasks using check_tasks_status() function, which declaration is in Tasks section
prev_month and next_month are used for buttons on the web page so the user can jump between different months, 

"""

@login_required(login_url='login')
def CalendarPageMonth(request):

    user = request.user
    # check_tasks_status(request.user)

    day = get_date(request.GET.get("month", None))
    html_calendar = create_calendar(day.year, day.month, user)
    local_prev_month = prev_month(day)
    local_next_month = next_month(day)


    context = {
        "calendar_month": html_calendar,
        "prev_month": local_prev_month,
        "next_month": local_next_month,
    }


    return render(request, 'base/calendar.html', context)


"""
List of analogical functions for CalendarPageYear(), like for CalendarPageMonth()

"""

def get_year(req_year):
    if req_year:
        return int(req_year)
    return datetime.today().year


def prev_year(y):
    y -= 1
    year = "year=" + str(y)
    return year


def next_year(y):
    y += 1
    year = "year=" + str(y)
    return year

"""
View displaying the whole year, it uses create_calendar() function in a loop to create the 12 months

not very optimal

"""


@login_required(login_url='login')
def CalendarPageYear(request):

    user = request.user
    # check_tasks_status(request.user)
    current_year = get_year(request.GET.get("year", None))

    # print(request.GET.get("year", None))
    calendar_year=[]
    for i in range(1, 13):
        calendar_year.append(create_calendar(current_year, i, user))

    local_prev_year = prev_year(current_year)
    local_next_year = next_year(current_year)
    
    context = {
        "calendar_year": calendar_year,
        "prev_year": local_prev_year,
        "next_year": local_next_year,
    }

    return render(request, 'base/calendar_year.html', context)



"""
Two functions to navigate between weeks on a web page related to the view CalendarPageWeek()

"""


def prev_week(week_dates):

    prev_week = week_dates[0] - timedelta(days=7)
    week = "week=" + str(prev_week.year) + "-" + str(prev_week.month) + "-" + str(prev_week.day)
    return week


def next_week(week_dates):

    next_week = week_dates[0] + timedelta(days=7)
    week = "week=" + str(next_week.year) + "-" + str(next_week.month) + "-" + str(next_week.day)
    return week

"""
Function essential to set proper week_dates while using weekly calendar,
it formats given date to a needed format and then it checks which day of the week is the current day to discern properly, which dates are relevant to the current week and to be able to add and substruct weeks from this point. 

"""

def get_week_dates(day):

    if day:
         y, m, d = (int(x) for x in day.split("-"))
         current_date = date(y, m, d)
    else:
        current_date = date.today()

    current_weekday = current_date.weekday()
    start_of_week = current_date - timedelta(days=current_weekday)
    week_dates = []

    for i in range(7):
        week_dates.append(start_of_week + timedelta(days=i))

    return week_dates

"""
View related to the weekly calendar feature,
it checks status of user's tasks, uses function get_week_dates() to discern which week it's supposed to display,
it uses funtion find_task_day to find all user's tasks that should be displayed each week



"""


@login_required(login_url='login')
def CalendarPageWeek(request):

    user = request.user
    today = date.today()
    # check_tasks_status(request.user)
    week_dates = get_week_dates(request.GET.get("week", None))

    local_prev_week = prev_week(week_dates)
    local_next_week = next_week(week_dates)

    personal_tasks_for_day = {}
    for i in range(len(week_dates)):
        tasks = []
        tasks = find_task_day(user, week_dates[i].year, week_dates[i].month, week_dates[i].day)
        personal_tasks_for_day[week_dates[i]] = tasks

    group_tasks_for_day = {}

    for i in range(len(week_dates)):
        tasks = []
        tasks = find_group_task_day(user, week_dates[i].year, week_dates[i].month, week_dates[i].day)
        group_tasks_for_day[week_dates[i]] = tasks

    tasks_for_day = {}
    for key in group_tasks_for_day.keys():
        tasks_for_day[key] = (personal_tasks_for_day[key], group_tasks_for_day[key])


    context = {
        "week_dates": week_dates,
        "prev_week": local_prev_week,
        "next_week": local_next_week,
        "today": today,
        "tasks_for_day": tasks_for_day,
        "group_tasks_for_day": group_tasks_for_day,
    }

    return render(request, 'base/calendar_week.html', context)

"""
--------------- Notifications
"""



def get_unified_notifications_list(user):

    notifications_task = NotificationTask.objects.filter(user=user)
    notifications_group_task = NotificationGroupTask.objects.filter(user=user)
    notifications_group = NotificationGroup.objects.filter(user=user)
    notifications_invite = NotificationInvite.objects.filter(user=user)
    notifications_daily = NotificationDaily.objects.filter(user=user)
    notifications_list = notifications_task.union(notifications_group_task, notifications_group, notifications_invite, notifications_daily)

    return notifications_list


def get_specified_notification(user, Ntype, pk):

    if Ntype == 'task':
        notification = NotificationTask.objects.get(user=user, id=pk)
    elif Ntype == 'group_task':
        notification = NotificationGroupTask.objects.get(user=user, id=pk)
    elif Ntype == 'group_task_history':
        notification = NotificationGroupTaskHistory.objects.get(id=pk)
    elif Ntype == 'group':
        notification = NotificationGroup.objects.get(user=user, id=pk)
    elif Ntype == 'invite':
        notification = NotificationInvite.objects.get(user=user, id=pk)
    elif Ntype == 'daily':
        notification = NotificationDaily.objects.get(user=user, id=pk)
    

    return notification

def check_existance_of_related_object(user, Ntype, object):
    
    if Ntype == 'task':
        return Task.objects.filter(id=object.id).exists()
    elif Ntype == 'group_task':
        return GroupTask.objects.filter(id=object.id).exists()
    elif Ntype == 'group':
        return CustomGroup.objects.filter(id=object.id).exists()
    elif Ntype == 'invite':
        if GroupInvite.objects.filter(id=object.id).exists():
            invite = GroupInvite.objects.get(id=object.id)
            if invite.hidden == False:
                return True
            elif invite.hidden == True and user == invite.inviting_user:
                return True
            else:
                return False


@login_required(login_url='login')
def NotificationListPage(request):

    notifications_list = get_unified_notifications_list(request.user).order_by('-created')


    context = {
        'notifications_list': notifications_list,
    }

    return render(request, 'base/notifications_list.html', context)



@login_required(login_url='login')
def NotificationDetailPage(request, Ntype, pk):

    notification = get_specified_notification(request.user, Ntype, pk)
    related_object = notification.related_to
    link_view = ''
    link_arguments = []

    if not Ntype == 'daily':
        if(related_object):
            check_related_object = check_existance_of_related_object(request.user, Ntype, related_object)

            if(check_related_object):
                if notification.link == True:
                    if Ntype == 'task':
                        link_view = 'task-update'
                        link_arguments.append(related_object.id)
                    elif Ntype == 'group_task':
                        link_view = 'group-task-detail'
                        link_arguments.append(related_object.group.id)
                        link_arguments.append(related_object.id)
                    elif Ntype == 'group':
                        link_view = 'group-detail'
                        link_arguments.append(related_object.id)
                    elif Ntype == 'invite':
                        link_view = 'invite-detail'
                        link_arguments.append(related_object.id)
            else:
                notification.link = False
                notification.save()
                # print(notification.link)
        else:
            notification.link = False
    
    notification.seen = True
    notification.save()

    context = {
        'notification': notification,
        'link_view': link_view,
        'link_arguments': link_arguments,
        # 'link_to_object': link_to_object,
    }

    return render(request, 'base/notification_detail.html', context)



@login_required(login_url='login')
def NotificationDeletePage(request, Ntype, pk):
    
    notification = get_specified_notification(request.user, Ntype, pk)

    # print(Ntype)

    if Ntype != 'group_task_history':
        url = 'notifications-list'
    else:
        # print(notification.related_to)
        if notification.related_to:
            url = f'/group/{notification.related_to.group.id}/group-task/{notification.related_to.id}/history/'
        else:
            url = 'notifications-list'
    
    obj_name = 'notification'
    obj = notification.title

    if request.method == 'POST':

        notification.delete()
        next_page_url=request.POST.get('next_page', reverse('dashboard'))
        return redirect(next_page_url)

    context = {'obj': obj,
               'obj_name': obj_name,
               'url': url
    }

    return render(request, 'base/confirm-delete.html', context)


@login_required(login_url='login')
def NotificationDeleteManyPage(request):

    if request.method == 'POST':
        chosen_items = request.POST.getlist('chosen-items')
        for item in chosen_items:
            item_arguments = []
            item_arguments = item.split(", ")
            if item_arguments[0] == 'task':
                NotificationTask.objects.get(id=item_arguments[1]).delete()
            elif item_arguments[0] == 'group_task':
                NotificationGroupTask.objects.get(id=item_arguments[1]).delete()
            elif item_arguments[0] == 'group_task_history':
                NotificationGroupTaskHistory.objects.get(id=item_arguments[1]).delete()
            elif item_arguments[0] == 'group':
                NotificationGroup.objects.get(id=item_arguments[1]).delete()
            elif item_arguments[0] == 'invite':
                NotificationInvite.objects.get(id=item_arguments[1]).delete()
            elif item_arguments[0] == 'daily':
                NotificationDaily.objects.get(id=item_arguments[1]).delete()

        next_page = request.META.get('HTTP_REFERER', '/')
        if next_page:
            return redirect(next_page)
        else:
            return redirect('notifications-list')

    return redirect('notifications-list')







"""
--------------- Tasks
"""




"""
Function to find user's tasks that fits certain day,


returns QuerySet of tasks that fits the critiria

"""

def find_task_day(user, year, month, day):
    tasks = Task.objects.filter(user = user, start_time__year__lte = year, end_time__year__gte = year,
                                start_time__month__lte = month, end_time__month__gte = month,
                                start_time__day__lte = day, end_time__day__gte = day)
    # print(tasks)
    return tasks

"""
Function to find user's group tasks that fits certain day,


returns QuerySet of tasks that fits the critiria

"""

def find_group_task_day(user, year, month, day):

    group_member = GroupMember.objects.filter(Q(user=user, status='accepted'))

    leader_group_tasks = GroupTask.objects.filter(Q(creator = user, start_time__year__lte = year, end_time__year__gte = year, start_time__month__lte = month, end_time__month__gte = month, start_time__day__lte = day, end_time__day__gte = day))
    member_group_tasks = GroupTask.objects.filter(Q(member__in = group_member, start_time__year__lte = year, end_time__year__gte = year, start_time__month__lte = month, end_time__month__gte = month, start_time__day__lte = day, end_time__day__gte = day))

    group_tasks = leader_group_tasks | member_group_tasks

    return group_tasks


"""
View handling display of daily tasks for a certain day,
the day is specified in parameters in the function declaration,
First check_tasks_status() to check tasks' statuses and then find_task_day() to find all tasks for a specific day,
counts incomplete tasks to display it on the page,
it doesn't use any additional external functions to handle user's desire to change displayed day,
instead buttons on the page using prev_day and next_day are redirecting user to the DailyTaskList with all parameters of the mentioned variables 



"""

@login_required(login_url='login')
def DailyTaskList(request, year, month, day):

    # check_tasks_status(request.user)
    tasks = find_task_day(request.user, year, month, day)
    group_tasks = find_group_task_day(request.user, year, month, day)
    count = tasks.filter(complete=False).count()
    clicked_date = f'{year:04d}-{month:02d}-{day:02d}'

    date_day = date(year, month, day)

    # today_time = datetime.now()
    # print("to jest datetime" + str(today_time))
    # for task in tasks:
    #     print(task.end_time)

    prev_day = date_day + relativedelta(days=-1)
    next_day = date_day + relativedelta(days=+1)
    
    context = {'tasks': tasks, 
                'year': year, 
                'month': month, 
                'day': day, 
                'next_day': next_day,
                'prev_day': prev_day,
                'count': count,
                'group_tasks': group_tasks,
                'clicked_date': clicked_date}
    
    return render(request, 'base/task_list_day.html', context)


"""
View that is simply redirecting to DailyTaskList() with current date


"""



@login_required(login_url='login')
def TodayTaskList(request):
    
    today = date.today()

    return DailyTaskList(request, today.year, today.month, today.day)




"""
View that handles main page of the app - Dashboard(),
it collects actual lists of certain kinds of tasks and then display them on the web page,
it also checks whether the user typed anything in the search bar on the page and updates lists of tasks accordingly


as it turns out the search_query (value from the search bar on the page ) is not needed .-. JS suffices


"""




@login_required(login_url='login')
def DashboardPage(request):
    # check_tasks_status(request.user)

    list_of_tasks = Task.objects.filter(user=request.user) 
    completed_tasks = list_of_tasks.filter(complete='True')
    overdue_tasks = list_of_tasks.filter(status='overdue')
    pending_tasks = list_of_tasks.filter(status='pending')

    group_member = GroupMember.objects.filter(Q(user = request.user, status='accepted'))
    leader_group_tasks = GroupTask.objects.filter(Q(creator = request.user))
    member_group_tasks = GroupTask.objects.filter(Q(member__in = group_member))
    group_tasks = leader_group_tasks | member_group_tasks
  
    all_tasks_number = list_of_tasks.count()
    completed_tasks_number = completed_tasks.count()
    overdue_tasks_number = overdue_tasks.count()
    pending_tasks_number = pending_tasks.count()
    group_tasks_number = group_tasks.count()
    all_tasks_number += group_tasks_number
    context={'completed_tasks': completed_tasks,
             'completed_tasks_number': completed_tasks_number,
               'overdue_tasks': overdue_tasks,
             'overdue_tasks_number': overdue_tasks_number,
              'pending_tasks': pending_tasks,
             'pending_tasks_number': pending_tasks_number,
              'all_tasks': list_of_tasks,
               'all_tasks_number': all_tasks_number,
               'group_tasks': group_tasks,
               'group_tasks_number': group_tasks_number,

                # 'search_query': search_query 
                }

    return render(request, 'base/dashboard.html', context)


"""
View handling Task() model instance creation, 
code is a bit convoluted, it's mainly about handling DateTimeField() in the Task() model,
it handles given information about a day that the user wants to add the task for, when it's not given it set the date for current date 

it also handles returning to the previous page
"""


@login_required(login_url='login')
def TaskCreatePage(request, weekday):
    proper_date = None
    try:           
        proper_date = datetime.strptime(weekday, '%Y-%m-%d').date()
    except:
        try: 
            weekday_int = int(weekday)
            if weekday_int == 1:
                proper_date = datetime.now()
        except ValueError:
            print(f'Weekday is not a number: {weekday}')

    help = f'{proper_date.year:04d}-{proper_date.month:02d}-{proper_date.day:02d}T00:00'
    proper_datetime = datetime.strptime(help, '%Y-%m-%dT%H:%M')
    
    if request.method == 'POST':
        form = TaskForm(request.POST)

        if form.is_valid():

            task = form.save(commit=False)
            task.user = request.user
            task.start_time = form.cleaned_data['start_time']
            task.end_time = form.cleaned_data['end_time']
            task.save()
            form.save_m2m()
            next_page_url=request.POST.get('next_page', reverse('dashboard'))
            return redirect(next_page_url)
        
    else: 
        form = TaskForm(initial={'start_time': proper_datetime, 'end_time': proper_datetime})

    context = {'form': form}
    return render(request, 'base/task_form.html', context)


"""
View handling updating Task() instance
"""


@login_required(login_url='login')
def TaskUpdatePage(request, tpk):

    task = Task.objects.get(id=tpk)
    task_end_time = task.end_time
    task_title = task.title
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():

            task = form.save(commit=False)
            task.user = request.user
            task.start_time = form.cleaned_data['start_time']
            task.end_time = form.cleaned_data['end_time']

            if form.cleaned_data['end_time'] != task_end_time:

                task.deadline_already_notified = False
                schedule_name = f"Notification for task: {task_title} {task.id}"
                schedule_query = Schedule.objects.filter(name=schedule_name)
                if schedule_query.exists():
                    schedule = Schedule.objects.get(name=schedule_name)
                    schedule.delete()

            task.save()
            next_page_url=request.POST.get('next_page', reverse('dashboard'))
            return redirect(next_page_url)

    else: 
        form = TaskForm(instance=task)
  
    context = {'form': form}
    return render(request, 'base/task_form.html', context)



"""
View handling deletion of the Task()
"""

@login_required(login_url='login')
def TaskDeletePage(request, tpk):

    task = Task.objects.get(id=tpk)
    url = 'dashboard'
    obj_name = 'task'
    
    if request.method == 'POST':
        
        task.delete()

        next_page_url=request.POST.get('next_page', reverse('dashboard'))
        return redirect(next_page_url)

    
    context = {'obj': task,
               'obj_name': obj_name,
               'url': url}


    return render(request, 'base/confirm-delete.html', context)





"""
--------------- Groups
"""


"""
View handling display of user's groups in which the user participates - whether as a member or as the leader,

The additional filter() usage is needed because of how the models are related to each other - GroupMember model is a middleman between the User and CustomGroup models  


"""

@login_required(login_url='login')
def GroupListPage(request):

    user = request.user

    leader_groups = CustomGroup.objects.filter(Q(leader=user))
    
    accepted_groups = GroupMember.objects.filter(Q(user=request.user, status='accepted'))

    participant_groups = CustomGroup.objects.filter(id__in=accepted_groups.values('group_id'))

    user_groups = (leader_groups | participant_groups).distinct()



    context = { 'user_groups': user_groups}

    return render(request, 'base/groups.html', context)



"""
View that handles creating instance of CustomGroup model,
the only additional issue is handling creating GroupInvite instances for anyone chosen by the user creating the group and excluding the creator from the list of potential group members


"""

@login_required(login_url='login')
def GroupCreatePage(request):

    title = "Create Group" 
    if request.method == 'POST':
        form = GroupForm(request.POST)

        if form.is_valid():

            group = form.save(commit=False)
            group.leader = request.user
            group.save()
            form.save_m2m()
            participants = form.cleaned_data['participants']
            for user in participants:
                GroupInvite.objects.create(group=group, inviting_user=request.user, invited_user=user)
            return redirect('group-list')
           
    else:
        form = GroupForm()
       

        form.fields['participants'].queryset = form.fields['participants'].queryset.exclude(id=request.user.id)
    
    
    context = {'form': form,
               'title': title}
    return render(request, 'base/group-form.html', context)


"""
View that handles updating instances of CustomGroup model,
the tricky part in this view is handling properly the list of potential group members - to exclude the group leader and its members, save the new group members properly to the database and send them invites

it also uses the same template as GroupCreatePage()
"""


@login_required(login_url='login')
def GroupUpdatePage(request, gpk):

    group = CustomGroup.objects.get(id=gpk)
    title = "Update Group"
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():    
            new_group=form.save(commit=False)
            new_participants = form.cleaned_data['participants']
            all_participants = set(new_participants) | set(group.participants.all())
            new_group.save()
            group.participants.set(all_participants)
            new_participants_id = set(new_participants.values_list('id', flat=True))

            for user_id in new_participants_id:
                user = User.objects.get(id=user_id)
                GroupInvite.objects.create(group=new_group, inviting_user=request.user, invited_user=user)

            return redirect('group-detail', pk=group.id)
           
    else: 
        form = GroupForm(instance=group)
        current_members = GroupMember.objects.filter(group=group)
        current_participants = User.objects.filter(id__in=current_members.values('user_id'))
        group_leader = User.objects.filter(id=group.leader.id)
        excluded_users = current_participants | group_leader
        
        form.fields['participants'].queryset = form.fields['participants'].queryset.exclude(id__in=excluded_users.values_list('id', flat=True))
   
    context = {'form': form,
               'group': group,
               'title': title}
    return render(request, 'base/group-form.html', context)


"""
View that handles display of the group, its leader, members, potential members and group tasks


"""

@login_required(login_url='login')
def GroupDetailPage(request, gpk):

    group = CustomGroup.objects.get(id=gpk)
    
    members = GroupMember.objects.filter(Q(group=group, status='accepted'))

    participants = User.objects.filter(id__in=members.values('user_id'))

    pending_members = GroupMember.objects.filter(Q(group=group, status='pending'))

    pending_participants = User.objects.filter(id__in=pending_members.values('user_id'))

    group_tasks = GroupTask.objects.filter(group=group)

    context = {'group': group, 
               'participants': participants, 
               'pending_participants': pending_participants,
               'group_tasks': group_tasks}

    return render(request, 'base/group-detail.html', context)


"""
View that handles deletion of a group


"""

@login_required(login_url='login')
def DeleteGroup(request, gpk):

    group = CustomGroup.objects.get(id=gpk)

    url = 'group-list'
    obj_name ='group'

    if request.user != group.leader:
        return redirect('group-list')
    
    else:

        if request.method == 'POST':

            create_notification_group(group,'delete')

            group.delete()

            return redirect('group-list')
                

        context = {'obj': group.name,
                   'obj_name': obj_name,
                   'url': url}

        return render(request, 'base/confirm-delete.html', context)
    







"""
View that handles showing two lists of invites for each users, one that were sent by the user to other users, 
and another one that handles received invites (doesn't work at the moment, because those invites are not implemented yet)

"""



@login_required(login_url='login')
def GroupInviteList(request):

    user = request.user

    sent_invites = GroupInvite.objects.filter(Q(inviting_user=user))

    obtained_invites = GroupInvite.objects.filter(Q(invited_user=user, hidden = False))

    context = {'sent_invites': sent_invites,
                'obtained_invites': obtained_invites}
    
    return render(request, 'base/invite_list.html', context)


"""
View that displays details of the GroupInvite instance

"""



@login_required(login_url='login')
def GroupInviteDetail(request, pk):

    invite = GroupInvite.objects.get(id=pk)

    context = {'invite': invite}

    return render(request, 'base/invite_detail.html', context)


"""
View that handles acceptance of the invite,
it handles necessary variables related to UI of invite list and changes GroupMember status on "accepted"

"""



@login_required(login_url='login')
def AcceptGroupInvite(request, pk):

    invitation = GroupInvite.objects.get(id=pk)

    member = GroupMember.objects.get(group=invitation.group, user=request.user)

    if invitation.invited_user != request.user:
        return redirect('groups')
       
    invitation.accepted = True
    invitation.rejected = False
    invitation.hidden = True

    member.status = 'accepted'

    member.save()
    invitation.save()
    return redirect('invite-list')


"""
View that handles rejection of the invite,
analogic to the previous one

"""


@login_required(login_url='login')
def RejectGroupInvite(request, pk):

    invitation = GroupInvite.objects.get(id=pk)

    member = GroupMember.objects.get(group=invitation.group, user=request.user)


    user = request.user

    if invitation.invited_user != user:
        return redirect('groups')

    invitation.accepted = False
    invitation.rejected = True
    invitation.hidden = True

    member.delete()
    
    invitation.save()
    return redirect('invite-list')


"""
View that handles deletion of the invite

"""

@login_required(login_url='login')
def DeleteGroupInvite(request, pk):

    invitation = GroupInvite.objects.get(id=pk)

    user = request.user

    if invitation.inviting_user != user:
        return redirect('groups')

    invitation.delete()
    return redirect('invite-list')


"""
View that handles deletion of the particular GroupMember

"""


@login_required(login_url='login')
def DeleteGroupMember(request, gpk, pk):

    user = User.objects.get(id=pk)

    group = CustomGroup.objects.get(id=gpk)

    member = GroupMember.objects.get(group=group, user=user)

    if request.method == 'POST':

        object_to_send = [member]

        # print(object_to_send)

        create_notification_group(group, 'delete member', object_to_send)

        member.delete()

        if request.user == group.leader:
            return redirect('group-detail', pk=group.id)
        else:
            return redirect('groups')
    
    context = {'group': group,
               'user': user}
    return render(request, 'base/group-member-delete.html', context)







"""
View about creating group tasks, it behaves similarly to a Task(), but it also need information from group leader about who is going to be working on this task.
Also there's a feature to upload tasks in this case in a moment the GroupTask() is created. 


REDO THIS PART if possible, mostly the part about uploading files

"""



@login_required(login_url='login')
def GroupTaskCreatePage(request, gpk):

    group = CustomGroup.objects.get(id=gpk)
    title = "Create Group Task"
    create = 1
    if request.user != group.leader:
        return redirect('groups')   
    else:

        today = date.today()
        help = f'{today.year:04d}-{today.month:02d}-{today.day:02d}T00:00'
        proper_datetime = datetime.strptime(help, '%Y-%m-%dT%H:%M')

        if request.method == 'POST':

            form = GroupTaskForm(request.POST, request.FILES)

            if form.is_valid():
                group_task = form.save(commit=False)
                group_task.group = group
                group_task.creator = request.user
                group_task.member = form.cleaned_data['member']
                group_task.status = form.cleaned_data['status']
                group_task.start_time = form.cleaned_data['start_time']
                group_task.end_time = form.cleaned_data['end_time']
                group_task.group_files = form.cleaned_data['group_files']
                group_task.save()
                form.save_m2m()


                if group_task.group_files:
                    old_path = group_task.group_files.path

                    file_name = group_task.group_files.name
                    file_name = file_name.lstrip('temporary/')
                    new_path = group_files_directory_path(group_task, file_name)

                    if old_path != new_path:

                        with default_storage.open(old_path, 'rb') as old_file:
                            default_storage.save(new_path, ContentFile(old_file.read()))
                        default_storage.delete(old_path)
                        group_task.group_files.name = new_path
                        group_task.save()

                    
                create_notification_group_task(group_task,'create')
                create_notification_group_task_history(group_task,'create')

                return redirect('group-detail', pk=group.id)

        else:

            form = GroupTaskForm(initial={'start_time': proper_datetime, 'end_time': proper_datetime})
            current_members = GroupMember.objects.filter(group=group, status='accepted')
            form.fields['member'].queryset = current_members

        context = {'form': form,
                    'group': group,
                    'title': title,
                    'create': create}
        return render(request, 'base/group-task-form.html', context)
    


"""
View that handles updates of GroupTask model,
now it handles files properly,
variable 'create' is related to the fact that I use one template for handling creation and updating the GroupTask model,
experiment of boredom, it's not the end of the world but in this case it's not optimal, mainly handling file upload


"""


@login_required(login_url='login')
def GroupTaskUpdatePage(request, gpk, gtpk):
    group = CustomGroup.objects.get(id=gpk)
    group_task = GroupTask.objects.get(group=group, id=gtpk)
    title = "Update Group Task"
    create = 0
    old_group_files = set(get_group_task_files(group_task))
    group_task_info = {
        'title': group_task.title,
        'description': group_task.description,
        'status': group_task.status,
        'start_time': group_task.start_time,
        'end_time': group_task.end_time,
        'group_files': old_group_files,

    }
    if request.user == group_task.creator or request.user == group_task.member.user:

        if request.method == 'POST':

            form = GroupTaskForm(request.POST, request.FILES, instance=group_task)

            # print(form.errors)

            if form.is_valid():

                new_group_task=form.save(commit=False)
                
                new_group_task.title = form.cleaned_data['title']
                new_group_task.description = form.cleaned_data['description']
                new_group_task.member = group_task.member
                new_group_task.status = form.cleaned_data['status']
                new_group_task.start_time = form.cleaned_data['start_time']
                new_group_task.end_time = form.cleaned_data['end_time']
                group_task.group_files = form.cleaned_data['group_files']

                changed = ''

                if form.cleaned_data['title'] != group_task_info['title']:
                    changed += ', title'
                if form.cleaned_data['description'] != group_task_info['description']:
                    changed += ', description'
                if form.cleaned_data['status'] != group_task_info['status']:
                    changed += ', status'
                if form.cleaned_data['start_time'] != group_task_info['start_time']:
                    changed += ', start-time'
                if form.cleaned_data['end_time'] != group_task_info['end_time']:
                    changed += ', end-time'
                    new_group_task.deadline_already_notified = False
                    schedule_name = f"Notification for group task: {group_task_info['title']} {new_group_task.id}"
                    schedule_query = Schedule.objects.filter(name=schedule_name)
                    if schedule_query.exists():
                        schedule = Schedule.objects.get(name=schedule_name)
                        schedule.delete()

                new_group_task.save()
                new_group_files = set(get_group_task_files(new_group_task))

                if old_group_files != new_group_files:
                    changed += ', files'

                person = request.user

                if person == group_task.creator:
                    create_notification_group_task(new_group_task, 'update creator', changed)
                    create_notification_group_task_history(new_group_task, 'update creator', changed)
                elif person == group_task.member.user:
                    create_notification_group_task(new_group_task, 'update member', changed)
                    create_notification_group_task_history(new_group_task, 'update member', changed)

                return redirect('group-task-detail', gpk=group.id, pk=group_task.id)

        else:

            form = GroupTaskForm(instance=group_task)
            form.fields['member'].initial = group_task.member

            if request.user == group_task.member:
                form.fields['status'].choices = [
                    ('pending', 'Pending'),
                    ('initiated', 'Initiated'),
                    ('finished', 'Finished'),
                ]

        context = {'form': form,
                'group': group,
                'group_task': group_task,
                'title': title,
                'create': create}
        return render(request, 'base/group-task-form.html', context)

        
    
    else:

        return redirect('group-list')

        
"""
Function that handles prorperly finding files of a group task,
returns path to the folder with group task's files


"""



def get_group_task_files(group_task):

    path = os.path.join(settings.MEDIA_ROOT, f'documents/group_task_{group_task.id}')

    if os.path.exists(path):
        return os.listdir(path)
    
    return []


"""
View that handles displaying information about the GroupTask instance 


"""


@login_required(login_url='login')
def GroupTaskDetailPage(request, gpk, gtpk):

    group = CustomGroup.objects.get(id=gpk)

    group_task = GroupTask.objects.get(group=group, id=gtpk)

    group_files = get_group_task_files(group_task)

    path_to_file = settings.MEDIA_URL


    context = {'group_task': group_task,
               'group_files': group_files,
               'path_to_file': path_to_file}

    return render(request, 'base/group-task-detail.html', context)



"""
View that handles deletion of the GroupTask, 
one of the signals in singlas.py handles deletion fo files related to the particular GroupTask


"""

@login_required(login_url='login')
def GroupTaskDeletePage(request, gpk, gtpk):

    group = CustomGroup.objects.get(id=gpk)

    group_task = GroupTask.objects.get(group=group, id=gtpk)

    obj_name = 'task'
    url = "'group-detail' pk=group_task.group.id "
    

    if request.user != group_task.creator:
        return redirect('group-list')
    
    else:

        if request.method == 'POST':

            create_notification_group_task(group_task, 'delete')

            group_task.delete()
            next_page_url=request.POST.get('next_page', reverse('dashboard'))
            return redirect(next_page_url)


        context = {'obj': group_task,
                   'url': url,
                   'obj_name': obj_name}



        return render(request, 'base/confirm-delete.html', context)


"""
View that handles deletion of files from GroupTask()

At the moment only Group leader/ GroupTask creator have access to this feature
"""

@login_required(login_url='login')
def GroupTaskDeleteFile(request, gpk, gtpk, file_name):

    group = CustomGroup.objects.get(id=gpk)
    group_task = GroupTask.objects.get(group=group, id=gtpk)
    obj_name = 'file'
    url = "'group-task-detail' gpk=group_task.group.id pk=group_task.id"
    if request.user != group_task.creator:
        return redirect('group-list')
    else:
        if request.method == 'POST':

            general_path = settings.MEDIA_ROOT
            path_to_file = group_files_directory_path(group_task, file_name)
            true_path_to_file = os.path.join(general_path, path_to_file)

            if os.path.exists(true_path_to_file):
                print("path exists")
            else:
                print("nope")
            try: 
                os.remove(true_path_to_file)
                create_notification_group_task(group_task, 'delete file')
                create_notification_group_task_history(group_task, 'delete file')
                return redirect('group-task-detail', gpk=gpk, pk=gtpk)
            except FileNotFoundError:
                print("the file doesn't exist")
                return redirect('group-task-detail', gpk=gpk, pk=gtpk)
        context = {
                'obj': file_name,
                'url': url,
                'obj_name': obj_name,
                'group_task': group_task,
        }
        return render(request, 'base/confirm-delete.html', context)




@login_required(login_url='login')
def GroupTaskHistoryPage(request, gpk, gtpk):

    group = CustomGroup.objects.get(id=gpk)

    group_task = GroupTask.objects.get(group=group, id=gtpk)

    notifications_list = NotificationGroupTaskHistory.objects.filter(related_to=group_task).order_by('-created')


    context = {
        'notifications_list': notifications_list,
        'group_task': group_task,
    }
    return render(request, 'base/group-task-history.html', context)   

            