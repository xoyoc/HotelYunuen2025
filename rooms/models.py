from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class Amenity(models.Model):
    """Comodidades disponibles en el hotel"""
    name = models.CharField(_("nombre"), max_length=100, unique=True)
    icon = models.CharField(_("icono"), max_length=50, blank=True, help_text="Clase de icono (ej. fa-wifi)")
    description = models.TextField(_("descripción"), blank=True)
    is_active = models.BooleanField(_("activo"), default=True)
    
    class Meta:
        verbose_name = _("comodidad")
        verbose_name_plural = _("comodidades")
        ordering = ['name']
    
    def __str__(self):
        return self.name


class RoomType(models.Model):
    """Tipos de habitaciones disponibles en el hotel"""
    
    class RoomCategory(models.TextChoices):
        BASIC = 'BASIC', _('Básica')
        STANDARD = 'STANDARD', _('Estándar')
        PREMIUM = 'PREMIUM', _('Premium')
        LUXURY = 'LUXURY', _('De Lujo')
        SUITE = 'SUITE', _('Suite')
    
    name = models.CharField(_("nombre"), max_length=100, unique=True)
    category = models.CharField(
        _("categoría"),
        max_length=20,
        choices=RoomCategory.choices,
        default=RoomCategory.STANDARD
    )
    price_per_night = models.DecimalField(
        _("precio por noche"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    number_of_beds = models.PositiveIntegerField(
        _("número de camas"),
        validators=[MinValueValidator(1)]
    )
    room_capacity = models.PositiveIntegerField(
        _("capacidad"),
        validators=[MinValueValidator(1)],
        help_text=_("Capacidad máxima de personas")
    )
    total_rooms = models.PositiveIntegerField(
        _("total de habitaciones"),
        validators=[MinValueValidator(1)],
        help_text=_("Cantidad total de habitaciones de este tipo")
    )
    description = models.TextField(_("descripción"))
    amenities = models.ManyToManyField(
        Amenity,
        verbose_name=_("comodidades"),
        related_name='room_types',
        blank=True
    )
    image = models.ImageField(
        _("imagen"),
        upload_to='room_types/',
        blank=True,
        null=True
    )
    size_sqm = models.DecimalField(
        _("tamaño (m²)"),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(_("activo"), default=True)
    created_at = models.DateTimeField(_("fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("fecha de actualización"), auto_now=True)
    
    class Meta:
        verbose_name = _("tipo de habitación")
        verbose_name_plural = _("tipos de habitación")
        ordering = ['category', 'price_per_night']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price_per_night']),
        ]
    
    def __str__(self):
        return f"{self.name} - ${self.price_per_night}/noche"
    
    def available_rooms_count(self):
        """Retorna el número de habitaciones disponibles de este tipo"""
        return self.rooms.filter(is_available=True).count()


class Room(models.Model):
    """Habitaciones individuales del hotel"""
    
    class RoomStatus(models.TextChoices):
        AVAILABLE = 'AVAILABLE', _('Disponible')
        OCCUPIED = 'OCCUPIED', _('Ocupada')
        MAINTENANCE = 'MAINTENANCE', _('Mantenimiento')
        CLEANING = 'CLEANING', _('Limpieza')
    
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.PROTECT,
        related_name='rooms',
        verbose_name=_("tipo de habitación")
    )
    room_number = models.CharField(
        _("número de habitación"),
        max_length=10,
        unique=True,
        help_text=_("Identificador único de la habitación (ej. 101, 205)")
    )
    floor = models.PositiveIntegerField(
        _("piso"),
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        _("estado"),
        max_length=20,
        choices=RoomStatus.choices,
        default=RoomStatus.AVAILABLE
    )
    is_available = models.BooleanField(
        _("disponible"),
        default=True,
        help_text=_("Disponibilidad para reservas")
    )
    notes = models.TextField(_("notas"), blank=True)
    created_at = models.DateTimeField(_("fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("fecha de actualización"), auto_now=True)
    
    class Meta:
        verbose_name = _("habitación")
        verbose_name_plural = _("habitaciones")
        ordering = ['room_number']
        indexes = [
            models.Index(fields=['room_number']),
            models.Index(fields=['status', 'is_available']),
        ]
    
    def __str__(self):
        return f"Habitación {self.room_number} - {self.room_type.name}"
    
    def is_available_for_dates(self, check_in, check_out):
        """Verifica si la habitación está disponible en un rango de fechas"""
        from bookings.models import Booking
        
        overlapping_bookings = Booking.objects.filter(
            room=self,
            check_in_date__lt=check_out,
            check_out_date__gt=check_in,
            payment_status__in=['PAID', 'CONFIRMED']
        )
        return not overlapping_bookings.exists() and self.is_available