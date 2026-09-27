import uuid
from urllib.parse import parse_qs, urlparse

from django.db import models
from django.conf import settings as django_settings


class EventSettings(models.Model):
    title = models.CharField(max_length=120, default="Unofficial Freshers '26")
    organizer_name = models.CharField(max_length=120, default="Department of Engineering")
    event_date = models.DateTimeField(default="2026-10-10T11:00:00+05:30")
    event_end_time = models.TimeField(default="18:00", verbose_name="Event end time")
    venue = models.CharField(max_length=180, default="Bonvivant Banquet Hall, City Center")
    ticket_price = models.PositiveIntegerField(default=750)
    capacity = models.PositiveIntegerField(default=120)
    upi_id = models.CharField(max_length=120, default="engineering.freshers@upi")
    description = models.TextField(
        blank=True,
        default="Meet your people, take the stage, and celebrate the start of something unforgettable.",
    )
    registration_url = models.URLField(blank=True)
    hero_image = models.ImageField(upload_to="events/", blank=True)
    poster_image = models.ImageField(upload_to="events/", blank=True)
    contact_phone = models.CharField(max_length=40, blank=True)
    contact_email = models.EmailField(blank=True)
    instagram_url = models.URLField(blank=True)
    social_url = models.URLField(blank=True)

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    COLLECTION_GENERAL = "GENERAL"
    COLLECTION_PREVIOUS = "PREVIOUS"
    COLLECTION_VENUE = "VENUE"
    COLLECTION_CHOICES = [
        (COLLECTION_GENERAL, "General gallery"),
        (COLLECTION_PREVIOUS, "Last year's party"),
        (COLLECTION_VENUE, "This year's venue"),
    ]

    image = models.ImageField(upload_to="gallery/", blank=True)
    image_url = models.URLField(blank=True)
    caption = models.CharField(max_length=180, blank=True)
    alt_text = models.CharField(max_length=180, blank=True)
    collection = models.CharField(
        max_length=12, choices=COLLECTION_CHOICES, default=COLLECTION_GENERAL
    )
    sort_order = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "pk"]
        verbose_name = "gallery image"
        verbose_name_plural = "gallery images"

    def __str__(self):
        return self.caption or f"Gallery image {self.pk}"

    @property
    def display_url(self):
        return self.image.url if self.image else self.image_url


class EventVideo(models.Model):
    SOURCE_YOUTUBE = "YOUTUBE"
    SOURCE_UPLOAD = "UPLOAD"
    SOURCE_CHOICES = [
        (SOURCE_YOUTUBE, "External video URL (YouTube / Reel)"),
        (SOURCE_UPLOAD, "Uploaded video"),
    ]
    EDITION_PREVIOUS = "PREVIOUS"
    EDITION_CURRENT = "CURRENT"
    EDITION_PROMO = "PROMO"
    EDITION_CHOICES = [
        (EDITION_PREVIOUS, "Last year's party"),
        (EDITION_CURRENT, "This year's party"),
        (EDITION_PROMO, "Promo / teaser"),
    ]

    title = models.CharField(max_length=160)
    source_type = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=SOURCE_YOUTUBE)
    edition = models.CharField(
        max_length=8, choices=EDITION_CHOICES, default=EDITION_PROMO
    )
    url = models.URLField(blank=True)
    video_file = models.FileField(upload_to="videos/", blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "pk"]

    def __str__(self):
        return self.title

    @property
    def embed_url(self):
        parsed = urlparse(self.url)
        host = parsed.netloc.lower().split(":", 1)[0]
        if host in {"youtu.be", "www.youtu.be"}:
            video_id = parsed.path.strip("/").split("/")[0]
        elif host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
            video_id = parse_qs(parsed.query).get("v", [""])[0]
            if not video_id and parsed.path.startswith(("/embed/", "/shorts/")):
                video_id = parsed.path.split("/")[2]
        else:
            return ""
        if len(video_id) != 11 or not all(char.isalnum() or char in "-_" for char in video_id):
            return ""
        return f"https://www.youtube-nocookie.com/embed/{video_id}"


class ScheduleItem(models.Model):
    start_time = models.TimeField()
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "start_time", "pk"]

    def __str__(self):
        return f"{self.start_time:%I:%M %p} · {self.title}"


class EventRule(models.Model):
    title = models.CharField(max_length=140)
    description = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "pk"]
        verbose_name = "rule"

    def __str__(self):
        return self.title


class EventFAQ(models.Model):
    question = models.CharField(max_length=240)
    answer = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "pk"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class EventContact(models.Model):
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    social_url = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "pk"]

    def __str__(self):
        return self.name


class GoogleFormSubmission(models.Model):
    external_id = models.CharField(max_length=200, unique=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    responses = models.JSONField(default=dict)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at", "-received_at"]
        verbose_name = "Google Form response"
        verbose_name_plural = "Google Form responses"

    def __str__(self):
        return f"Form response {self.external_id}"


class Registration(models.Model):
    registration_id = models.CharField(max_length=20, unique=True, editable=False)
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    participants = models.JSONField(default=list)
    ticket_quantity = models.PositiveSmallIntegerField()
    total_amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.registration_id:
            self.registration_id = f"UF2026-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    @property
    def payment_status(self):
        return self.payment.status if hasattr(self, "payment") else Payment.STATUS_PENDING

    def __str__(self):
        return self.registration_id


class Payment(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_VERIFIED = "VERIFIED"
    STATUS_REJECTED = "REJECTED"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending verification"),
        (STATUS_VERIFIED, "Verified"),
        (STATUS_REJECTED, "Rejected"),
    ]

    registration = models.OneToOneField(
        Registration, on_delete=models.CASCADE, related_name="payment"
    )
    utr_number = models.CharField(max_length=40, unique=True)
    amount = models.PositiveIntegerField()
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True
    )
    verified_by = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_freshers_payments",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.registration.registration_id}: {self.get_status_display()}"


class Ticket(models.Model):
    registration = models.ForeignKey(
        Registration, on_delete=models.CASCADE, related_name="tickets"
    )
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    attendee_name = models.CharField(max_length=100)
    department = models.CharField(max_length=80)
    year = models.CharField(max_length=40)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=254)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checked_in_freshers_tickets",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["registration", "checked_in_at"])]

    def __str__(self):
        return f"{self.registration.registration_id} · {self.attendee_name}"