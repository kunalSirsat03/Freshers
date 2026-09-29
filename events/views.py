from django.conf import settings
from django.shortcuts import render


SCHEDULE = [
    ("11:00 - 11:30 AM", "Entry & Welcome", "Guest check-in, pass verification and seating."),
    ("11:30 - 11:45 AM", "Opening & Introduction", "Welcome address, event introduction and committee introduction."),
    ("11:45 AM - 1:15 PM", "Live Performances", "Dance performances, comedy acts, music and other stage acts."),
    ("1:15 - 2:00 PM", "Games & Interactive Activities", "Fun games, audience interaction and challenges."),
    ("2:00 - 2:45 PM", "Lunch Break", "Lunch served for all attendees at The Cleio (Ekaa Rooftop)."),
    ("2:45 - 5:15 PM", "OPEN DANCE FLOOR", "DJ, music, dancing and free interaction."),
    ("5:15 - 5:30 PM", "Closing & Thank You", "Final announcements, acknowledgements and event wrap-up."),
]

FAQS = [
    ("Who is the event for?", "Eligibility and attendee details are listed in the registration form. Please check those before submitting."),
    ("How do I register?", "Use any Register Now button to open the organizers' Google Form in a new tab. Follow the payment and UTR instructions there, then return to this page for the registration follow-up."),
    ("Where do I find payment instructions?", "Payment details and the UTR submission process are provided through the registration form and its linked organizer workflow. This website does not collect payment or attendee data."),
    ("What should I wear?", "The suggested dress code is western formal or party wear. Choose something comfortable for the full day."),
    ("Who can help with a registration question?", "Use the organizer contact details provided in the Google Form. For website queries, email kunal3work@gmail.com."),
]


def home(request):
    return render(
        request,
        "events/home.html",
        {
            "event_date": "10 October 2026",
            "event_time": "11:00 AM - 6:00 PM",
            "venue": "The Cleio (Ekaa Rooftop), Nashik",
            "venue_map_url": "https://maps.app.goo.gl/mwoWJLKVdRmqZYJX8",
            "ticket_price": 750,
            "schedule": SCHEDULE,
            "faqs": FAQS,
            "has_registration": bool(settings.GOOGLE_FORM_URL),
        },
    )