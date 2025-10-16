# Hotel Yunuen - Sistema de Gestión Hotelera

Sistema de gestión hotelera desarrollado en Django para Hotel Yunuen, ubicado en Pátzcuaro, Michoacán. Este sistema incluye gestión completa de reservas, habitaciones, reseñas de huéspedes y análisis estadísticos.

## 🏨 Características Principales

- **Gestión de Reservaciones**: Creación, modificación, cancelación y seguimiento de reservas
- **Sistema de Habitaciones**: Gestión de tipos de habitaciones, disponibilidad y precios
- **Reseñas y Calificaciones**: Sistema completo de feedback de huéspedes con moderación
- **Cupones de Descuento**: Sistema flexible de cupones con validaciones
- **Estadísticas en Tiempo Real**: Analytics de ocupación, ingresos y satisfacción
- **Procesamiento Asíncrono**: Tareas programadas con Celery
- **Interfaz Responsiva**: Frontend moderno con Bootstrap 5

## 🛠️ Stack Tecnológico

- **Backend**: Django 5.2.7
- **Base de Datos**: SQLite (desarrollo), compatible con PostgreSQL
- **Cache**: Redis con django-redis
- **Procesamiento Asíncrono**: Celery 5.5.3
- **Frontend**: Bootstrap 5, Font Awesome, jQuery
- **Manejo de Imágenes**: Pillow
- **Localización**: Español México (es-mx)

## 📋 Requisitos

- Python 3.12+
- Redis (para cache y Celery)
- Las dependencias están listadas en `requirements.txt`

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone [URL_DEL_REPOSITORIO]
cd HotelYunuen
```

### 2. Crear y activar entorno virtual

```bash
python -m venv .venv_hotel
source .venv_hotel/bin/activate  # Linux/Mac
# o en Windows:
# .venv_hotel\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos

```bash
python manage.py migrate
```

### 5. Crear superusuario

```bash
python manage.py createsuperuser
```

### 6. Cargar datos de prueba (opcional)

```bash
python manage.py generate_test_data
```

## 🏃‍♂️ Ejecutar el Proyecto

### Servidor de Desarrollo

```bash
python manage.py runserver
```

El servidor estará disponible en `http://127.0.0.1:8000/`

### Ejecutar Celery Worker (en otra terminal)

```bash
celery -A config worker -l info
```

### Ejecutar Celery Beat para tareas programadas (en otra terminal)

```bash
celery -A config beat -l info
```

## 📁 Estructura del Proyecto

```
HotelYunuen/
├── config/                     # Configuración principal del proyecto
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py              # Configuración de Celery
│   ├── settings.py            # Configuración de Django
│   ├── urls.py                # URLs principales
│   └── wsgi.py
├── bookings/                  # App de reservaciones
│   ├── management/commands/   # Comandos de administración
│   │   ├── check_expired_bookings.py
│   │   ├── generate_test_data.py
│   │   └── update_room_availability.py
│   ├── migrations/
│   ├── models.py             # Modelos: Hotel, Booking, Coupon
│   ├── views.py              # Vistas para gestión de reservas
│   ├── urls.py               # URLs de reservaciones
│   ├── admin.py              # Configuración del admin
│   ├── signals.py            # Señales Django
│   └── utils.py              # Utilidades
├── rooms/                    # App de habitaciones
│   ├── migrations/
│   ├── models.py             # Modelos: RoomType, Room, Amenity
│   ├── views.py              # Vistas de habitaciones
│   ├── urls.py               # URLs de habitaciones
│   └── admin.py              # Admin de habitaciones
├── reviews/                  # App de reseñas
│   ├── management/commands/
│   │   └── refresh_hotel_statistics.py
│   ├── migrations/
│   ├── models.py             # Modelos: ReviewAndRating, HotelStatistics
│   ├── views.py              # Vistas de reseñas
│   ├── urls.py               # URLs de reseñas
│   ├── signals.py            # Señales para estadísticas
│   └── admin.py              # Admin de reseñas
├── templates/                # Templates HTML
│   ├── base.html             # Template base
│   ├── bookings/
│   │   └── booking_detail.html
│   └── rooms/
│       └── room_type_list.html
├── static/                   # Archivos estáticos (CSS, JS, imágenes)
├── media/                    # Archivos subidos por usuarios
├── db.sqlite3               # Base de datos SQLite
├── manage.py                # Comando de gestión Django
├── requirements.txt         # Dependencias Python
├── WARP.md                  # Configuración para WARP
└── README.md                # Este archivo
```

