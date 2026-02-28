from django.core.management.base import BaseCommand
from rooms.models import Room, RoomImage


ROOM_IMAGES = {
    'standard-single-room': [
        ('rooms/standard-single-1.jpg', 'Single bed with mosaic wall'),
    ],
    'standard-double-room': [
        ('rooms/standard-double-1.jpg', 'Double bed with patterned walls'),
    ],
    'deluxe-room': [
        ('rooms/deluxe-1.jpg', 'Deluxe room with padded headboard'),
        ('rooms/deluxe-2.jpg', 'TV and sitting area'),
        ('rooms/deluxe-3.jpg', 'Deluxe room interior'),
    ],
    'deluxe-twin-room': [
        ('rooms/deluxe-twin-1.jpg', 'Twin single beds'),
        ('rooms/deluxe-twin-2.jpg', 'Deluxe twin room view'),
        ('rooms/deluxe-twin-3.jpg', 'Deluxe twin room interior'),
    ],
    'family-room': [
        ('rooms/family-room-1.jpg', 'Twin double beds'),
        ('rooms/family-room-2.jpg', 'Family room sofa area'),
        ('rooms/family-room-3.jpg', 'Family room interior'),
        ('rooms/family-room-4.jpg', 'Family room view'),
    ],
    'executive-suite': [
        ('rooms/executive-suite-1.jpg', 'Luxury headboard and king bed'),
        ('rooms/executive-suite-2.jpg', 'Executive suite armchairs'),
        ('rooms/executive-suite-3.jpg', 'Executive suite living area'),
        ('rooms/executive-suite-4.jpg', 'Executive suite details'),
    ],
    'family-suite': [
        ('rooms/family-suite-1.jpg', 'Spacious family suite'),
        ('rooms/family-suite-2.jpg', 'Family suite dark decor'),
        ('rooms/family-suite-3.jpg', 'Family suite twin beds'),
        ('rooms/family-suite-4.jpg', 'Family suite interior'),
        ('rooms/family-suite-5.jpg', 'Family suite additional view'),
    ],
}

BATHROOM_IMAGES = [
    ('rooms/bathroom-1.jpg', 'Clean attached bathroom'),
    ('rooms/bathroom-2.jpg', 'Bathroom with hot water'),
]


class Command(BaseCommand):
    help = 'Load real room images into RoomImage records for all rooms'

    def handle(self, *args, **options):
        # Clear existing RoomImage records
        deleted_count, _ = RoomImage.objects.all().delete()
        if deleted_count:
            self.stdout.write(f'Deleted {deleted_count} existing RoomImage records')

        total_created = 0

        for slug, images in ROOM_IMAGES.items():
            try:
                room = Room.objects.get(slug=slug)
            except Room.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Room "{slug}" not found, skipping'))
                continue

            # Add room-specific images (first one is primary)
            for i, (path, caption) in enumerate(images):
                RoomImage.objects.create(
                    room=room,
                    image=path,
                    caption=caption,
                    is_primary=(i == 0),
                )
                total_created += 1

            # Add shared bathroom images to every room
            for path, caption in BATHROOM_IMAGES:
                RoomImage.objects.create(
                    room=room,
                    image=path,
                    caption=caption,
                    is_primary=False,
                )
                total_created += 1

            room_count = len(images) + len(BATHROOM_IMAGES)
            self.stdout.write(f'  {room.name}: {room_count} images')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created {total_created} RoomImage records for {len(ROOM_IMAGES)} rooms'
        ))
