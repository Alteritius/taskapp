from typing import Any
from django.forms.models import BaseModelForm
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic import TemplateView
import calendar
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login 

from .models import Task

from .forms import TaskForm

from .html_cal import MyCalendar

from datetime import timedelta, datetime, date


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__' #it makes the form on login.html get all fields the user have - username and password
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')
    
# def CustomLogoutView():
#     return redirect('login')

class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm #this has to be changed later, I want the registering person to provide mail

    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs): #function to manually override function get to redirect logged in user from RegisterPage  
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)




class TaskListView(LoginRequiredMixin,  ListView):
    model = Task
    context_object_name = 'tasks'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            
            context['tasks'] = context['tasks'].filter(title__icontains=search_input) #another option is title_icontains or __startwith

        context['search_input'] = search_input
        return context
    
    def get(self, request, *args, **kwargs):

        last_visited_url = request.get_full_path()

        request.session['last_visited_url'] = last_visited_url

        return super().get(request, *args, **kwargs)
    

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split("-"))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = "month=" + str(prev_month.year) + "-" + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = "month=" + str(next_month.year) + "-" + str(next_month.month)
    return month


class CalendarView(LoginRequiredMixin, TemplateView):
    
    template_name = "base/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get("month", None)) #the way to get today's date
        cal = MyCalendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context["calendar"] = mark_safe(html_cal)
        context["prev_month"] = prev_month(d)
        context["next_month"] = next_month(d)
        return context
    

def DailyTaskList(request, year, month, day):
    tasks = Task.objects.filter(start_time__year__lte = year, end_time__year__gte = year, 
                                start_time__month__lte = month, end_time__month__gte = month,
                                start_time__day__lte = day, end_time__day__gte = day
                                )
    count = tasks.filter(complete=False).count()
    request.session['last_visited_url'] = request.get_full_path()
    return render(request, 'base/task_list_day.html', {'tasks': tasks, 
                                                       'year': year, 
                                                       'month': month, 
                                                       'day': day, 
                                                       'count': count})




# class CalendarView(LoginRequiredMixin, TemplateView):
    
#     template_name = 'base/calendar.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['calendar'] = MyCalendar().formatmonth(datetime.now().year, datetime.now().month)
#         # context['week'] = MyCalendar().formatweek()
#         # context['day'] = MyCalendar().formatday()
#         return context

    

    # def get(self, request):
    #     calendar = MyCalendar().formatmonth(datetime.now().year, datetime.now().month)
    #     return render(request, 'base/calendar.html', {'calendar': calendar})


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task

    form_class = TaskForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreateView, self).form_valid(form)
    
    def get_success_url(self):
        
        last_visited_url = self.request.session.get('last_visited_url')
        if last_visited_url:
            return last_visited_url
        else:
            return reverse_lazy('tasks') 


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task

    form_class = TaskForm

    def get_success_url(self):
        
        last_visited_url = self.request.session.get('last_visited_url')
        if last_visited_url:
            return last_visited_url
        else:
            return reverse_lazy('tasks') 

class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name ='task' #the same name specified in the TaskDetail() class

    def get_success_url(self):
        
        last_visited_url = self.request.session.get('last_visited_url')
        if last_visited_url:
            return last_visited_url
        else:
            return reverse_lazy('tasks') 
