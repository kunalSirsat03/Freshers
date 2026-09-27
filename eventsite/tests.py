import json

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from eventsite.models import (
    EventFAQ,
    EventSettings,
    EventRule,
    EventVideo,
    GalleryImage,
    GoogleFormSubmission,
    PastYearLink,
    Payment,
    Registration,
    ScheduleItem,
    Ticket,
)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class RegistrationFlowTests(TestCase):
    def setUp(self):
        self.event = EventSettings.objects.create(pk=1)
        self.participant = {
            "name": "Asha Student",
            "department": "Computer",
            "year": "First Year (FE)",
            "phone": "9876543210",
            "email": "asha@example.com",
        }

    def submit_booking(self, *, utr="UPI12345678", participants=None):
        return self.client.post(
            reverse("register"),
            data=json.dumps({
                "participants": participants if participants is not None else [self.participant],
                "utr_number": utr,
            }),
            content_type="application/json",
        )

    def test_public_home_renders_database_content_and_google_form_link(self):
        self.event.registration_url = "https://forms.gle/example-form"
        self.event.save(update_fields=("registration_url",))
        faq = EventFAQ.objects.create(question="When?", answer="See the schedule.")
        unpublished_faq = EventFAQ.objects.create(
            question="Hidden question", answer="Not public.", is_published=False
        )
        rule = EventRule.objects.create(title="Bring ID", description="Show your college ID.")
        schedule = ScheduleItem.objects.create(
            start_time="18:00", title="Doors open", description="Welcome."
        )
        GalleryImage.objects.create(
            image_url="https://images.unsplash.com/photo-1501386761578-eac5c94b800a",
            caption="Welcome night",
            featured=True,
        )
        GalleryImage.objects.create(
            image_url="https://images.unsplash.com/photo-1514525253161-7a46d19cd819",
            caption="Previous party memory",
            collection=GalleryImage.COLLECTION_PREVIOUS,
        )
        GalleryImage.objects.create(
            image_url="https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3",
            caption="Venue photo for Freshers 2026",
            collection=GalleryImage.COLLECTION_VENUE,
        )
        EventVideo.objects.create(
            title="Previous party video",
            url="https://youtu.be/M7lc1UVf-VE",
            edition=EventVideo.EDITION_PREVIOUS,
        )
        EventVideo.objects.create(
            title="Unclassified promo video",
            url="https://youtu.be/aqz-KE-bpKQ",
            edition=EventVideo.EDITION_PROMO,
        )
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title.replace("'", "&#x27;"))
        self.assertContains(response, self.event.registration_url)
        self.assertContains(response, faq.question)
        self.assertContains(response, rule.title)
        self.assertContains(response, schedule.title)
        self.assertContains(response, "Welcome night")
        self.assertContains(response, "https://images.unsplash.com/photo-1501386761578-eac5c94b800a")
        self.assertContains(response, "Previous party memory")
        self.assertContains(response, "Previous party video")
        self.assertContains(response, "Venue photo for Freshers 2026")
        self.assertContains(response, "youtube-nocookie.com/embed/M7lc1UVf-VE")
        self.assertNotContains(response, "Unclassified promo video")
        self.assertNotContains(response, unpublished_faq.question)
        self.assertContains(response, 'id="countDays"')
        self.assertContains(response, "11:00 AM to 6:00 PM")
        self.assertNotContains(response, "tickets remaining")

    @override_settings(EVENT_REGISTRATION_URL="https://forms.gle/rT1QgLVCPCMPLYyv9")
    def test_existing_event_row_receives_configured_google_form_url(self):
        self.event.registration_url = ""
        self.event.save(update_fields=("registration_url",))

        response = self.client.get(reverse("home"))

        self.event.refresh_from_db()
        self.assertEqual(self.event.registration_url, "https://forms.gle/rT1QgLVCPCMPLYyv9")
        self.assertContains(response, "https://forms.gle/rT1QgLVCPCMPLYyv9")
        self.assertContains(response, "Register now")

    def test_public_home_omits_capacity(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, str(self.event.capacity))

    def test_homepage_shows_venue_and_previous_edition_empty_state(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="venue"')
        self.assertContains(response, self.event.venue)
        self.assertContains(response, "View venue map")
        self.assertContains(response, 'id="last-year"')
        self.assertContains(response, "Previous-edition photos and video will appear here.")

    def test_public_home_renders_past_year_links(self):
        PastYearLink.objects.create(
            title="Freshers 2025 recap",
            url="https://example.com/freshers-2025",
            description="A quick look at the previous edition.",
        )
        PastYearLink.objects.create(
            title="Instagram reel",
            url="https://instagram.com/freshers2025",
            description="Highlights reel from last year.",
            is_published=False,
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Freshers 2025 recap")
        self.assertContains(response, "https://example.com/freshers-2025")
        self.assertNotContains(response, "Instagram reel")

    def test_past_year_link_uses_youtube_thumbnail_for_short_links(self):
        link = PastYearLink.objects.create(
            title="Dance Reel 1",
            url="https://youtube.com/shorts/in6gm1NFqow?si=rASaNjGlQz1jkcOB",
        )

        self.assertIn("img.youtube.com/vi/in6gm1NFqow/hqdefault.jpg", link.thumbnail_url)

    def test_public_event_status_does_not_disclose_capacity_or_registration_totals(self):
        response = self.client.get(reverse("event_status"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("capacity", response.json())
        self.assertNotIn("booked", response.json())
        self.assertNotIn("remaining", response.json())

    def test_registration_endpoint_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.get(reverse("home"))
        response = csrf_client.post(
            reverse("register"),
            data=json.dumps({"participants": [self.participant], "utr_number": "UPI12345678"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_booking_creates_pending_payment_and_individual_ticket(self):
        response = self.submit_booking()

        self.assertEqual(response.status_code, 201)
        registration = Registration.objects.get()
        payment = Payment.objects.get(registration=registration)
        ticket = Ticket.objects.get(registration=registration)
        self.assertEqual(payment.status, Payment.STATUS_PENDING)
        self.assertEqual(payment.amount, self.event.ticket_price)
        self.assertEqual(ticket.attendee_name, "Asha Student")
        self.assertEqual(response.json()["registration_id"], registration.registration_id)
        self.assertNotIn("qr_token", response.json())

    def test_invalid_json_shape_is_rejected(self):
        response = self.client.post(
            reverse("register"), data=json.dumps(["not", "an", "object"]),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Registration.objects.count(), 0)

    def test_duplicate_utr_is_rejected_without_second_booking(self):
        self.assertEqual(self.submit_booking().status_code, 201)
        response = self.submit_booking()
        self.assertEqual(response.status_code, 409)
        self.assertEqual(Registration.objects.count(), 1)

    def test_rejected_payment_releases_capacity(self):
        self.event.capacity = 1
        self.event.save(update_fields=("capacity",))
        self.assertEqual(self.submit_booking().status_code, 201)
        Payment.objects.update(status=Payment.STATUS_REJECTED)

        response = self.submit_booking(utr="UPI87654321")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Registration.objects.count(), 2)

    def test_payment_qr_only_accepts_valid_amounts(self):
        valid = self.client.get(reverse("payment-qr"), {"amount": 1500})
        invalid = self.client.get(reverse("payment-qr"), {"amount": 751})
        self.assertEqual(valid.status_code, 200)
        self.assertEqual(valid["Content-Type"], "image/png")
        self.assertEqual(invalid.status_code, 400)

    def test_staff_can_verify_send_ticket_and_check_in_once(self):
        response = self.submit_booking()
        registration = Registration.objects.get(registration_id=response.json()["registration_id"])
        ticket = Ticket.objects.get(registration=registration)
        organizer = get_user_model().objects.create_user(
            username="organizer", password="test-password", is_staff=True
        )
        self.client.force_login(organizer)

        dashboard = self.client.get(reverse("organizer-dashboard"))
        self.assertEqual(dashboard.status_code, 200)
        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            verify_response = self.client.post(reverse(
                "review-payment", kwargs={"registration_id": registration.registration_id, "action": "verify"}
            ))
        self.assertEqual(len(callbacks), 1)
        self.assertEqual(verify_response.status_code, 302)
        payment = registration.payment
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_VERIFIED)
        self.assertEqual(payment.verified_by, organizer)
        self.assertEqual(len(mail.outbox), 1)

        ticket_page = self.client.get(reverse("ticket-detail", kwargs={"qr_token": ticket.qr_token}))
        self.assertEqual(ticket_page.status_code, 200)
        self.assertContains(ticket_page, "Save / print ticket")

        checkin_url = reverse("check-in-ticket")
        first_scan = self.client.post(checkin_url, {"qr_token": str(ticket.qr_token)})
        ticket.refresh_from_db()
        checked_in_at = ticket.checked_in_at
        second_scan = self.client.post(checkin_url, {"qr_token": str(ticket.qr_token)})
        ticket.refresh_from_db()
        self.assertEqual(first_scan.status_code, 302)
        self.assertEqual(second_scan.status_code, 302)
        self.assertEqual(ticket.checked_in_by, organizer)
        self.assertEqual(ticket.checked_in_at, checked_in_at)

    def test_organizer_dashboard_and_export_require_staff(self):
        response = self.client.get(reverse("organizer-dashboard"))
        self.assertEqual(response.status_code, 302)
        staff = get_user_model().objects.create_user(
            username="staff", password="test-password", is_staff=True
        )
        self.client.force_login(staff)
        export = self.client.get(reverse("export-registrations"))
        self.assertEqual(export.status_code, 200)
        self.assertEqual(export["Content-Type"], "text/csv; charset=utf-8")


@override_settings(GOOGLE_FORMS_WEBHOOK_TOKEN="test-sync-secret")
class GoogleFormSyncTests(TestCase):
    def setUp(self):
        self.url = reverse("google-form-webhook")
        self.payload = {
            "response_id": "sheet-123:2",
            "submitted_at": "2026-09-27T10:30:00Z",
            "responses": {
                "Full Name": "Asha Student",
                "Phone Number": "9876543210",
            },
        }

    def post_response(self, payload=None, token="test-sync-secret"):
        return self.client.post(
            self.url,
            data=json.dumps(payload if payload is not None else self.payload),
            content_type="application/json",
            HTTP_X_WEBHOOK_TOKEN=token,
        )

    def test_webhook_requires_shared_token(self):
        response = self.post_response(token="wrong-token")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(GoogleFormSubmission.objects.count(), 0)

    def test_webhook_import_is_idempotent(self):
        first = self.post_response()
        changed_payload = {
            **self.payload,
            "responses": {"Full Name": "Asha Student Updated"},
        }
        second = self.post_response(changed_payload)

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(GoogleFormSubmission.objects.count(), 1)
        self.assertEqual(
            GoogleFormSubmission.objects.get().responses["Full Name"],
            "Asha Student Updated",
        )

    def test_response_page_requires_staff_and_searches_response_fields(self):
        self.post_response()
        page_url = reverse("google-form-responses")
        self.assertEqual(self.client.get(page_url).status_code, 302)

        staff = get_user_model().objects.create_user(
            username="form-staff", password="test-password", is_staff=True
        )
        self.client.force_login(staff)
        response = self.client.get(page_url, {"q": "9876543210"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Asha Student")
        self.assertContains(response, "9876543210")
