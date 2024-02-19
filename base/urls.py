from django.urls import path
from .views import TaskListView, TaskCreateView, TaskUpdateView, DeleteView, CustomLoginView, RegisterPage, CalendarView, DailyTaskList 
# from .views import CustomLogoutView
from django.contrib.auth.views import LogoutView

from .views import TaskDetailView


urlpatterns =[
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    # path('logout/', CustomLogoutView(), name='logout'),
    path('register/', RegisterPage.as_view(), name='register'),

    path('', TaskListView.as_view(), name='tasks'),
    # path('task/<int:pk>/', TaskDetail.as_view(), name='task'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('tasks/<int:year>/<int:month>/<int:day>', DailyTaskList, name='tasks_for_day'),

    path('task-create/', TaskCreateView.as_view(), name='task-create'),
    path('task-update/<int:pk>/', TaskUpdateView.as_view(), name='task-update'),
    path('task-delete/<int:pk>/', DeleteView.as_view(), name='task-delete'),

]


# urlpatterns = [
#     path('tasks/<int:year>/<int:month>/<int:day>/', views.view_tasks_for_day, name='view_tasks_for_day'),
#     path('tasks/create/', views.create_task, name='create_task'),
#     # other paths as needed
# ]
