from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg

User = get_user_model()


class ReviewAndRating(models.Model):
    """Reseñas y calificaciones de los huéspedes"""
    
    # Relaciones
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_("usuario")
    )
    hotel = models.ForeignKey(
        'bookings.Hotel',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_("hotel")
    )
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review',
        verbose_name=_("reservación"),
        help_text=_("Reservación asociada a esta reseña")
    )
    
    # Calificaciones detalladas
    rating = models.PositiveIntegerField(
        _("calificación general"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("Calificación de 1 a 5 estrellas")
    )
    cleanliness_rating = models.PositiveIntegerField(
        _("limpieza"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    service_rating = models.PositiveIntegerField(
        _("servicio"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    location_rating = models.PositiveIntegerField(
        _("ubicación"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    value_rating = models.PositiveIntegerField(
        _("relación calidad-precio"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    
    # Contenido de la reseña
    title = models.CharField(
        _("título"),
        max_length=200,
        blank=True,
        help_text=_("Título breve de la reseña")
    )
    review_text = models.TextField(
        _("comentario"),
        help_text=_("Comparte tu experiencia en el hotel")
    )
    
    # Recomendación
    would_recommend = models.BooleanField(
        _("¿recomendarías este hotel?"),
        default=True
    )
    
    # Metadata
    review_date = models.DateTimeField(_("fecha de reseña"), auto_now_add=True)
    updated_at = models.DateTimeField(_("actualizado"), auto_now=True)
    
    # Moderación
    is_active = models.BooleanField(
        _("activo"),
        default=True,
        help_text=_("Las reseñas inactivas no se muestran al público")
    )
    is_verified = models.BooleanField(
        _("verificado"),
        default=False,
        help_text=_("Reseña de un huésped que completó su estancia")
    )
    
    # Respuesta del hotel
    hotel_response = models.TextField(
        _("respuesta del hotel"),
        blank=True
    )
    hotel_response_date = models.DateTimeField(
        _("fecha de respuesta"),
        null=True,
        blank=True
    )
    
    # Utilidad
    helpful_count = models.PositiveIntegerField(
        _("votos útiles"),
        default=0
    )
    
    class Meta:
        verbose_name = _("reseña y calificación")
        verbose_name_plural = _("reseñas y calificaciones")
        ordering = ['-review_date']
        indexes = [
            models.Index(fields=['hotel', 'is_active']),
            models.Index(fields=['user', 'review_date']),
            models.Index(fields=['rating', 'is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'booking'],
                name='unique_review_per_booking',
                condition=models.Q(booking__isnull=False)
            )
        ]
    
    def __str__(self):
        return f"Reseña de {self.user.get_full_name() or self.user.username} - {self.rating}★"
    
    def clean(self):
        # Verificar que el usuario tiene una reservación completada
        if self.booking:
            if self.booking.user != self.user:
                raise ValidationError(_("La reservación no pertenece a este usuario"))
            
            if not self.booking.is_active() and self.booking.payment_status != 'CONFIRMED':
                raise ValidationError(_("Solo puedes reseñar reservaciones completadas"))
    
    def save(self, *args, **kwargs):
        # Marcar como verificado si hay una reservación asociada
        if self.booking:
            self.is_verified = True
        
        super().save(*args, **kwargs)
    
    @property
    def average_detailed_rating(self):
        """Calcula el promedio de las calificaciones detalladas"""
        ratings = [
            self.cleanliness_rating,
            self.service_rating,
            self.location_rating,
            self.value_rating
        ]
        valid_ratings = [r for r in ratings if r is not None]
        
        if valid_ratings:
            return sum(valid_ratings) / len(valid_ratings)
        return self.rating


class ReviewHelpful(models.Model):
    """Votos de utilidad en reseñas"""
    review = models.ForeignKey(
        ReviewAndRating,
        on_delete=models.CASCADE,
        related_name='helpful_votes',
        verbose_name=_("reseña")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='helpful_votes',
        verbose_name=_("usuario")
    )
    created_at = models.DateTimeField(_("fecha"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("voto útil")
        verbose_name_plural = _("votos útiles")
        unique_together = ['review', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.review}"


class HotelStatistics(models.Model):
    """Estadísticas agregadas del hotel (para optimización)"""
    hotel = models.OneToOneField(
        'bookings.Hotel',
        on_delete=models.CASCADE,
        related_name='statistics',
        verbose_name=_("hotel")
    )
    
    # Calificaciones
    average_rating = models.DecimalField(
        _("calificación promedio"),
        max_digits=3,
        decimal_places=2,
        default=0.0
    )
    total_reviews = models.PositiveIntegerField(
        _("total de reseñas"),
        default=0
    )
    
    # Calificaciones detalladas promedio
    avg_cleanliness = models.DecimalField(
        _("limpieza promedio"),
        max_digits=3,
        decimal_places=2,
        default=0.0
    )
    avg_service = models.DecimalField(
        _("servicio promedio"),
        max_digits=3,
        decimal_places=2,
        default=0.0
    )
    avg_location = models.DecimalField(
        _("ubicación promedio"),
        max_digits=3,
        decimal_places=2,
        default=0.0
    )
    avg_value = models.DecimalField(
        _("calidad-precio promedio"),
        max_digits=3,
        decimal_places=2,
        default=0.0
    )
    
    # Recomendaciones
    recommendation_percentage = models.DecimalField(
        _("% recomendaciones"),
        max_digits=5,
        decimal_places=2,
        default=0.0
    )
    
    # Reservaciones
    total_bookings = models.PositiveIntegerField(
        _("total de reservaciones"),
        default=0
    )
    completed_bookings = models.PositiveIntegerField(
        _("reservaciones completadas"),
        default=0
    )
    cancelled_bookings = models.PositiveIntegerField(
        _("reservaciones canceladas"),
        default=0
    )
    
    # Timestamps
    last_updated = models.DateTimeField(_("última actualización"), auto_now=True)
    
    class Meta:
        verbose_name = _("estadísticas del hotel")
        verbose_name_plural = _("estadísticas de hoteles")
    
    def __str__(self):
        return f"Estadísticas - {self.hotel.name}"
    
    def update_statistics(self):
        """Actualiza todas las estadísticas del hotel"""
        from django.db.models import Count, Q
        from decimal import Decimal
        
        # Obtener reseñas activas
        active_reviews = self.hotel.reviews.filter(is_active=True)
        
        # Calificaciones
        self.total_reviews = active_reviews.count()
        
        if self.total_reviews > 0:
            # Calificación promedio general
            self.average_rating = active_reviews.aggregate(
                avg=Avg('rating')
            )['avg'] or Decimal('0.00')
            
            # Calificaciones detalladas promedio
            self.avg_cleanliness = active_reviews.filter(
                cleanliness_rating__isnull=False
            ).aggregate(avg=Avg('cleanliness_rating'))['avg'] or Decimal('0.00')
            
            self.avg_service = active_reviews.filter(
                service_rating__isnull=False
            ).aggregate(avg=Avg('service_rating'))['avg'] or Decimal('0.00')
            
            self.avg_location = active_reviews.filter(
                location_rating__isnull=False
            ).aggregate(avg=Avg('location_rating'))['avg'] or Decimal('0.00')
            
            self.avg_value = active_reviews.filter(
                value_rating__isnull=False
            ).aggregate(avg=Avg('value_rating'))['avg'] or Decimal('0.00')
            
            # Porcentaje de recomendaciones
            recommendations = active_reviews.filter(would_recommend=True).count()
            self.recommendation_percentage = (recommendations / self.total_reviews) * 100
        else:
            self.average_rating = Decimal('0.00')
            self.avg_cleanliness = Decimal('0.00')
            self.avg_service = Decimal('0.00')
            self.avg_location = Decimal('0.00')
            self.avg_value = Decimal('0.00')
            self.recommendation_percentage = Decimal('0.00')
        
        # Estadísticas de reservaciones
        all_bookings = self.hotel.bookings.all()
        self.total_bookings = all_bookings.count()
        self.completed_bookings = all_bookings.filter(
            payment_status__in=['PAID', 'CONFIRMED']
        ).count()
        self.cancelled_bookings = all_bookings.filter(
            payment_status='CANCELLED'
        ).count()
        
        self.save()