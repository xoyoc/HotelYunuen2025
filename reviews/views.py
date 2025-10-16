# reviews/views.py
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import ReviewAndRating, ReviewHelpful, HotelStatistics
from bookings.models import Booking, Hotel


class ReviewListView(ListView):
    """Lista todas las reseñas activas"""
    model = ReviewAndRating
    template_name = 'reviews/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 20
    
    def get_queryset(self):
        return ReviewAndRating.objects.filter(
            is_active=True
        ).select_related(
            'user', 'hotel', 'booking'
        ).order_by('-review_date')


class ReviewDetailView(DetailView):
    """Detalle de una reseña"""
    model = ReviewAndRating
    template_name = 'reviews/review_detail.html'
    context_object_name = 'review'
    
    def get_queryset(self):
        return ReviewAndRating.objects.filter(
            is_active=True
        ).select_related('user', 'hotel', 'booking')


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """Crear una nueva reseña"""
    model = ReviewAndRating
    template_name = 'reviews/review_create.html'
    fields = ['rating', 'cleanliness_rating', 'service_rating', 
              'location_rating', 'value_rating', 'title', 
              'review_text', 'would_recommend']
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar que el usuario tenga una reservación completada
        booking_id = request.GET.get('booking_id')
        
        if booking_id:
            try:
                self.booking = Booking.objects.get(
                    booking_id=booking_id,
                    user=request.user,
                    payment_status__in=['PAID', 'CONFIRMED']
                )
                
                # Verificar que no haya reseña existente
                if hasattr(self.booking, 'review'):
                    messages.info(request, 'Ya has dejado una reseña para esta reservación.')
                    return redirect('reviews:review_detail', pk=self.booking.review.pk)
                    
            except Booking.DoesNotExist:
                messages.error(request, 'Reservación no encontrada.')
                return redirect('bookings:booking_list')
        else:
            messages.error(request, 'Debes seleccionar una reservación para reseñar.')
            return redirect('bookings:booking_list')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.hotel = self.booking.hotel
        form.instance.booking = self.booking
        
        messages.success(
            self.request,
            '¡Gracias por tu reseña! Será publicada después de moderación.'
        )
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('reviews:review_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking'] = self.booking
        return context


class HotelReviewsView(ListView):
    """Lista las reseñas de un hotel específico"""
    model = ReviewAndRating
    template_name = 'reviews/hotel_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 10
    
    def dispatch(self, request, *args, **kwargs):
        self.hotel = get_object_or_404(Hotel, slug=kwargs['hotel_slug'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = ReviewAndRating.objects.filter(
            hotel=self.hotel,
            is_active=True
        ).select_related('user', 'booking').order_by('-review_date')
        
        # Filtrar por calificación
        rating = self.request.GET.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
        
        # Ordenar
        ordering = self.request.GET.get('ordering', '-review_date')
        if ordering == 'helpful':
            queryset = queryset.order_by('-helpful_count', '-review_date')
        elif ordering == 'rating_high':
            queryset = queryset.order_by('-rating', '-review_date')
        elif ordering == 'rating_low':
            queryset = queryset.order_by('rating', '-review_date')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hotel'] = self.hotel
        
        # Obtener o crear estadísticas
        stats, created = HotelStatistics.objects.get_or_create(hotel=self.hotel)
        if created:
            stats.update_statistics()
        
        context['statistics'] = stats
        
        # Distribución de calificaciones
        rating_distribution = {}
        for i in range(1, 6):
            count = self.get_queryset().filter(rating=i).count()
            rating_distribution[i] = count
        
        context['rating_distribution'] = rating_distribution
        
        return context


class MarkReviewHelpfulView(LoginRequiredMixin, View):
    """Marcar una reseña como útil"""
    
    def post(self, request, pk):
        review = get_object_or_404(ReviewAndRating, pk=pk, is_active=True)
        
        # Verificar si ya votó
        helpful, created = ReviewHelpful.objects.get_or_create(
            review=review,
            user=request.user
        )
        
        if created:
            message = 'Has marcado esta reseña como útil.'
            action = 'added'
        else:
            helpful.delete()
            message = 'Has quitado tu voto de utilidad.'
            action = 'removed'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'action': action,
                'helpful_count': review.helpful_count,
                'message': message
            })
        
        messages.success(request, message)
        return redirect('reviews:review_detail', pk=pk)