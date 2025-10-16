# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

HotelYunuen is a hotel management system. This appears to be a new project in early development stages.

## Development Commands

Since this is a new project, the following commands will be established as the project develops:

### Setup
```bash
# Install dependencies (will vary by technology stack chosen)
npm install          # For Node.js/React projects
composer install     # For PHP/Laravel projects
pip install -r requirements.txt  # For Python projects
```

### Development Server
```bash
# Start development server (technology-specific)
npm run dev         # For Node.js/React
php artisan serve   # For Laravel
python manage.py runserver  # For Django
```

### Testing
```bash
# Run tests (to be established)
npm test           # For Node.js projects
php artisan test   # For Laravel projects
python -m pytest  # For Python projects
```

### Building
```bash
# Build for production (to be established)
npm run build      # For Node.js projects
php artisan optimize  # For Laravel optimization
```

## Project Architecture

This is a new project, so the architecture will be established during development. Common patterns for hotel management systems include:

### Core Modules (Expected)
- **Reservations Management**: Handle booking creation, modification, and cancellation
- **Room Management**: Room types, availability, pricing, and maintenance
- **Guest Management**: Customer profiles, preferences, and history
- **Payment Processing**: Billing, invoicing, and payment gateway integration
- **Staff Management**: Employee roles, scheduling, and permissions
- **Reporting**: Occupancy rates, revenue analytics, and operational reports

### Database Design Considerations
- Rooms: room numbers, types, amenities, status
- Reservations: guest info, dates, pricing, status
- Guests: contact information, preferences, loyalty status
- Payments: transactions, methods, refunds
- Staff: roles, permissions, schedules

### API Design
- RESTful endpoints for all major entities
- Authentication and authorization
- Rate limiting and security measures
- API documentation (OpenAPI/Swagger)

## Technology Stack

The technology stack has not yet been established. Consider:

### Frontend Options
- React with TypeScript for modern web applications
- Vue.js for component-based development
- Laravel Blade for PHP-based solutions

### Backend Options
- Node.js with Express for JavaScript-based APIs
- Laravel for PHP-based development with built-in features
- Django/FastAPI for Python-based solutions

### Database Options
- PostgreSQL for complex relational data
- MySQL for traditional web applications
- MongoDB for flexible document storage

## Development Guidelines

### Code Organization
- Separate concerns between frontend and backend
- Use environment variables for configuration
- Implement proper error handling and logging
- Follow REST API conventions
- Use meaningful commit messages

### Security Considerations
- Implement user authentication and authorization
- Secure payment processing (PCI compliance)
- Data encryption for sensitive information
- Input validation and sanitization
- HTTPS enforcement in production

### Performance
- Implement caching strategies for frequently accessed data
- Optimize database queries
- Use connection pooling
- Implement proper indexing
- Monitor application performance

## Hotel-Specific Features to Consider

### Booking System
- Real-time availability checking
- Dynamic pricing based on demand
- Overbooking management
- Group bookings and corporate rates

### Guest Experience
- Online check-in/check-out
- Digital key integration
- Guest communication system
- Loyalty program integration

### Operations
- Housekeeping management
- Maintenance scheduling
- Inventory management
- Staff shift management

### Integrations
- Property Management Systems (PMS)
- Channel managers for online booking platforms
- Payment gateways
- Email and SMS services
- Analytics and reporting tools