from django.apps import AppConfig



class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    def ready(self):
        import base.signals
        from .background import create_email_schedule, create_task_schedule, delete_schedule_checks, create_regular_task_check_schedule

        delete_schedule_checks()
        create_task_schedule()
        create_email_schedule()
        create_regular_task_check_schedule()
