from django.conf import settings
from django.shortcuts import render


SCHEDULE = [
    ("18:00", "Doors open", "Find your people, get your welcome drink, and take a photo on the red carpet."),
    ("18:30", "The opening", "A toast to the new faces and the start of a very good night."),
    ("19:15", "Freshers spotlight", "A little stage time for the people who make this night theirs."),
    ("20:30", "Dinner is served", "Settle in for the evening buffet at Bonvivant."),
    ("21:15", "Dance floor", "The lights come up and the DJ takes it from here."),
]

FAQS = [
    ("Who is the event for?", "Eligibility and attendee details are listed in the registration form. Please check those before submitting."),
    ("How do I register?", "Use any Register Now button to open the organizers' Google Form in a new tab. Follow the payment and UTR instructions there."),
    ("Where do I find payment instructions?", "Payment details and the UTR submission process are provided through the registration form and its linked organizer workflow. This website does not collect payment or attendee data."),
    ("What should I wear?", "The suggested dress code is western formal or party wear. Choose something comfortable enough to enjoy the whole evening."),
    ("Who can help with a registration question?", "Use the organizer contact details provided in the Google Form."),
]


def home(request):
    return render(
        request,
        "events/home.html",
        {
            "event_date": "10 October 2026",
            "event_time": "6:00 PM onwards",
            "venue": "Bonvivant",
            "ticket_price": 750,
            "schedule": SCHEDULE,
            "faqs": FAQS,
            "has_registration": bool(settings.GOOGLE_FORM_URL),
        },
    )