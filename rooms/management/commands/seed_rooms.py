from django.core.management.base import BaseCommand
from rooms.models import Room
from core.models import Testimonial, FAQ, NearbyAttraction
from datetime import date


class Command(BaseCommand):
    help = 'Seed the database with rooms, testimonials, FAQs, and nearby attractions'

    def handle(self, *args, **options):
        self._seed_rooms()
        self._seed_testimonials()
        self._seed_faqs()
        self._seed_attractions()

    def _seed_rooms(self):
        rooms_data = [
            {
                'name': 'Standard Single Room',
                'slug': 'standard-single-room',
                'room_type': 'standard',
                'description': 'A clean and comfortable standard room in our F-6/2 Islamabad guest house. Features a single bed, en-suite bathroom, air conditioning, and high-speed Wi-Fi. Perfect for solo business travelers visiting the capital.',
                'price_per_night': 5500.00,
                'capacity': 1,
                'amenities': 'Wi-Fi, Air Conditioning, LED TV, Geyser, Attached Bathroom, Room Service, Daily Housekeeping',
                'featured': False,
                'bed_type': 'Single',
                'room_size': '15 sqm',
            },
            {
                'name': 'Standard Double Room',
                'slug': 'standard-double-room',
                'room_type': 'standard',
                'description': 'A well-furnished standard double room at Blue Moon Residency, F-6/2 Islamabad. Equipped with a comfortable double bed, private bathroom with hot water, air conditioning, and a work desk. Ideal for couples or business travelers.',
                'price_per_night': 7000.00,
                'capacity': 2,
                'amenities': 'Wi-Fi, Air Conditioning, LED TV, Geyser, Attached Bathroom, Room Service, Daily Housekeeping, Work Desk',
                'featured': True,
                'bed_type': 'Double',
                'room_size': '20 sqm',
            },
            {
                'name': 'Deluxe Room',
                'slug': 'deluxe-room',
                'room_type': 'deluxe',
                'description': 'Spacious deluxe room with premium furnishings at our Islamabad guest house. Features a king-size bed, sitting area, large LED TV, mini fridge, and a modern bathroom. Enjoy extra space and comfort during your stay in F-6/2.',
                'price_per_night': 10000.00,
                'capacity': 2,
                'amenities': 'Wi-Fi, Air Conditioning, 42" LED TV, Mini Fridge, Geyser, Attached Bathroom, Room Service, Daily Housekeeping, Iron, Bathrobes, Sitting Area',
                'featured': True,
                'bed_type': 'King',
                'room_size': '28 sqm',
            },
            {
                'name': 'Deluxe Twin Room',
                'slug': 'deluxe-twin-room',
                'room_type': 'deluxe',
                'description': 'A beautifully appointed deluxe room with two single beds at Blue Moon Residency. Ideal for friends, colleagues, or siblings traveling together to Islamabad. All premium amenities included.',
                'price_per_night': 9000.00,
                'capacity': 2,
                'amenities': 'Wi-Fi, Air Conditioning, 42" LED TV, Mini Fridge, Geyser, Attached Bathroom, Room Service, Daily Housekeeping, Work Desk',
                'featured': False,
                'bed_type': 'Twin',
                'room_size': '25 sqm',
            },
            {
                'name': 'Executive Suite',
                'slug': 'executive-suite',
                'room_type': 'suite',
                'description': 'Our premium suite with separate living and sleeping areas at Blue Moon Residency, F-6/2 Islamabad. Features a king-size bed, luxury bathroom, dining area, and premium furnishings. The finest accommodation experience in the F-6 sector.',
                'price_per_night': 18000.00,
                'capacity': 2,
                'amenities': 'Wi-Fi, Air Conditioning, 55" Smart TV, Mini Bar, Safe, Luxury Bathroom, Room Service, Daily Housekeeping, Iron, Bathrobes, Dining Area, Sitting Lounge',
                'featured': True,
                'bed_type': 'King',
                'room_size': '45 sqm',
            },
            {
                'name': 'Family Room',
                'slug': 'family-room',
                'room_type': 'family',
                'description': 'A spacious family room at our Islamabad guest house designed for families visiting the capital. Features one double bed and two single beds, large bathroom, and extra storage. Located in the safe and family-friendly F-6/2 neighborhood.',
                'price_per_night': 14000.00,
                'capacity': 4,
                'amenities': 'Wi-Fi, Air Conditioning, LED TV, Mini Fridge, Geyser, Attached Bathroom, Room Service, Daily Housekeeping, Extra Storage, Iron',
                'featured': True,
                'bed_type': 'Double + 2 Singles',
                'room_size': '35 sqm',
            },
            {
                'name': 'Family Suite',
                'slug': 'family-suite',
                'room_type': 'family',
                'description': 'Our largest accommodation at Blue Moon Residency with two connected rooms, a living area, and a kitchenette. Perfect for extended family stays in Islamabad. Accommodates up to 6 guests comfortably in the heart of F-6/2.',
                'price_per_night': 25000.00,
                'capacity': 6,
                'amenities': 'Wi-Fi, Air Conditioning, Smart TV, Kitchenette, Mini Fridge, Safe, Room Service, Daily Housekeeping, Washing Machine Access, Dining Table, Sitting Lounge',
                'featured': False,
                'bed_type': 'King + 2 Singles + Sofa Bed',
                'room_size': '55 sqm',
            },
        ]

        created = 0
        for data in rooms_data:
            _, was_created = Room.objects.update_or_create(
                slug=data['slug'],
                defaults=data,
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Rooms: {created} created, {len(rooms_data) - created} updated'))

    def _seed_testimonials(self):
        testimonials_data = [
            {
                'name': 'Ahmed Raza',
                'location': 'Lahore, Pakistan',
                'rating': 5,
                'text': 'Excellent guest house in F-6 Islamabad! The room was spotless, Wi-Fi was fast, and the staff was very helpful. I stay here every time I visit Islamabad for business. Highly recommended for anyone looking for quality accommodation.',
                'date': date(2025, 12, 15),
                'room_type': 'Deluxe Room',
            },
            {
                'name': 'Sarah Khan',
                'location': 'Karachi, Pakistan',
                'rating': 5,
                'text': 'We booked the Family Room for our Islamabad trip and it was perfect. Clean rooms, great location in F-6/2 near Super Market, and the kids loved it. The price was very reasonable compared to hotels.',
                'date': date(2025, 11, 20),
                'room_type': 'Family Room',
            },
            {
                'name': 'Dr. Usman Ali',
                'location': 'Peshawar, Pakistan',
                'rating': 4,
                'text': 'Very convenient location for my medical conference in Islamabad. The guest house is close to major hospitals and the Blue Area. Room service was prompt and the bed was comfortable. Will book again.',
                'date': date(2026, 1, 8),
                'room_type': 'Standard Double Room',
            },
            {
                'name': 'Maria Fernandez',
                'location': 'Dubai, UAE',
                'rating': 5,
                'text': 'Found Blue Moon Residency online while searching for guest houses in Islamabad. What a great find! The Executive Suite was beautiful, the staff arranged airport pickup, and the location in F-6 is perfect for sightseeing. Faisal Mosque is just 5 minutes away!',
                'date': date(2026, 1, 25),
                'room_type': 'Executive Suite',
            },
            {
                'name': 'Bilal Mahmood',
                'location': 'Multan, Pakistan',
                'rating': 5,
                'text': 'Best guest house near Faisal Mosque! I have stayed at many places in Islamabad but Blue Moon Residency stands out for its cleanliness, hospitality, and value. The location in F-6/2 is unbeatable.',
                'date': date(2025, 10, 5),
                'room_type': 'Deluxe Room',
            },
            {
                'name': 'Fatima Noor',
                'location': 'Rawalpindi, Pakistan',
                'rating': 4,
                'text': 'Booked this guest house for my parents who were visiting from the village. They felt very comfortable and safe. The rooms are well-maintained and the staff treats guests like family. Very affordable too.',
                'date': date(2025, 9, 18),
                'room_type': 'Standard Double Room',
            },
        ]

        created = 0
        for data in testimonials_data:
            _, was_created = Testimonial.objects.get_or_create(
                name=data['name'],
                date=data['date'],
                defaults=data,
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Testimonials: {created} created'))

    def _seed_faqs(self):
        faqs_data = [
            {
                'question': 'Where is Blue Moon Residency located in Islamabad?',
                'answer': 'Blue Moon Residency is located at House # 2-A, Justice Abdul Rasheed Road, F-6/2, Islamabad. We are in one of the most central sectors of Islamabad, just minutes from Faisal Mosque, F-6 Super Market, and the Margalla Hills.',
                'category': 'location',
                'order': 1,
            },
            {
                'question': 'How far is Blue Moon Residency from Islamabad International Airport?',
                'answer': 'Blue Moon Residency is approximately 30 minutes (25 km) from Islamabad International Airport via the Islamabad Expressway. We can arrange airport pickup and drop-off on request.',
                'category': 'location',
                'order': 2,
            },
            {
                'question': 'What are the room rates at Blue Moon Residency?',
                'answer': 'Our room rates start from PKR 5,500 per night for a Standard Single Room and go up to PKR 25,000 for our Family Suite. Rates may vary by season. We also offer discounted monthly rates for extended stays.',
                'category': 'booking',
                'order': 3,
            },
            {
                'question': 'Do I need to pay in advance to book a room?',
                'answer': 'No, Blue Moon Residency operates on a Pay at Check-in model. You can book online without any upfront payment and settle the bill at the front desk during check-in.',
                'category': 'booking',
                'order': 4,
            },
            {
                'question': 'What amenities are included in the room?',
                'answer': 'All rooms include high-speed Wi-Fi, air conditioning, LED TV, hot water (geyser), attached bathroom, daily housekeeping, and room service. Deluxe and Suite rooms additionally include a mini fridge, bathrobes, and a sitting area.',
                'category': 'rooms',
                'order': 5,
            },
            {
                'question': 'What are the check-in and check-out times?',
                'answer': 'Check-in time is 2:00 PM and check-out time is 12:00 PM (noon). Early check-in and late check-out can be arranged based on availability by contacting us in advance.',
                'category': 'policies',
                'order': 6,
            },
            {
                'question': 'Is parking available at the guest house?',
                'answer': 'Yes, Blue Moon Residency offers secure parking for guests at no additional charge. Our premises are monitored and our neighborhood in F-6/2 is one of the safest areas in Islamabad.',
                'category': 'general',
                'order': 7,
            },
            {
                'question': 'Is the guest house suitable for families with children?',
                'answer': 'Absolutely! We have dedicated Family Rooms and Family Suites that are ideal for families. F-6/2 is a quiet, residential neighborhood with parks nearby. We can also arrange extra bedding for children on request.',
                'category': 'rooms',
                'order': 8,
            },
            {
                'question': 'Do you offer monthly or long-term stay rates?',
                'answer': 'Yes, we offer special discounted rates for guests staying a week or longer. Please contact us directly for a customized quote for extended stays in Islamabad.',
                'category': 'booking',
                'order': 9,
            },
            {
                'question': 'What landmarks are near Blue Moon Residency?',
                'answer': 'We are close to Faisal Mosque (5 min), Margalla Hills Trail 3 (10 min), F-6 Super Market (3 min walk), Centaurus Mall (8 min), PIMS Hospital (12 min), Diplomatic Enclave (10 min), and Serena Hotel (7 min).',
                'category': 'location',
                'order': 10,
            },
        ]

        created = 0
        for data in faqs_data:
            _, was_created = FAQ.objects.get_or_create(
                question=data['question'],
                defaults=data,
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'FAQs: {created} created'))

    def _seed_attractions(self):
        attractions_data = [
            {'name': 'F-6 Super Market (Markaz)', 'category': 'shopping', 'distance': '3 min walk', 'description': 'The nearest commercial area with restaurants, banks, pharmacies, and grocery stores. A daily convenience hub for guests.', 'order': 1},
            {'name': 'Faisal Mosque', 'category': 'landmark', 'distance': '5 min drive', 'description': 'The iconic national mosque of Pakistan and one of the largest in the world. A must-visit landmark for every traveler to Islamabad.', 'order': 2},
            {'name': 'Margalla Hills National Park', 'category': 'landmark', 'distance': '10 min drive', 'description': 'Beautiful hiking trails (Trail 3 and Trail 5 are closest) with panoramic views of Islamabad. Popular for morning walks and nature lovers.', 'order': 3},
            {'name': 'Centaurus Mall', 'category': 'shopping', 'distance': '8 min drive', 'description': 'Islamabad\'s premier shopping mall with international brands, food court, cinema, and entertainment options.', 'order': 4},
            {'name': 'Serena Hotel Islamabad', 'category': 'landmark', 'distance': '7 min drive', 'description': 'A five-star luxury hotel and conference venue. Close proximity for guests attending events at Serena.', 'order': 5},
            {'name': 'Pakistan Institute of Medical Sciences (PIMS)', 'category': 'hospital', 'distance': '12 min drive', 'description': 'The largest public hospital in Islamabad. Our guest house is a convenient base for medical visitors and patient attendants.', 'order': 6},
            {'name': 'Shifa International Hospital', 'category': 'hospital', 'distance': '15 min drive', 'description': 'Leading private hospital in Islamabad with international accreditation. Many medical tourists stay at our guest house.', 'order': 7},
            {'name': 'Diplomatic Enclave', 'category': 'government', 'distance': '10 min drive', 'description': 'Houses foreign embassies and high commissions. Convenient for guests with visa or diplomatic appointments.', 'order': 8},
            {'name': 'Blue Area (Jinnah Avenue)', 'category': 'shopping', 'distance': '10 min drive', 'description': 'Islamabad\'s central business district with corporate offices, banks, and restaurants.', 'order': 9},
            {'name': 'Islamabad International Airport', 'category': 'transport', 'distance': '30 min drive', 'description': 'The new Islamabad airport. We offer airport pickup and drop-off service on request.', 'order': 10},
            {'name': 'Daman-e-Koh Viewpoint', 'category': 'landmark', 'distance': '15 min drive', 'description': 'A hilltop garden and viewpoint in the Margalla Hills offering breathtaking views of Islamabad. A popular tourist spot.', 'order': 11},
            {'name': 'Pakistan Monument', 'category': 'landmark', 'distance': '12 min drive', 'description': 'National monument representing the four provinces and three territories of Pakistan. Features a museum inside.', 'order': 12},
        ]

        created = 0
        for data in attractions_data:
            _, was_created = NearbyAttraction.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Nearby Attractions: {created} created'))
