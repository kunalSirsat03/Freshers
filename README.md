# Unofficial Freshers '26

A Django-rendered event information site. Registration and payment stay in the organizers' existing Google Form and linked workflow; this website does not store participant, payment, ticket, or check-in data.

## Local setup

1. Create and activate a virtual environment, then install Python dependencies:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` if you need to override the default Google Form URL or website contact email. Export the values in that file in your shell before running Django; `.env` is intentionally not loaded by the app.

3. Install the Tailwind CLI and build the stylesheet:

   ```powershell
   npm install
   npm run css:build
   ```

4. Start Django:

   ```powershell
   py manage.py migrate
   py manage.py runserver
   ```

Open <http://127.0.0.1:8000/>. During design work, run `npm run css:watch` in a second terminal.

## Production

Set `DJANGO_DEBUG=False`, a unique `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and a PostgreSQL `DATABASE_URL` in the deployment environment. Set `GOOGLE_FORM_URL` to the verified form. Then run:

```sh
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```

Static files are served by WhiteNoise. The form URL is read once from Django settings and used by every registration CTA. The post-form dialog is an informational handoff only: Google Forms does not notify this site of a submission, so organizers must verify responses and confirm tickets. No public attendee or capacity count is shown. If the Google Form itself does not enforce its response limit, organizers must close it manually at the agreed capacity.