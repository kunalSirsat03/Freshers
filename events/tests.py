from django.test import TestCase, override_settings


class HomePageTests(TestCase):
    @override_settings(GOOGLE_FORM_URL="https://forms.google.com/example")
    def test_registration_ctas_use_configured_form_without_public_counts(self):
        response = self.client.get("/")
        page = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(page.count('href="https://forms.google.com/example"'), 4)
        self.assertEqual(page.count('target="_blank" rel="noopener noreferrer"'), 4)
        self.assertNotIn("120", page)
        self.assertNotIn("localStorage", page)

    @override_settings(GOOGLE_FORM_URL="")
    def test_missing_form_url_does_not_render_a_placeholder_external_link(self):
        response = self.client.get("/")
        page = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Registration link coming soon.", page)
        self.assertNotIn("https://docs.google.com/forms", page)