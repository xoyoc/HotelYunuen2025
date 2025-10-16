# bookings/management/commands/generate_test_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from rooms.models import Amenity, RoomType, Room
from bookings.models import Hotel, Booking
from reviews.models import ReviewAndRating
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Genera datos de prueba para el sistema'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina todos los datos antes de generar nuevos',
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Eliminando datos existentes...')
            ReviewAndRating.objects.all().delete()
            Booking.objects.all().delete()
            Room.objects.all().delete()
            RoomType.objects.all().delete()
            Amenity.objects.all().delete()
            Hotel.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Datos eliminados'))
        
        # Crear hotel
        self.stdout.write('Creando hotel...')
        hotel, created = Hotel.objects.get_or_create(
            slug='hotel-yunuen',
            defaults={
                'name': 'Hotel Yunuen',
                'address': 'Av. Principal 123',
                'city': 'Pátzcuaro',
                'state': 'Michoacán',
                'postal_code': '61600',
                'phone': '+52 434 342 0000',
                'email': 'info@hotelyunuen.com',
                'description': 'Hotel boutique en el corazón de Pátzcuaro'
            }
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Hotel: {hotel.name}'))
        
        # Crear comodidades
        self.stdout.write('Creando comodidades...')
        amenities_data = [
            {'name': 'WiFi Gratuito', 'icon': 'fa-wifi'},
            {'name': 'Aire Acondicionado', 'icon': 'fa-snowflake'},
            {'name': 'TV por Cable', 'icon': 'fa-tv'},
            {'name': 'Minibar', 'icon': 'fa-wine-bottle'},
            {'name': 'Caja Fuerte', 'icon': 'fa-lock'},
            {'name': 'Vista al Lago', 'icon': 'fa-water'},
            {'name': 'Estacionamiento', 'icon': 'fa-parking'},
            {'name': 'Servicio a Habitación', 'icon': 'fa-concierge-bell'},
        ]
        
        amenities = []
        for amenity_data in amenities_data:
            amenity, created = Amenity.objects.get_or_create(
                name=amenity_data['name'],
                defaults={'icon': amenity_data['icon']}
            )
            amenities.append(amenity)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(amenities)} comodidades creadas'))
        
        # Crear tipos de habitación
        self.stdout.write('Creando tipos de habitación...')
        room_types_data = [
            {
                'name': 'Habitación Básica',
                'category': 'BASIC',
                'price_per_night': 800.00,
                'number_of_beds': 1,
                'room_capacity': 2,
                'total_rooms': 10,
                'size_sqm': 20.00,
                'description': 'Habitación acogedora con todas las comodidades básicas'
            },
            {
                'name': 'Habitación Estándar',
                'category': 'STANDARD',
                'price_per_night': 1200.00,
                'number_of_beds': 2,
                'room_capacity': 3,
                'total_rooms': 15,
                'size_sqm': 30.00,
                'description': 'Habitación espaciosa con vista parcial al lago'
            },
            {
                'name': 'Habitación Premium',
                'category': 'PREMIUM',
                'price_per_night': 1800.00,
                'number_of_beds': 2,
                'room_capacity': 4,
                'total_rooms': 8,
                'size_sqm': 40.00,
                'description': 'Habitación de lujo con vista completa al lago y balcón'
            },
            {
                'name': 'Suite Ejecutiva',
                'category': 'SUITE',
                'price_per_night': 2500.00,
                'number_of_beds': 2,
                'room_capacity': 4,
                'total_rooms': 5,
                'size_sqm': 60.00,
                'description': 'Suite amplia con sala de estar separada y jacuzzi'
            },
        ]
        
        for rt_data in room_types_data:
            room_type, created = RoomType.objects.get_or_create(
                name=rt_data['name'],
                defaults={
                    'category': rt_data['category'],
                    'price_per_night': rt_data['price_per_night'],
                    'number_of_beds': rt_data['number_of_beds'],
                    'room_capacity': rt_data['room_capacity'],
                    'total_rooms': rt_data['total_rooms'],
                    'size_sqm': rt_data['size_sqm'],
                    'description': rt_data['description']
                }
            )
            
            # Agregar comodidades aleatorias
            if created:
                selected_amenities = random.sample(amenities, random.randint(4, 8))
                room_type.amenities.set(selected_amenities)
            
            # Crear habitaciones individuales
            for i in range(1, rt_data['total_rooms'] + 1):
                floor = (i - 1) // 10 + 1
                room_number = f"{floor}{i:02d}"
                
                Room.objects.get_or_create(
                    room_number=room_number,
                    defaults={
                        'room_type': room_type,
                        'floor': floor,
                        'status': 'AVAILABLE',
                        'is_available': True
                    }
                )
        
        self.stdout.write(self.style.SUCCESS(f'✓ {RoomType.objects.count()} tipos de habitación creados'))
        self.stdout.write(self.style.SUCCESS(f'✓ {Room.objects.count()} habitaciones creadas'))
        
        # Crear usuarios de prueba
        self.stdout.write('Creando usuarios de prueba...')
        users_data = [
            {'username': 'juan.perez', 'email': 'juan@example.com', 'first_name': 'Juan', 'last_name': 'Pérez'},
            {'username': 'maria.garcia', 'email': 'maria@example.com', 'first_name': 'María', 'last_name': 'García'},
            {'username': 'carlos.lopez', 'email': 'carlos@example.com', 'first_name': 'Carlos', 'last_name': 'López'},
            {'username': 'ana.martinez', 'email': 'ana@example.com', 'first_name': 'Ana', 'last_name': 'Martínez'},
            {'username': 'luis.rodriguez', 'email': 'luis@example.com', 'first_name': 'Luis', 'last_name': 'Rodríguez'},
        ]
        
        test_users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name']
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            test_users.append(user)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(test_users)} usuarios creados'))
        
        # Crear reservaciones de prueba
        self.stdout.write('Creando reservaciones de prueba...')
        rooms = list(Room.objects.all())
        today = timezone.now().date()
        
        for i in range(20):
            user = random.choice(test_users)
            room = random.choice(rooms)
            
            # Crear fechas aleatorias
            days_offset = random.randint(-30, 60)
            check_in = today + timedelta(days=days_offset)
            nights = random.randint(1, 7)
            check_out = check_in + timedelta(days=nights)
            
            # Determinar estado según las fechas
            if check_in > today:
                status = random.choice(['PENDING', 'PAID', 'CONFIRMED'])
            elif check_in <= today <= check_out:
                status = random.choice(['PAID', 'CONFIRMED'])
            else:
                status = random.choice(['CONFIRMED', 'CANCELLED'])
            
            booking = Booking.objects.create(
                user=user,
                hotel=hotel,
                room=room,
                check_in_date=check_in,
                check_out_date=check_out,
                adults=random.randint(1, 3),
                children=random.randint(0, 2),
                payment_status=status,
                subtotal=0,  # Se calculará automáticamente en save()
                total_price=0
            )
        
        self.stdout.write(self.style.SUCCESS(f'✓ {Booking.objects.count()} reservaciones creadas'))
        
        # Crear reseñas de prueba
        self.stdout.write('Creando reseñas de prueba...')
        completed_bookings = Booking.objects.filter(
            payment_status__in=['CONFIRMED', 'PAID'],
            check_out_date__lt=today
        )
        
        reviews_texts = [
            "Excelente hotel, muy buena atención y habitaciones limpias.",
            "La ubicación es perfecta y el desayuno delicioso.",
            "Muy recomendable, volveré sin duda.",
            "Buena relación calidad-precio, aunque el WiFi podría mejorar.",
            "Personal muy amable y atento a todas nuestras necesidades.",
            "Habitaciones cómodas con hermosa vista al lago.",
            "Una experiencia maravillosa, todo estuvo perfecto.",
            "Buen hotel pero el estacionamiento es limitado.",
            "Ideal para una escapada romántica, muy tranquilo.",
            "Las instalaciones están muy bien cuidadas.",
        ]
        
        for booking in completed_bookings[:15]:
            ReviewAndRating.objects.create(
                user=booking.user,
                hotel=hotel,
                booking=booking,
                rating=random.randint(3, 5),
                cleanliness_rating=random.randint(3, 5),
                service_rating=random.randint(3, 5),
                location_rating=random.randint(3, 5),
                value_rating=random.randint(3, 5),
                title=f"Estancia en {booking.check_in_date.strftime('%B %Y')}",
                review_text=random.choice(reviews_texts),
                would_recommend=random.choice([True, True, True, False]),
                is_active=True,
                is_verified=True
            )
        
        self.stdout.write(self.style.SUCCESS(f'✓ {ReviewAndRating.objects.count()} reseñas creadas'))
        
        # Actualizar estadísticas
        self.stdout.write('Actualizando estadísticas...')
        from reviews.models import HotelStatistics
        stats, created = HotelStatistics.objects.get_or_create(hotel=hotel)
        stats.update_statistics()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Datos de prueba generados exitosamente!'))
        self.stdout.write(self.style.SUCCESS(f'   Hotel: {hotel.name}'))
        self.stdout.write(self.style.SUCCESS(f'   Habitaciones: {Room.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   Reservaciones: {Booking.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   Reseñas: {ReviewAndRating.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'   Calificación promedio: {stats.average_rating}★'))