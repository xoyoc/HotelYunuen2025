from django.core.management.base import BaseCommand
from reviews.models import HotelStatistics
from bookings.models import Hotel


class Command(BaseCommand):
    help = 'Actualiza las estadísticas de todos los hoteles'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--hotel-id',
            type=int,
            help='ID específico del hotel a actualizar',
        )
    
    def handle(self, *args, **options):
        hotel_id = options.get('hotel_id')
        
        if hotel_id:
            try:
                hotel = Hotel.objects.get(id=hotel_id)
                stats, created = HotelStatistics.objects.get_or_create(hotel=hotel)
                stats.update_statistics()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Estadísticas actualizadas para {hotel.name}')
                )
            except Hotel.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'✗ Hotel con ID {hotel_id} no encontrado')
                )
        else:
            hotels = Hotel.objects.all()
            for hotel in hotels:
                stats, created = HotelStatistics.objects.get_or_create(hotel=hotel)
                stats.update_statistics()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Estadísticas actualizadas para {hotel.name}')
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Total: {hotels.count()} hoteles procesados')
            )