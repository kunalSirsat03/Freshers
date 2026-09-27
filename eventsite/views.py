import base64
import csv
import json
import secrets
from io import BytesIO
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.db.models import Q, Sum, TextField
from django.db.models.functions import Cast
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date, parse_datetime
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import (
    EventContact,
    EventFAQ,
    EventRule,
    EventSettings,
    EventVideo,
    GoogleFormSubmission,
    GalleryImage,
    Payment,
    Registration,
    ScheduleItem,
    Ticket,
)


def _event_settings():
    event, _ = EventSettings.objects.get_or_create(
        pk=1,
        defaults={"registration_url": settings.EVENT_REGISTRATION_URL},
    )
    if not event.registration_url and settings.EVENT_REGISTRATION_URL:
        event.registration_url = settings.EVENT_REGISTRATION_URL
        event.save(update_fields=("registration_url",))
    return event


def _send_confirmed_tickets(request, registration_id):
    registration = Registration.objects.prefetch_related("tickets").get(pk=registration_id)
    for ticket in registration.tickets.all():
        ticket_url = request.build_absolute_uri(
            reverse("ticket-detail", kwargs={"qr_token": ticket.qr_token})
        )
        try:
            send_mail(
                subject="Your Unofficial Freshers ticket is confirmed",
                message=(
                    f"Hi {ticket.attendee_name},\n\n"
                    f"Your payment has been verified. Your registration ID is "
                    f"{registration.registration_id}.\n"
                    f"Open your mobile ticket and QR code here: {ticket_url}\n\n"
                    "Please bring your college ID to the event."
                ),
                from_email=None,
                recipient_list=[ticket.email],
                fail_silently=False,
            )
        except Exception:
            messages.warning(
                request,
                f"Payment verified, but the ticket email to {ticket.email} could not be sent. "
                "Share the ticket link from this dashboard.",
            )


def _booked_count():
    return (
        Registration.objects.exclude(payment__status=Payment.STATUS_REJECTED)
        .aggregate(total=Sum("ticket_quantity"))["total"]
        or 0
    )


def home(request):
    settings = _event_settings()
    published_gallery = GalleryImage.objects.filter(is_published=True).exclude(
        image="", image_url=""
    )
    return render(
        request,
        "fresher_cinematic.html",
        {
            "event": settings,
            "gallery": published_gallery.filter(
                collection=GalleryImage.COLLECTION_GENERAL
            ).order_by("-featured", "sort_order", "pk"),
            "archive_gallery": published_gallery.filter(
                collection=GalleryImage.COLLECTION_PREVIOUS
            ).order_by("-featured", "sort_order", "pk"),
            "venue_gallery": published_gallery.filter(
                collection=GalleryImage.COLLECTION_VENUE
            ).order_by("-featured", "sort_order", "pk"),
            "previous_videos": EventVideo.objects.filter(
                is_published=True, edition=EventVideo.EDITION_PREVIOUS
            ),
            "schedule": ScheduleItem.objects.filter(is_published=True),
            "rules": EventRule.objects.filter(is_published=True),
            "faqs": EventFAQ.objects.filter(is_published=True),
            "contacts": EventContact.objects.filter(is_published=True),
        },
    )


@csrf_exempt
@require_POST
def google_form_response_webhook(request):
    expected_token = settings.GOOGLE_FORMS_WEBHOOK_TOKEN
    supplied_token = request.headers.get("X-Webhook-Token", "")
    if not expected_token:
        return JsonResponse({"error": "Response sync is not configured."}, status=503)
    if not secrets.compare_digest(supplied_token, expected_token):
        return JsonResponse({"error": "Unauthorized."}, status=403)
    if len(request.body) > 1_000_000:
        return JsonResponse({"error": "Response payload is too large."}, status=413)

    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"error": "Expected a JSON object."}, status=400)

    external_id = str(payload.get("response_id", "")).strip()
    responses = payload.get("responses")
    if not external_id or len(external_id) > 200 or not isinstance(responses, dict):
        return JsonResponse({"error": "A response_id and responses object are required."}, status=400)

    submitted_at_value = payload.get("submitted_at")
    submitted_at = parse_datetime(str(submitted_at_value)) if submitted_at_value else None
    if submitted_at_value and not submitted_at:
        return JsonResponse({"error": "submitted_at must be an ISO 8601 datetime."}, status=400)
    if submitted_at and timezone.is_naive(submitted_at):
        submitted_at = timezone.make_aware(submitted_at, timezone.get_current_timezone())

    submission, created = GoogleFormSubmission.objects.update_or_create(
        external_id=external_id,
        defaults={"submitted_at": submitted_at, "responses": responses},
    )
    return JsonResponse(
        {"ok": True, "response_id": submission.external_id, "created": created},
        status=201 if created else 200,
    )


