from calendar import HTMLCalendar
from datetime import datetime

class MyCalendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(MyCalendar, self).__init__()

    def today(self):
        today = datetime.now()
        return today

    # formats a day as a td
    def formatday(self, day, specifiedday):
        day_today = self.today()
        
        href_link = f'/tasks/{specifiedday[0]}/{specifiedday[1]}/{day}'

        if day != 0:
            if day == day_today.day and specifiedday[0] == day_today.year and specifiedday[1] == day_today.month:
                return f"<td id='today'><span class='date'><a href='{href_link}'>{day}</a></span></td>"
            return f"<td><span class='date'><a href='{href_link}'>{day}</a></span></td>"
        return "<td></td>"

    # formats a week as a tr
    def formatweek(self, theweek, specifiedday):
        week = ""
        for d, weekday in theweek:
            week += self.formatday(d,specifiedday)
        return f"<tr> {week} </tr>"

    # formats a month as a table
    def formatmonth(self, withyear=True):
        cal = (
            '<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        )  
        cal += (
            f"{self.formatmonthname(self.year, self.month, withyear=withyear)}\n" #February 2024
        )  
        cal += f"{self.formatweekheader()}\n" #Headers - Mon, Tue, etc.
        specifiedday = (self.year, self.month)
        for week in self.monthdays2calendar(self.year, self.month): #searching through list of tuples with day numbers and their types of days, Mondays, Tuesdays etc.
            cal += f"{self.formatweek(week, specifiedday)}\n" #formatting week by week
        return cal


    # def __init__(self):
    #     super().__init__()

    # def formatday(self, day):
    #     if day != 0:
    #         return f'<td>{day}</td>'
    #     return '<td></td>'
    
    
    # def formatweek(self, theweek):
    #     week = ''
    #     for day in theweek:
    #         week += self.formatday(day)
    #     return '<tr>%s</tr>' % week
    

    # def formatmonth(self, year, month):
    #     weeks = self.monthdays2calendar(year, month)
    #     month_str = ''
    #     for week in weeks:
    #         month_str += self.formatweek(week)
    #     return month_str