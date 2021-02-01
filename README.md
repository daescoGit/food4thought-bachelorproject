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
- cd into deals_project (settings.py dir)
- python manage.py makemigrations
- Put 84 as default region code when prompted
- python manage.py migrate
- python manage.py rqworker (for email processes, not required for demo)
- python manage.py runserver (new terminal if rqworker is running)
