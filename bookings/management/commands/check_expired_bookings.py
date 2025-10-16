# bookings/management/commands/check_expired_bookings.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from bookings.models import Booking
from datetime import timedelta


class Command(BaseCommand):
    help = 'Verifica y marca reservas como expiradas si no se confirmaron'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=3,
            help='Días después de los cuales una reserva pendiente se considera expirada',
        )
    
    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Buscar reservas pendientes antiguas
        expired_bookings = Booking.objects.filter(
            payment_status='PENDING',
            booking_date__lt=cutoff_date
        )
        
        count = expired_bookings.count()
        
        if count > 0:
            # Marcar como canceladas
            expired_bookings.update(payment_status='CANCELLED')
            
            self.stdout.write(
                self.style.WARNING(f'⚠ {count} reservas pendientes marcadas como canceladas')
            )
            
            # Listar las reservas canceladas
            for booking in expired_bookings:
                self.stdout.write(
                    f'  - {booking.invoice_id} (Usuario: {booking.user.username})'
                )
        else:
            self.stdout.write(
                self.style.SUCCESS('✓ No hay reservas pendientes expiradas')
            )