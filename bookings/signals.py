# bookings/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Booking, Coupon


@receiver(pre_save, sender=Booking)
def update_coupon_usage(sender, instance, **kwargs):
    """Incrementa el uso del cupón cuando una reserva es pagada"""
    if instance.pk:  # Si ya existe
        try:
            old_instance = Booking.objects.get(pk=instance.pk)
            # Si cambió de pendiente a pagado/confirmado
            if (old_instance.payment_status not in ['PAID', 'CONFIRMED'] and 
                instance.payment_status in ['PAID', 'CONFIRMED'] and
                instance.coupon):
                instance.coupon.times_used += 1
                instance.coupon.save(update_fields=['times_used'])
        except Booking.DoesNotExist:
            pass


@receiver(post_save, sender=Booking)
def update_room_status(sender, instance, created, **kwargs):
    """Actualiza el estado de la habitación según la reserva"""
    from django.utils import timezone
    
    today = timezone.now().date()
    
    # Si la reserva está activa (check-in <= hoy <= check-out)
    if (instance.check_in_date <= today <= instance.check_out_date and 
        instance.payment_status in ['PAID', 'CONFIRMED']):
        instance.room.status = 'OCCUPIED'
        instance.room.is_available = False
        instance.room.save(update_fields=['status', 'is_available'])
    
    # Si la reserva fue cancelada, liberar la habitación
    elif instance.payment_status == 'CANCELLED':
        # Verificar si no hay otras reservas activas para esta habitación
        active_bookings = Booking.objects.filter(
            room=instance.room,
            check_in_date__lte=today,
            check_out_date__gte=today,
            payment_status__in=['PAID', 'CONFIRMED']
        ).exclude(pk=instance.pk)
        
        if not active_bookings.exists():
            instance.room.status = 'AVAILABLE'
            instance.room.is_available = True
            instance.room.save(update_fields=['status', 'is_available'])


@receiver(post_save, sender=Booking)
def update_booking_statistics(sender, instance, created, **kwargs):
    """Actualiza las estadísticas del hotel cuando hay una nueva reserva"""
    if hasattr(instance.hotel, 'statistics'):
        instance.hotel.statistics.update_statistics()