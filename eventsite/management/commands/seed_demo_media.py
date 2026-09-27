from django.core.management.base import BaseCommand

from eventsite.models import EventVideo, GalleryImage


class Command(BaseCommand):
    help = "Create or refresh sample gallery images and videos."

    def handle(self, *args, **options):
        demo_images = [
            {
                "caption": "Demo image: live music crowd",
                "alt_text": "Crowd enjoying a live music performance",
                "image_url": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?auto=format&fit=crop&w=1000&q=85",
                "featured": True,
                "sort_order": 0,
            },
            {
                "caption": "Demo image: concert lights",
                "alt_text": "Concert lights across a dance floor",
                "image_url": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?auto=format&fit=crop&w=800&q=85",
                "featured": False,
                "sort_order": 1,
            },
            {
                "caption": "Demo image: celebration",
                "alt_text": "Friends celebrating together at an event",
                "image_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=85",
                "featured": False,
                "sort_order": 2,
            },
        ]
        for image in demo_images:
            GalleryImage.objects.update_or_create(
                caption=image["caption"], defaults=image
            )

        demo_videos = [
            {
                "title": "Demo video: YouTube player",
                "url": "https://www.youtube.com/watch?v=M7lc1UVf-VE",
                "sort_order": 0,
            },
            {
                "title": "Demo video: Blender Foundation short film",
                "url": "https://www.youtube.com/watch?v=aqz-KE-bpKQ",
                "sort_order": 1,
            },
        ]
        for video in demo_videos:
            EventVideo.objects.update_or_create(
                title=video["title"],
                defaults={
                    **video,
                    "source_type": EventVideo.SOURCE_YOUTUBE,
                    "is_published": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Demo gallery images and videos are ready."))