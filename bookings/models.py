from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class Hotel(models.Model):
    """Información del hotel (útil para múltiples ubicaciones)"""
    name = models.CharField(_("nombre"), max_length=200)
    slug = models.SlugField(_("slug"), unique=True)
    address = models.TextField(_("dirección"))
    city = models.CharField(_("ciudad"), max_length=100)
    state = models.CharField(_("estado"), max_length=100)
    postal_code = models.CharField(_("código postal"), max_length=10)
    phone = models.CharField(_("teléfono"), max_length=20)
    email = models.EmailField(_("email"))
    description = models.TextField(_("descripción"))
    check_in_time = models.TimeField(_("hora de check-in"), default="15:00")
    check_out_time = models.TimeField(_("hora de check-out"), default="12:00")
    is_active = models.BooleanField(_("activo"), default=True)
    created_at = models.DateTimeField(_("fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("fecha de actualización"), auto_now=True)
    
    class Meta:
        verbose_name = _("hotel")
        verbose_name_plural = _("hoteles")
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Coupon(models.Model):
    """Cupones de descuento para reservaciones"""
    
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'PERCENTAGE', _('Porcentaje')
        FIXED = 'FIXED', _('Monto Fijo')
    
    code = models.CharField(
        _("código"),
        max_length=50,
        unique=True,
        help_text=_("Código único del cupón")
    )
    discount_type = models.CharField(
        _("tipo de descuento"),
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE
    )
    discount_value = models.DecimalField(
        _("valor del descuento"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    min_amount = models.DecimalField(
        _("monto mínimo"),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Monto mínimo de reserva para aplicar el cupón")
    )
    max_discount = models.DecimalField(
        _("descuento máximo"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Descuento máximo aplicable (solo para porcentajes)")
    )
    valid_from = models.DateTimeField(_("válido desde"))
    valid_until = models.DateTimeField(_("válido hasta"))
    max_uses = models.PositiveIntegerField(
        _("usos máximos"),
        null=True,
        blank=True,
        help_text=_("Número máximo de veces que puede usarse el cupón")
    )
    times_used = models.PositiveIntegerField(_("veces usado"), default=0)
    is_active = models.BooleanField(_("activo"), default=True)
    created_at = models.DateTimeField(_("fecha de creación"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("cupón")
        verbose_name_plural = _("cupones")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'PERCENTAGE' else '$'}"
    
    def clean(self):
        if self.valid_from >= self.valid_until:
            raise ValidationError(_("La fecha de inicio debe ser anterior a la fecha de fin"))
        
        if self.discount_type == 'PERCENTAGE' and self.discount_value > 100:
            raise ValidationError(_("El porcentaje de descuento no puede ser mayor a 100"))
    
    def is_valid(self):
        """Verifica si el cupón es válido actualmente"""
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.max_uses and self.times_used >= self.max_uses:
            return False
        return True
    
    def calculate_discount(self, amount):
        """Calcula el descuento para un monto dado"""
        if not self.is_valid() or amount < self.min_amount:
            return Decimal('0.00')
        
        if self.discount_type == 'PERCENTAGE':
            discount = amount * (self.discount_value / 100)
            if self.max_discount:
                discount = min(discount, self.max_discount)
        else:
            discount = self.discount_value
        
        return min(discount, amount)  # No puede ser mayor al monto total


class Booking(models.Model):
    """Reservaciones de habitaciones"""
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pendiente')
        PAID = 'PAID', _('Pagado')
        CONFIRMED = 'CONFIRMED', _('Confirmado')
        CANCELLED = 'CANCELLED', _('Cancelado')
        REFUNDED = 'REFUNDED', _('Reembolsado')
    
    # Identificadores
    booking_id = models.UUIDField(
        _("ID de reserva"),
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    invoice_id = models.CharField(
        _("ID de factura"),
        max_length=100,
        unique=True,
        editable=False
    )
    
    # Relaciones
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_("usuario")
    )
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name=_("hotel")
    )
    room = models.ForeignKey(
        'rooms.Room',
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name=_("habitación")
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        verbose_name=_("cupón")
    )
    
    # Fechas
    check_in_date = models.DateField(_("fecha de check-in"))
    check_out_date = models.DateField(_("fecha de check-out"))
    booking_date = models.DateTimeField(_("fecha de reserva"), auto_now_add=True)
    
    # Huéspedes
    adults = models.PositiveIntegerField(
        _("adultos"),
        validators=[MinValueValidator(1)]
    )
    children = models.PositiveIntegerField(
        _("niños"),
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Información adicional
    special_requests = models.TextField(
        _("solicitudes especiales"),
        blank=True,
        help_text=_("Necesidades especiales o preferencias")
    )
    
    # Precios
    subtotal = models.DecimalField(
        _("subtotal"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    discount_amount = models.DecimalField(
        _("descuento"),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    tax_amount = models.DecimalField(
        _("impuestos"),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_price = models.DecimalField(
        _("precio total"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Estado
    payment_status = models.CharField(
        _("estado de pago"),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    
    # Timestamps
    created_at = models.DateTimeField(_("creado"), auto_now_add=True)
    updated_at = models.DateTimeField(_("actualizado"), auto_now=True)
    
    class Meta:
        verbose_name = _("reservación")
        verbose_name_plural = _("reservaciones")
        ordering = ['-booking_date']
        indexes = [
            models.Index(fields=['user', 'payment_status']),
            models.Index(fields=['check_in_date', 'check_out_date']),
            models.Index(fields=['hotel', 'payment_status']),
            models.Index(fields=['booking_id']),
        ]
    
    def __str__(self):
        return f"Reserva {self.invoice_id} - {self.user.get_full_name() or self.user.username}"
    
    def save(self, *args, **kwargs):
        # Generar invoice_id si no existe
        if not self.invoice_id:
            self.invoice_id = f"INV-{uuid.uuid4().hex[:12].upper()}"
        
        # Calcular total_days y precios
        if self.check_in_date and self.check_out_date:
            self.calculate_prices()
        
        super().save(*args, **kwargs)
    
    def clean(self):
        # Validar fechas
        if self.check_in_date and self.check_out_date:
            if self.check_in_date >= self.check_out_date:
                raise ValidationError(_("La fecha de check-in debe ser anterior a la de check-out"))
            
            if self.check_in_date < timezone.now().date():
                raise ValidationError(_("La fecha de check-in no puede ser en el pasado"))
        
        # Validar capacidad
        if self.room:
            total_guests = self.adults + self.children
            if total_guests > self.room.room_type.room_capacity:
                raise ValidationError(
                    _(f"La habitación solo permite {self.room.room_type.room_capacity} huéspedes")
                )
        
        # Validar disponibilidad
        if self.room and self.check_in_date and self.check_out_date:
            if not self.room.is_available_for_dates(self.check_in_date, self.check_out_date):
                raise ValidationError(_("La habitación no está disponible para las fechas seleccionadas"))
    
    @property
    def total_days(self):
        """Calcula el número total de días de la estancia"""
        if self.check_in_date and self.check_out_date:
            return (self.check_out_date - self.check_in_date).days
        return 0
    
    def calculate_prices(self):
        """Calcula todos los precios de la reservación"""
        # Subtotal
        self.subtotal = self.room.room_type.price_per_night * self.total_days
        
        # Aplicar cupón si existe
        if self.coupon and self.coupon.is_valid():
            self.discount_amount = self.coupon.calculate_discount(self.subtotal)
        else:
            self.discount_amount = Decimal('0.00')
        
        # Calcular impuestos (16% IVA - ajustar según necesidad)
        taxable_amount = self.subtotal - self.discount_amount
        self.tax_amount = taxable_amount * Decimal('0.16')
        
        # Total
        self.total_price = self.subtotal - self.discount_amount + self.tax_amount
    
    def can_be_cancelled(self):
        """Verifica si la reservación puede ser cancelada"""
        if self.payment_status in ['CANCELLED', 'REFUNDED']:
            return False
        
        # No se puede cancelar si ya pasó el check-in
        if self.check_in_date <= timezone.now().date():
            return False
        
        return True
    
    def cancel(self):
        """Cancela la reservación"""
        if not self.can_be_cancelled():
            raise ValidationError(_("Esta reservación no puede ser cancelada"))
        
        self.payment_status = self.PaymentStatus.CANCELLED
        self.save()
    
    def is_active(self):
        """Verifica si la reservación está activa (dentro del periodo)"""
        today = timezone.now().date()
        return (
            self.check_in_date <= today <= self.check_out_date
            and self.payment_status in ['PAID', 'CONFIRMED']
        )