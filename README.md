# food4thought
### Web development bachelor project by Lewis Burtt-Smith and Dan Eskildsen

<img src="https://github.com/daescoGit/food4thought-bachelorproject/blob/main/deals_project/static/f4t.svg" width="400" />

Required installations:
- Python
- Django
- Docker
- Redis

Local install instructions:
- Set up environment (optional)
- pip install -r requirements.txt
- docker run -p 6379:6379 -d redis:5
- python manage.py makemigrations
- Enter your current region code when prompted https://da.wikipedia.org/wiki/ISO_3166-2:DK (eg. 84)
- python manage.py migrate
- python manage.py rqworker (for email processes)
- python manage.py runserver (in settings.py dir) (new terminal)
