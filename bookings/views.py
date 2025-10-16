# bookings/views.py
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Booking, Coupon
from rooms.models import Room
from datetime import datetime


class BookingListView(LoginRequiredMixin, ListView):
    """Lista las reservaciones del usuario"""
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Booking.objects.filter(
            user=self.request.user
        ).select_related(
            'hotel', 'room__room_type', 'coupon'
        ).order_by('-booking_date')
        
        # Filtrar por estado
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(payment_status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Booking.PaymentStatus.choices
        
        # Estadísticas del usuario
        all_bookings = Booking.objects.filter(user=self.request.user)
        context['total_bookings'] = all_bookings.count()
        context['upcoming_bookings'] = all_bookings.filter(
            check_in_date__gte=timezone.now().date(),
            payment_status__in=['PAID', 'CONFIRMED']
        ).count()
        
        return context


class BookingDetailView(LoginRequiredMixin, DetailView):
    """Detalle de una reservación"""
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'
    slug_field = 'booking_id'
    slug_url_kwarg = 'booking_id'
    
    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).select_related(
            'hotel', 'room__room_type', 'coupon'
        ).prefetch_related(
            'room__room_type__amenities'
        )


class BookingCreateView(LoginRequiredMixin, CreateView):
    """Crear una nueva reservación"""
    model = Booking
    template_name = 'bookings/booking_create.html'
    fields = ['hotel', 'room', 'check_in_date', 'check_out_date', 
              'adults', 'children', 'special_requests']
    
    def get_initial(self):
        initial = super().get_initial()
        
        # Pre-llenar desde parámetros GET
        room_id = self.request.GET.get('room_id')
        if room_id:
            try:
                room = Room.objects.get(id=room_id)
                initial['room'] = room
                initial['hotel'] = room.room_type.rooms.first().room_type.rooms.first() if hasattr(room, 'hotel') else None
            except Room.DoesNotExist:
                pass
        
        check_in = self.request.GET.get('check_in')
        check_out = self.request.GET.get('check_out')
        if check_in:
            initial['check_in_date'] = check_in
        if check_out:
            initial['check_out_date'] = check_out
            
        return initial
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Validar disponibilidad antes de guardar
        room = form.cleaned_data['room']
        check_in = form.cleaned_data['check_in_date']
        check_out = form.cleaned_data['check_out_date']
        
        if not room.is_available_for_dates(check_in, check_out):
            messages.error(
                self.request,
                'La habitación no está disponible para las fechas seleccionadas.'
            )
            return self.form_invalid(form)
        
        # Aplicar cupón si existe en sesión
        coupon_code = self.request.session.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                if coupon.is_valid():
                    form.instance.coupon = coupon
            except Coupon.DoesNotExist:
                pass
        
        messages.success(
            self.request,
            f'Reservación creada exitosamente. ID: {form.instance.invoice_id}'
        )
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('bookings:booking_detail', 
                          kwargs={'booking_id': self.object.booking_id})


class BookingCancelView(LoginRequiredMixin, View):
    """Cancelar una reservación"""
    
    def post(self, request, booking_id):
        booking = get_object_or_404(
            Booking,
            booking_id=booking_id,
            user=request.user
        )
        
        try:
            booking.cancel()
            messages.success(request, 'Reservación cancelada exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al cancelar: {str(e)}')
        
        return redirect('bookings:booking_detail', booking_id=booking_id)


class ValidateCouponView(LoginRequiredMixin, View):
    """Validar cupón de descuento (AJAX)"""
    
    def post(self, request):
        import json
        data = json.loads(request.body)
        code = data.get('code')
        amount = data.get('amount', 0)
        
        try:
            coupon = Coupon.objects.get(code=code)
            
            if not coupon.is_valid():
                return JsonResponse({
                    'valid': False,
                    'message': 'Cupón no válido o expirado'
                })
            
            discount = coupon.calculate_discount(float(amount))
            
            # Guardar en sesión
            request.session['coupon_code'] = code
            
            return JsonResponse({
                'valid': True,
                'discount': float(discount),
                'discount_type': coupon.get_discount_type_display(),
                'message': f'Cupón aplicado: {coupon.code}'
            })
            
        except Coupon.DoesNotExist:
            return JsonResponse({
                'valid': False,
                'message': 'Cupón no encontrado'
            })


class BookingInvoiceView(LoginRequiredMixin, DetailView):
    """Generar factura/comprobante de reservación"""
    model = Booking
    template_name = 'bookings/booking_invoice.html'
    context_object_name = 'booking'
    slug_field = 'booking_id'
    slug_url_kwarg = 'booking_id'
    
    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).select_related(
            'hotel', 'room__room_type', 'coupon', 'user'
        )