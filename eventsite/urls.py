from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/event/", views.event_status, name="event_status"),
    path("api/payment-qr/", views.payment_qr, name="payment-qr"),
    path("api/register/", views.register, name="register"),
    path("organizer/", views.organizer_dashboard, name="organizer-dashboard"),
    path("organizer/form-responses/", views.google_form_responses, name="google-form-responses"),
    path("api/google-form/responses/", views.google_form_response_webhook, name="google-form-webhook"),
    path(
        "organizer/registration/<str:registration_id>/<str:action>/",
        views.review_payment,
        name="review-payment",
    ),
    path("organizer/check-in/", views.check_in_ticket, name="check-in-ticket"),
    path("organizer/export.csv", views.export_registrations, name="export-registrations"),
    path("ticket/<uuid:qr_token>/", views.ticket_detail, name="ticket-detail"),
]