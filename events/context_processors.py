from django.conf import settings


def event_settings(request):
    return {
        "google_form_url": settings.GOOGLE_FORM_URL,
        "event_contact_email": settings.EVENT_CONTACT_EMAIL,
    }