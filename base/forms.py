from django import forms
from .models import Task, Profile, CustomGroup, GroupTask, GroupMember
from django.contrib.auth.models import User

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
                                                  'type': 'datetime-local'
                                                  }),
            'end_time': forms.DateTimeInput(attrs={ 'class': 'task-form',
                                                'type': 'datetime-local'
                                                }),
            'complete': forms.CheckboxInput(attrs={ 'class': 'task-form',
                                                'type': 'boolean'
                                                }),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model=User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={ 'class': 'task-form'}),
            'email': forms.EmailInput(attrs={ 'class': 'task-form',
                                             'type': 'email',
                                             'placeholder': 'Write down your email adress...'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user']
        widgets = {
            'bio': forms.Textarea(attrs={ 'class': 'task-form'}),
        }


class GroupForm(forms.ModelForm):
    class Meta:
        model = CustomGroup
        fields = ('name', 'description', 'participants')

    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget = forms.CheckboxSelectMultiple,
        required = False
    )


class GroupTaskForm(forms.ModelForm):
    class Meta:
        model = GroupTask
        fields = ('title', 'description', 'member', 'status', 'start_time', 'end_time', 'group_files')
        widgets = {
            'start_time': forms.DateTimeInput(attrs={ 'class': 'task-form',
                                                  'type': 'datetime-local'
                                                  }),
            'end_time': forms.DateTimeInput(attrs={ 'class': 'task-form',
                                                'type': 'datetime-local'
                                                }),
        }

    member = forms.ModelChoiceField(queryset=GroupMember.objects.all())
    status = forms.ChoiceField(choices=GroupTask.STATUS_CHOICES)
