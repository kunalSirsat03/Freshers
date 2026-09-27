from django.conf import settings
from django.shortcuts import render


SCHEDULE = [
    ("11:00", "Doors open", "Meet your classmates, collect your welcome pack, and settle in."),
    ("11:30", "Welcome and introductions", "A warm welcome to the new faces joining the year."),
    ("12:30", "Freshers spotlight", "A little stage time for the people who make this day theirs."),
    ("13:30", "Lunch is served", "Take a break and enjoy lunch together at Bonvivant."),
    ("15:00", "Games and good company", "Get to know your classmates with a few easygoing activities."),
    ("16:00", "Music and dancing", "The DJ takes over for an afternoon on the dance floor."),
    ("17:30", "One last group photo", "Wrap up the day with your new friends and a keepsake photo."),
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
            "venue": "Bonvivant",
            "ticket_price": 750,
            "schedule": SCHEDULE,
            "faqs": FAQS,
            "has_registration": bool(settings.GOOGLE_FORM_URL),
        },
    )