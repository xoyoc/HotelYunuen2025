# bookings/utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string

def send_booking_confirmation(booking):
    subject = f'Confirmación de Reserva - {booking.invoice_id}'
    
    context = {
        'booking': booking,
        'hotel': booking.hotel,
        'user': booking.user,
    }
    
    html_message = render_to_string('emails/booking_confirmation.html', context)
    plain_message = render_to_string('emails/booking_confirmation.txt', context)
    
    send_mail(
        subject,
        plain_message,
        'noreply@hotelyunuen.com',
        [booking.user.email],
        html_message=html_message,
        fail_silently=False,
    )