@staff_member_required
@require_GET
def google_form_responses(request):
    query = request.GET.get("q", "").strip()
    submissions = GoogleFormSubmission.objects.all()
    if query:
        submissions = submissions.annotate(
            response_text=Cast("responses", output_field=TextField())
        ).filter(Q(external_id__icontains=query) | Q(response_text__icontains=query))

    display_responses = []
    for submission in submissions[:500]:
        fields = []
        for label, value in submission.responses.items():
            if isinstance(value, list):
                value = ", ".join(str(item) for item in value)
            elif isinstance(value, dict):
                value = json.dumps(value, ensure_ascii=False)
            fields.append({"label": label, "value": str(value)})
        display_responses.append({"submission": submission, "fields": fields})

    return render(
        request,
        "form_responses.html",
        {
            "responses": display_responses,
            "query": query,
            "total_responses": GoogleFormSubmission.objects.count(),
        },
    )


@require_GET
def event_status(request):
    event = _event_settings()
    return JsonResponse({
        "title": event.title,
        "event_date": event.event_date.isoformat(),
        "venue": event.venue,
        "ticket_price": event.ticket_price,
        "registration_url": event.registration_url,
    })


@require_GET
def payment_qr(request):
    event = _event_settings()
    try:
        amount = int(request.GET.get("amount", ""))
    except ValueError:
        return HttpResponse(status=400)
    if event.ticket_price <= 0 or amount <= 0 or amount % event.ticket_price:
        return HttpResponse(status=400)
    quantity = amount // event.ticket_price
    if quantity > 5:
        return HttpResponse(status=400)

    import qrcode

    payment_uri = "upi://pay?" + urlencode({
        "pa": event.upi_id,
        "pn": event.title,
        "am": str(amount),
        "cu": "INR",
        "tn": "Freshers tickets",
    })
    image_buffer = BytesIO()
    qrcode.make(payment_uri).save(image_buffer, format="PNG")
    return HttpResponse(image_buffer.getvalue(), content_type="image/png")


def _validated_participants(attendees):
    if not isinstance(attendees, list) or not 1 <= len(attendees) <= 5:
        return None, "Choose between 1 and 5 attendees."

    clean_attendees = []
    for attendee in attendees:
        if not isinstance(attendee, dict):
            return None, "Attendee details are incomplete."
        person = {
            "name": str(attendee.get("name", "")).strip(),
            "department": str(attendee.get("department", "")).strip(),
            "year": str(attendee.get("year", "")).strip(),
            "phone": str(attendee.get("phone", "")).strip(),
            "email": str(attendee.get("email", "")).strip(),
        }
        if (
            not all(person.values())
            or len(person["name"]) > 100
            or len(person["department"]) > 80
            or len(person["year"]) > 40
            or len(person["phone"]) != 10
            or not person["phone"].isdigit()
            or len(person["email"]) > 254
        ):
            return None, "Check each attendee's name, department, year, phone, and email."
        try:
            validate_email(person["email"])
        except ValidationError:
            return None, "Enter a valid email address for each attendee."
        clean_attendees.append(person)
    return clean_attendees, None


