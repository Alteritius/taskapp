from django import forms
from .models import Task

class TaskForm(forms.ModelForm):

    complete = forms.BooleanField(
        required=False
    )

    class Meta:
        model = Task
        fields = ('title', 'description', 'start_time', 'end_time', 'complete')
        widgets = {
            'title': forms.TextInput(attrs={ 'class': 'task-form'}),
            'description': forms.Textarea(attrs={ 'class': 'task-form'}),
            'start_time': forms.DateTimeInput(attrs={ 'class': 'task-form',
                                                  'type': 'datetime-local',
                                                  'placeholder': 'dd-mm-rrrr hh:mm'}),
            'end_time': forms.DateTimeInput(attrs={ 'class': 'task-form',
                                                'type': 'datetime-local',
                                                'placeholder': 'dd-mm-rrrr hh:mm'}),
        }


# class TaskForm(forms.Form): #It would work for non-class based view

#     task_title = forms.CharField(
#         max_length=200,
#         label="title",
#         required=True,
#         widget=forms.TextInput(attrs={
#             'class': 'task-form'
#         }),
#     )
#     task_desc = forms.CharField(
#         label="description",
#         required=False,
#         widget=forms.Textarea(attrs={
#             'class': 'task-form'
#         }),
#     )
#     task_starttime = forms.DateTimeField(
#         label="start_time",
#         widget=forms.DateInput(
#             attrs={
#                 'class': 'task-form',
#                 'type': 'datetime-local'
#             }
#         ),
#     )
#     task_endtime = forms.DateTimeField(
#         label="end_time",
#         widget=forms.DateInput(
#             attrs={
#                 'class': 'task-form',
#                 'type': 'datetime-local'
#             }
#         ),
#     )
#     task_complete = forms.BooleanField(
#         label="complete",
#     )

    # start_time = models.DateTimeField(default=timezone.now) #in the future - change it to (null=True, blank=True) and change not to add seconds
    # end_time = models.DateTimeField(default=timezone.now) #in the future - change it to (null=True, blank=True)
    # complete = models.BooleanField(default=False)