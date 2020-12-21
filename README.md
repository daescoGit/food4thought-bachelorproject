# Food4Thought
### Web development bachelor project by Lewis Burtt-Smith and Dan Eskildsen

Required installations:
- Python
- Django
- Docker
- Redis

Local install instructions:
- Set up environment (optional)
- pip install -r requirements.txt
- docker run -p 6379:6379 -d redis:5
- (rq stuff)
- python manage.py makemigrations
- python manage.py migrate
- python manage.py runserver (in settings.py dir) (rq modified?)