@require_POST
def register(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid request data."}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({"error": "Invalid request data."}, status=400)

    attendees, error = _validated_participants(data.get("participants"))
    if error:
        return JsonResponse({"error": error}, status=400)

    utr = str(data.get("utr_number", "")).strip()
    if len(utr) < 8 or len(utr) > 40:
        return JsonResponse({"error": "Enter a valid UPI reference number."}, status=400)

    try:
        with transaction.atomic():
            event = EventSettings.objects.select_for_update().get_or_create(pk=1)[0]
            booked = _booked_count()
            quantity = len(attendees)
            if booked + quantity > event.capacity:
                return JsonResponse({"error": "There are not enough tickets remaining."}, status=409)

            registration = Registration.objects.create(
                participants=attendees,
                ticket_quantity=quantity,
                total_amount=quantity * event.ticket_price,
            )
            Payment.objects.create(
                registration=registration,
                utr_number=utr,
                amount=registration.total_amount,
            )
            Ticket.objects.bulk_create([
                Ticket(
                    registration=registration,
                    attendee_name=person["name"],
                    department=person["department"],
                    year=person["year"],
                    phone=person["phone"],
                    email=person["email"],
                )
                for person in attendees
            ])
    except IntegrityError:
        return JsonResponse({"error": "That UPI reference has already been submitted."}, status=409)

    return JsonResponse({
        "registration_id": registration.registration_id,
        "total_amount": registration.total_amount,
        "payment_status": Payment.STATUS_PENDING,
        "attendee": attendees[0]["name"],
    }, status=201)


@staff_member_required
def organizer_dashboard(request):
    event = _event_settings()
    status = request.GET.get("status", "")
    query = request.GET.get("q", "").strip()
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    registrations = Registration.objects.select_related("payment").prefetch_related("tickets").order_by("-created_at")
    if status in {choice[0] for choice in Payment.STATUS_CHOICES}:
        registrations = registrations.filter(payment__status=status)
    if query:
        registrations = registrations.filter(
            Q(registration_id__icontains=query)
            | Q(payment__utr_number__icontains=query)
            | Q(tickets__attendee_name__icontains=query)
            | Q(tickets__email__icontains=query)
        ).distinct()
    parsed_date_from = parse_date(date_from) if date_from else None
    parsed_date_to = parse_date(date_to) if date_to else None
    if parsed_date_from:
        registrations = registrations.filter(created_at__date__gte=parsed_date_from)
    if parsed_date_to:
        registrations = registrations.filter(created_at__date__lte=parsed_date_to)

    context = {
        "event": event,
        "registrations": registrations[:100],
        "query": query,
        "selected_status": status,
        "date_from": date_from if parsed_date_from else "",
        "date_to": date_to if parsed_date_to else "",
        "total_registrations": Registration.objects.count(),
        "confirmed_count": Payment.objects.filter(status=Payment.STATUS_VERIFIED).count(),
        "pending_count": Payment.objects.filter(status=Payment.STATUS_PENDING).count(),
        "rejected_count": Payment.objects.filter(status=Payment.STATUS_REJECTED).count(),
        "booked": _booked_count(),
        "remaining_capacity": max(0, event.capacity - _booked_count()),
        "checked_in_count": Ticket.objects.filter(checked_in_at__isnull=False).count(),
        "revenue": Payment.objects.filter(status=Payment.STATUS_VERIFIED).aggregate(
            total=Sum("amount")
        )["total"] or 0,
    }
    return render(request, "organizer.html", context)


@staff_member_required
@require_POST
def review_payment(request, registration_id, action):
    if action not in {"verify", "reject"}:
        raise Http404
    with transaction.atomic():
        payment = get_object_or_404(
            Payment.objects.select_for_update().select_related("registration"),
            registration__registration_id=registration_id,
        )
        if payment.status != Payment.STATUS_PENDING:
            messages.warning(request, "This payment has already been reviewed.")
        else:
            payment.status = (
                Payment.STATUS_VERIFIED if action == "verify" else Payment.STATUS_REJECTED
            )
            payment.verified_by = request.user
            payment.verified_at = timezone.now()
            payment.save(update_fields=("status", "verified_by", "verified_at"))
            messages.success(request, "Payment verified." if action == "verify" else "Payment rejected.")
            if action == "verify":
                transaction.on_commit(
                    lambda: _send_confirmed_tickets(request, payment.registration_id)
                )
    return redirect("organizer-dashboard")


@staff_member_required
@require_POST
def check_in_ticket(request):
    token = request.POST.get("qr_token", "").strip()
    try:
        with transaction.atomic():
            ticket = get_object_or_404(
                Ticket.objects.select_for_update().select_related("registration__payment"),
                qr_token=token,
            )
            if ticket.registration.payment.status != Payment.STATUS_VERIFIED:
                messages.error(request, "This ticket is not confirmed; payment must be verified first.")
            elif ticket.checked_in_at:
                messages.warning(request, f"Already checked in at {ticket.checked_in_at:%H:%M}.")
            else:
                ticket.checked_in_at = timezone.now()
                ticket.checked_in_by = request.user
                ticket.save(update_fields=("checked_in_at", "checked_in_by"))
                messages.success(request, f"Checked in {ticket.attendee_name}.")
    except (ValueError, ValidationError):
        messages.error(request, "Enter a valid ticket QR token.")
    return redirect("organizer-dashboard")


@staff_member_required
@require_GET
def export_registrations(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="freshers-registrations.csv"'
    response.write("\ufeff")
    writer = csv.writer(response)
    writer.writerow([
        "Registration ID", "Payment status", "UTR", "Amount", "Created at",
        "Attendee", "Department", "Year", "Phone", "Email", "Checked in at",
    ])
    tickets = Ticket.objects.select_related("registration__payment").order_by(
        "registration__created_at", "id"
    )
    for ticket in tickets.iterator():
        writer.writerow([
            ticket.registration.registration_id,
            ticket.registration.payment.status,
            ticket.registration.payment.utr_number,
            ticket.registration.payment.amount,
            ticket.registration.created_at.isoformat(),
            ticket.attendee_name,
            ticket.department,
            ticket.year,
            ticket.phone,
            ticket.email,
            ticket.checked_in_at.isoformat() if ticket.checked_in_at else "",
        ])
    return response


@require_GET
def ticket_detail(request, qr_token):
    ticket = get_object_or_404(
        Ticket.objects.select_related("registration__payment"), qr_token=qr_token
    )
    if ticket.registration.payment.status != Payment.STATUS_VERIFIED:
        raise Http404

    import qrcode

    ticket_url = request.build_absolute_uri(
        reverse("ticket-detail", kwargs={"qr_token": ticket.qr_token})
    )
    image = qrcode.make(ticket_url)
    image_buffer = BytesIO()
    image.save(image_buffer, format="PNG")
    qr_image = "data:image/png;base64," + base64.b64encode(image_buffer.getvalue()).decode("ascii")
    return render(request, "ticket.html", {"ticket": ticket, "qr_image": qr_image, "event": _event_settings()})