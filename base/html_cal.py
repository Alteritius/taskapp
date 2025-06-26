from calendar import HTMLCalendar
from datetime import datetime
from .models import Task, GroupMember, GroupTask
from django.db.models import Q

class MyCalendar(HTMLCalendar):
    def __init__(self, year=None, month=None, user=None):
        self.year = year
        self.month = month
        self.user = user
        super(MyCalendar, self).__init__()

    def today(self):
        today = datetime.now()
        return today
    
    def month_name(self, index):

        match index:
            case 1:
                return "January"
            case 2:
                return "February"
            case 3:
                return "March"
            case 4:
                return "April"
            case 5:
                return "May"
            case 6:
                return "June"
            case 7:
                return "July"
            case 8:
                return "August"
            case 9:
                return "September"
            case 10:
                return "October"
            case 11:
                return "November"
            case 12:
                return "December"
            


    def check_tasks(self, day, month, year):

        date = str(year) + '-' + str(month) + '-' + str(day)

        # today_date = self.today()

        if day < 1 or month < 1:
            return [0,0,0,0,0]
        
        else:

            list_of_tasks = Task.objects.filter(Q(user=self.user, start_time__date__lte = date, end_time__date__gte = date))

            completed_tasks = list_of_tasks.filter(Q(status = 'completed'))

            overdue_tasks = list_of_tasks.filter(Q(status = 'overdue'))

            pending_tasks = list_of_tasks.filter(Q(status = 'pending'))

            group_member = GroupMember.objects.filter(Q(user=self.user, status='accepted'))

            leader_group_tasks = GroupTask.objects.filter(Q(creator = self.user, start_time__date__lte = date, end_time__date__gte = date))
            member_group_tasks = GroupTask.objects.filter(Q(member__in = group_member, start_time__date__lte = date, end_time__date__gte = date))

            list_of_group_tasks = leader_group_tasks | member_group_tasks

            count = list_of_group_tasks.count()
            count += list_of_tasks.count()
            
            if completed_tasks.exists():
                com = 1
            else:
                com = 0

            if overdue_tasks.exists():
                over = 1
            else:
                over = 0

            if pending_tasks.exists():
                pend = 1
            else: 
                pend = 0
            
            if list_of_group_tasks.exists():
                group = 1
            else:
                group = 0
            
            return [com,over,pend,group,count]

    # formats a day as a td
    def formatday(self, day, specifiedday):
        day_today = self.today()
    
        check = self.check_tasks(day, specifiedday[1], specifiedday[0])

        if check[0]:
            completed_info = '<div class="completed"></div>'
        else:
            completed_info = ''

        if check[1]:
            overdue_info = '<div class="overdue"></div>'
        else:
            overdue_info = ''
        
        if check[2]:
            pending_info = '<div class="pending"></div>'
        else:
            pending_info = ''
        
        if check[3]:
            group_info = '<div class="group"></div>'
        else:
            group_info = ''

        if check[4] != 0:
            # count_of_tasks = f'<div class="count-container"><h4 class="count-of-tasks">Tasks: {check[4]}</h4><div>'
            count_of_tasks = f'<div class="count-container"><h4 class="count-of-tasks">Tasks: {check[4]}</h4></div>'
        else:
            count_of_tasks = ''
        
        href_link = f'/tasks/{specifiedday[0]}/{specifiedday[1]}/{day}'

        if day != 0:
            if day == day_today.day and specifiedday[0] == day_today.year and specifiedday[1] == day_today.month:
                return f"<td id='today'><a href='{href_link}'><div class='date-container'><span class='date'>{day}</span>{completed_info}{overdue_info}{pending_info}{group_info}{count_of_tasks}</a></div></td>"
            return f"<td><a href='{href_link}'><div class='date-container'><span class='date'>{day}</span>{completed_info}{overdue_info}{pending_info}{group_info}{count_of_tasks}</a></div></td>"
        return "<td></td>"

    # formats a week as a tr
    def formatweek(self, theweek, specifiedday):
        week = ""
        for d, weekday in theweek:
            week += self.formatday(d,specifiedday)
        return f"<tr> {week} </tr>"

    # formats a month as a table
    def formatmonth(self):
        cal = (
            '<table class="calendar">\n'
        )  
        cal += (
            
            f'<tr><th colspan="7" class="month">{self.month_name(self.month)} {self.year}</th></tr>\n'
        )
        # print(self.month)
        # f"{self.formatmonthname(self.year, self.month, withyear=withyear)}\n" #February 2024
        # f"<tr><th colspan="7" class="month">{day_today.month} {day_today.year}</th></tr>\n" #current year and month 
        # print(cal)
        cal += f"{self.formatweekheader()}\n" #Headers - Mon, Tue, etc.
        # print(cal)
        specifiedday = (self.year, self.month)
        for week in self.monthdays2calendar(specifiedday[0], specifiedday[1]): #searching through list of tuples with day numbers and their types of days, Mondays, Tuesdays etc.
            cal += f"{self.formatweek(week, specifiedday)}\n" #formatting week by week
        return cal