## 🏗️ Arquitectura del Sistema

### Modelos Principales

#### **Hotel**
- Información básica del hotel (nombre, dirección, horarios)
- Configuración de check-in/check-out
- Soporte para múltiples ubicaciones

#### **Booking (Reservación)**
- Gestión completa de reservas con UUIDs únicos
- Cálculo automático de precios con descuentos e impuestos
- Estados de pago: PENDING, PAID, CONFIRMED, CANCELLED, REFUNDED
- Validaciones de disponibilidad y capacidad

#### **RoomType y Room**
- Tipos de habitaciones con precios y comodidades
- Habitaciones individuales con estados operativos
- Sistema de disponibilidad inteligente

#### **Coupon**
- Sistema flexible de cupones (porcentaje o monto fijo)
- Validaciones por fechas, uso máximo y montos mínimos
- Aplicación automática de descuentos

#### **ReviewAndRating**
- Reseñas verificadas con calificaciones detalladas
- Respuestas del hotel y sistema de moderación
- Cálculo de estadísticas agregadas

### Funcionalidades Avanzadas

#### **Tareas Programadas (Celery)**
- **Actualización de disponibilidad**: Diaria a medianoche
- **Verificación de reservas expiradas**: Diaria a la 1 AM
- **Actualización de estadísticas**: Semanal los lunes a las 2 AM

#### **Sistema de Cache**
- Cache con Redis para optimizar consultas frecuentes
- Configuración en `settings.py` línea 129-137

#### **Localización**
- Interfaz completamente en español
- Zona horaria: America/Mexico_City
- Formato de moneda y fechas mexicano

## 🔧 Comandos Útiles

### Gestión de Datos

```bash
# Generar datos de prueba
python manage.py generate_test_data

# Actualizar disponibilidad de habitaciones
python manage.py update_room_availability

# Verificar reservas expiradas
python manage.py check_expired_bookings

# Refrescar estadísticas de hoteles
python manage.py refresh_hotel_statistics
```

### Base de Datos

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Reset de la base de datos (cuidado en producción)
python manage.py flush
```

### Administración

```bash
# Crear superusuario
python manage.py createsuperuser

# Shell interactivo
python manage.py shell

# Recopilar archivos estáticos
python manage.py collectstatic
```

## 🌐 URLs Principales

- **Home**: `/`
- **Admin**: `/admin/`
- **Habitaciones**: `/rooms/`
- **Reservaciones**: `/bookings/`
- **Reseñas**: `/reviews/`

## 📊 Funciones de Negocio

### Gestión de Reservas
- Creación de reservas con validación automática de disponibilidad
- Cálculo dinámico de precios con descuentos e impuestos (IVA 16%)
- Sistema de cupones con múltiples tipos de descuento
- Cancelaciones con políticas flexibles

### Gestión de Habitaciones
- Múltiples tipos de habitaciones con diferentes comodidades
- Control de estado de habitaciones (disponible, ocupada, mantenimiento, limpieza)
- Gestión de inventario automática

### Analytics y Reportes
- Estadísticas de ocupación y ingresos
- Análisis de satisfacción del cliente
- Reportes de desempeño por período

## 🔒 Consideraciones de Seguridad

- Validación de entrada en todos los formularios
- Protección CSRF habilitada
- Autenticación requerida para operaciones sensibles
- Logs de auditoría en operaciones críticas

## 🚀 Despliegue

Para producción, considera:

1. Cambiar a PostgreSQL en `settings.py`
2. Configurar variables de entorno para secretos
3. Usar un servidor web como Nginx + Gunicorn
4. Configurar SSL/HTTPS
5. Implementar backup automático de la base de datos

## 📝 Contribución

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit de cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📞 Contacto

**Hotel Yunuen**
- Dirección: Av. Principal 123, Cd. Lázaro Cárdenas, Michoacán
- Teléfono: +52 434 342 0000
- Email: info@hotelyunuen.com

---

*Desarrollado con ❤️ para Hotel Yunuen Cd. Lázaro Cárdenas, Michoacán*