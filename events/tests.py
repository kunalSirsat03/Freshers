from django.test import TestCase, override_settings


class HomePageTests(TestCase):
    @override_settings(GOOGLE_FORM_URL="https://forms.google.com/example", EVENT_CONTACT_EMAIL="kunal3work@gmail.com")
    def test_registration_flow_and_event_details_render(self):
        response = self.client.get("/")
        page = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(page.count('href="https://forms.google.com/example"'), 4)
        self.assertEqual(page.count('target="_blank" rel="noopener noreferrer"'), 6)
        self.assertEqual(page.count('href="https://maps.app.goo.gl/mwoWJLKVdRmqZYJX8"'), 2)
        self.assertIn("The Cleio (Ekaa Rooftop), Nashik", page)
        self.assertIn("11:00 AM - 6:00 PM", page)
        self.assertIn("Your response is on its way.", page)
        self.assertIn("organizers will verify your details and payment", page)
        self.assertIn('href="mailto:kunal3work@gmail.com"', page)
        self.assertIn("youtube-nocookie.com/embed/in6gm1NFqow", page)
        self.assertIn("youtube-nocookie.com/embed/Ay5_obp5Zgo", page)
        self.assertIn("youtube-nocookie.com/embed/1pM_pVoYIUE", page)
        self.assertNotIn("120", page)
        self.assertNotIn("localStorage", page)

    @override_settings(GOOGLE_FORM_URL="")
    def test_missing_form_url_does_not_render_a_placeholder_external_link(self):
        response = self.client.get("/")
        page = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Registration link coming soon.", page)
        self.assertNotIn("https://docs.google.com/forms", page)