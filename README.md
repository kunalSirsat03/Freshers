# Unofficial Freshers registration

Django event site with database-managed public content, Django admin editing, and a configurable Google Form registration link. The existing staff dashboard also supports local registration/payment review and QR check-in.

## Local development

1. Create/activate a virtual environment and install `requirements.txt`.
2. Copy `.env.example` to `.env`. Keep `DJANGO_DEBUG=True` for local development.
3. Run `python manage.py migrate` and `python manage.py createsuperuser`.
4. Run `python manage.py runserver` and open `/`.
5. Sign in at `/admin/`; organizer dashboard is at `/organizer/`.

## Managing event content

Open **Event settings** in Django admin to edit the event name, organizer, date, venue, ticket price, description, Google Form URL, poster/hero images, contact details, and social links. Add and order gallery images, videos, schedule items, rules, FAQs, and contacts from their respective admin sections. Unpublished records are not shown on the public page. Uploaded files are served from `MEDIA_ROOT` during local development; configure persistent or object storage for production uploads.

Set the Google Form's public URL in Event settings. Public registration buttons open that form. Capacity and registration totals remain in the staff dashboard and are not included on the public page or public event-status response. Google Sheets response synchronization requires the Apps Script setup below; until configured, form responses will not appear in Django. The existing registration/payment metrics still reflect Django records only.

## Google Form response sync

The staff dashboard's **Form responses** page receives rows from the linked response Sheet. To enable it:

1. Set `GOOGLE_FORMS_WEBHOOK_TOKEN` to a long random secret in Django's environment.
2. Open the Google Form's linked response Sheet, choose **Extensions → Apps Script**, and add the source in `scripts/google_forms_sync.gs`.
3. In Apps Script **Project Settings → Script Properties**, set `DJANGO_WEBHOOK_URL` to `https://YOUR-DOMAIN/api/google-form/responses/` and `DJANGO_WEBHOOK_TOKEN` to the same secret.
4. Run `syncExistingResponses` once to import prior rows and grant the requested permissions.
5. Add an installable trigger for `onFormSubmit`, using the spreadsheet as the event source and **On form submit** as the event type.
6. Sign in to Django staff at `/organizer/` and open **Form responses**.

The Django endpoint must be reachable over HTTPS by Google Apps Script. Do not publish the response Sheet: attendee data is sent through the token-protected webhook and displayed only to staff. Imported answers are stored verbatim as JSON; this does not automatically verify payments, create tickets, or generate QR codes.

When DEBUG is enabled, confirmation emails are printed to the runserver terminal. Registration data is stored in SQLite locally.

## Organizer workflow

- Staff users review pending payments in the dashboard or Django admin.
- Approving a payment records the reviewer and timestamp, then emails each attendee a private ticket link and unique QR code.
- The attendee ticket page is available only after payment verification.
- Logged-in staff can open a QR ticket and check in that attendee, or submit a scanned token at the dashboard.
- Rejected bookings release reserved capacity. Pending and verified bookings reserve capacity.
- CSV export and all attendee/payment data are staff-only.

## Production deployment

Use PostgreSQL. Production startup deliberately fails unless `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_SECRET_KEY`, and `POSTGRES_DB` are configured. Set the remaining PostgreSQL credentials and `POSTGRES_SSLMODE=require` if required by your provider. Configure SMTP (`EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and `DEFAULT_FROM_EMAIL`) so verified attendees receive their tickets. Set `DJANGO_CSRF_TRUSTED_ORIGINS` to comma-separated HTTPS origins where needed.

Before serving traffic:

1. Set production environment variables in the hosting provider; never commit `.env` or real secrets.
2. Run `python manage.py migrate` and `python manage.py collectstatic --noinput`.
3. Run with Gunicorn, for example `gunicorn freshers_project.wsgi:application --bind 0.0.0.0:$PORT`.
4. Terminate HTTPS at the platform proxy; Django uses the forwarded HTTPS header, secure cookies, HSTS, and HTTPS redirects when DEBUG is disabled.

SQLite does not provide the row-locking guarantee needed for simultaneous bookings. Production PostgreSQL serializes reservations on the event settings row to keep the configured capacity from being exceeded.
