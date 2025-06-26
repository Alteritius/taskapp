from django.urls import path
from .views import CustomLoginView, RegisterPage, CalendarPageMonth, DailyTaskList
from .views import TodayTaskList, DashboardPage, ProfilePage, UpdateProfilePage, GroupListPage, GroupCreatePage, GroupDetailPage
from .views import CalendarPageYear, CalendarPageWeek, TaskCreatePage, TaskUpdatePage, TaskDeletePage
from .views import GroupInviteList, GroupInviteDetail, GroupUpdatePage, AcceptGroupInvite, RejectGroupInvite, DeleteGroupInvite
from .views import GroupTaskCreatePage, DeleteGroupMember, DeleteGroup, GroupTaskDetailPage, GroupTaskUpdatePage, GroupTaskDeleteFile, GroupTaskDeletePage, GroupTaskHistoryPage
from .views import NotificationListPage, NotificationDetailPage, NotificationDeletePage, NotificationDeleteManyPage
from django.contrib.auth.views import LogoutView



urlpatterns =[
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterPage.as_view(), name='register'),

    path('profile/<int:pk>', ProfilePage, name='profile'),
    path('profile/update', UpdateProfilePage, name='update-profile'),

    path('groups/', GroupListPage, name='group-list'),
    path('group-create/', GroupCreatePage, name='group-create'),
    path('group-update/<int:gpk>', GroupUpdatePage, name='group-update'),
    path('group/<int:gpk>', GroupDetailPage, name='group-detail'),
    
    path('group/<int:gpk>/group-member-delete/<int:pk>', DeleteGroupMember, name='group-member-delete'),
    path('group/<int:gpk>/delete/', DeleteGroup, name='group-delete'),


    path('groups/invites/', GroupInviteList, name='invite-list'),
    path('groups/invites/<int:pk>', GroupInviteDetail, name='invite-detail'),
    path('groups/invites/accept/<int:pk>', AcceptGroupInvite, name='invite-accept'),
    path('groups/invites/reject/<int:pk>', RejectGroupInvite, name='invite-reject'),
    path('groups/invites/delete/<int:pk>', DeleteGroupInvite, name='invite-delete'),

    path('group/<int:gpk>/group-task-create/', GroupTaskCreatePage, name='group-task-create'),
    path('group/<int:gpk>/group-task-detail/<int:gtpk>', GroupTaskDetailPage, name='group-task-detail'),
    path('group/<int:gpk>/group-task-update/<int:gtpk>', GroupTaskUpdatePage, name='group-task-update'),
    path('group/<int:gpk>/group-task-delete/<int:gtpk>', GroupTaskDeletePage, name='group-task-delete'),
    path('group/<int:gpk>/group-task-delete-file/<int:gtpk>/<str:file_name>', GroupTaskDeleteFile, name='group-task-delete-file'),
    path('group/<int:gpk>/group-task/<int:gtpk>/history/', GroupTaskHistoryPage, name='group-task-history'),

    path('notifications/', NotificationListPage, name='notifications-list'),
    path('notifications/<str:Ntype>/<int:pk>', NotificationDetailPage, name='notification-detail'),
    path('notifications/delete/<str:Ntype>/<int:pk>', NotificationDeletePage, name='notification-delete'),
    path('notifications/delete/many/', NotificationDeleteManyPage, name='notifications-delete-many'),



    path('calendar/', CalendarPageMonth, name='calendar'),
    path('calendar/year/', CalendarPageYear, name='calendar-year'),
    path('calendar/week/', CalendarPageWeek, name='calendar-week'),
    path('tasks/<int:year>/<int:month>/<int:day>', DailyTaskList, name='tasks_for_day'),
    path('tasks/today', TodayTaskList, name='tasks_for_today'),

    path('dashboard', DashboardPage, name='dashboard'),


    path('task-create/<str:weekday>/', TaskCreatePage, name='task-create'),
    path('task-update/<int:tpk>/', TaskUpdatePage, name='task-update'),
    path('task-delete/<int:tpk>/', TaskDeletePage, name='task-delete'),


]

