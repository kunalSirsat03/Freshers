from django.contrib import admin
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


@admin.register(EventSettings)
class EventSettingsAdmin(admin.ModelAdmin):
    list_display = ("title", "organizer_name", "event_date", "event_end_time", "venue", "ticket_price")
    fieldsets = (
        ("Event", {"fields": ("title", "organizer_name", "event_date", "event_end_time", "venue", "description", "ticket_price", "capacity")}),
        ("Registration", {"fields": ("registration_url", "upi_id")}),
        ("Images", {"fields": ("hero_image", "poster_image")}),
        ("Contact and social", {"fields": ("contact_phone", "contact_email", "instagram_url", "social_url")}),
    )

    def has_add_permission(self, request):
        return not EventSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("caption", "featured", "sort_order", "is_published")
    list_editable = ("featured", "sort_order", "is_published")
    list_filter = ("featured", "is_published")
    search_fields = ("caption", "alt_text")


@admin.register(EventVideo)
class EventVideoAdmin(admin.ModelAdmin):
    list_display = ("title", "source_type", "sort_order", "is_published")
    list_editable = ("sort_order", "is_published")
    list_filter = ("source_type", "is_published")
    search_fields = ("title",)


@admin.register(ScheduleItem)
class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ("start_time", "title", "sort_order", "is_published")
    list_editable = ("sort_order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "description")


@admin.register(EventRule)
class EventRuleAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_published")
    list_editable = ("sort_order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "description")


@admin.register(EventFAQ)
class EventFAQAdmin(admin.ModelAdmin):
    list_display = ("question", "sort_order", "is_published")
    list_editable = ("sort_order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("question", "answer")


@admin.register(EventContact)
class EventContactAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "phone", "email", "sort_order", "is_published")
    list_editable = ("sort_order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("name", "role", "phone", "email")


@admin.register(GoogleFormSubmission)
class GoogleFormSubmissionAdmin(admin.ModelAdmin):
    list_display = ("external_id", "submitted_at", "received_at")
    search_fields = ("external_id",)
    readonly_fields = ("external_id", "submitted_at", "responses", "received_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("registration_id", "ticket_quantity", "total_amount", "payment_state", "created_at")
    list_filter = ("payment__status", "created_at")
    search_fields = ("registration_id", "payment__utr_number", "participants")
    readonly_fields = ("registration_id", "qr_token", "created_at")

    def has_add_permission(self, request):
        return False

    @admin.display(description="Payment status", ordering="payment__status")
    def payment_state(self, registration):
        return registration.payment.get_status_display()


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("registration", "utr_number", "amount", "status", "verified_by", "verified_at")
    list_filter = ("status", "created_at")
    search_fields = ("registration__registration_id", "utr_number")
    readonly_fields = ("registration", "utr_number", "amount", "status", "verified_by", "verified_at", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("attendee_name", "registration", "email", "checked_in_at", "checked_in_by")
    list_filter = ("checked_in_at", "created_at")
    search_fields = ("attendee_name", "email", "phone", "registration__registration_id")
    readonly_fields = ("registration", "qr_token", "created_at", "checked_in_at", "checked_in_by")