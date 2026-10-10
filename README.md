# Eddyforge

## Run locally

Install dependencies and start the Django development server from this directory:

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The portfolio pages are served by the `core` app. Static assets are stored in `core/static/core/`.

Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, and `DJANGO_ALLOWED_HOSTS` in the environment before deployment.
