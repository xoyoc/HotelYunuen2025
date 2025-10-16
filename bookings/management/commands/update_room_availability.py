# bookings/management/commands/update_room_availability.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from bookings.models import Booking
from rooms.models import Room


class Command(BaseCommand):
    help = 'Actualiza la disponibilidad de habitaciones según las reservas activas'
    
    def handle(self, *args, **options):
        today = timezone.now().date()
        updated_count = 0
        
        # Obtener todas las habitaciones
        rooms = Room.objects.all()
        
        for room in rooms:
            # Verificar si tiene reservas activas
            active_bookings = Booking.objects.filter(
                room=room,
                check_in_date__lte=today,
                check_out_date__gte=today,
                payment_status__in=['PAID', 'CONFIRMED']
            )
            
            if active_bookings.exists():
                if room.status != 'OCCUPIED':
                    room.status = 'OCCUPIED'
                    room.is_available = False
                    room.save(update_fields=['status', 'is_available'])
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Habitación {room.room_number} marcada como OCUPADA')
                    )
            else:
                # Verificar si tiene reservas futuras
                future_bookings = Booking.objects.filter(
                    room=room,
                    check_in_date__gt=today,
                    payment_status__in=['PAID', 'CONFIRMED']
                )
                
                if not future_bookings.exists() and room.status == 'OCCUPIED':
                    room.status = 'AVAILABLE'
                    room.is_available = True
                    room.save(update_fields=['status', 'is_available'])
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Habitación {room.room_number} marcada como DISPONIBLE')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ {updated_count} habitaciones actualizadas')
        )