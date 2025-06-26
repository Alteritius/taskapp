# Taskapp

## About the project:

The project is a to-do list app with some elements of project management apps like Jira.
This version was written in large part using Django.

## How to run:

### Docker:

If you use Docker, use this line in your command prompt:

```
docker-compose up
```

### Local:

Optionally you can create your virtual environment:

```
python -m venv myEnvName
```

Then install requirements/dependencies for the project:

```
pip install -r requirements.txt
```

prepare the database (optionally you can delete the one provided in the repo and create your own sqlite3 database with this command):

```
python manage.py migrate
```

then you can start the app,
the first step is starting qcluster that is a responsible for few background tasks going on in the app:

```
python manage.py qcluster
```

then you can safely run the server:

```
python manage.py runserver
```

#### Optional:

The app has a notification system that uses gmail account to send emails to its users.
For safety reasons I put credentials to the account into my global environment variables which are not shared in this repo.

To change it you have to find settings.py file in taskapp folder and change values for these 2 variables at the end of the file:

```
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
```

Even though Google made it a bit more difficult it's still possible to use a dummy gmail account for that purpose.
You can also just use a third-party service to manage sending emails.
Or just not care about it.
