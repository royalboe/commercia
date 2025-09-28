# Commercia Backend

Commercia is a backend service for an e-commerce platform built with **Django REST Framework (DRF)**.  
The project provides APIs for managing users, authentication, product catalogs, shopping carts, and orders.  

This README documents the work done over the past week, challenges encountered, and pending improvements.

---

## Table of Contents

- [Commercia Backend](#commercia-backend)
  - [Table of Contents](#table-of-contents)
  - [Project Setup](#project-setup)
  - [Core Features Implemented](#core-features-implemented)
    - [User Management](#user-management)
    - [Product Catalog](#product-catalog)
    - [Cart \& Checkout](#cart--checkout)
    - [Orders](#orders)
  - [Authentication \& Authorization](#authentication--authorization)
  - [Cart \& Order Management](#cart--order-management)
  - [Deployment Setup](#deployment-setup)
  - [Challenges \& Solutions](#challenges--solutions)
    - [1. Cart Functionality](#1-cart-functionality)
    - [2. Order Flow](#2-order-flow)
    - [3. SSH Access Loss](#3-ssh-access-loss)
    - [4. ERD (Entity Relationship Diagram)](#4-erd-entity-relationship-diagram)
  - [Pending Features (WIP)](#pending-features-wip)
  - [Next Steps](#next-steps)
  - [Conclusion](#conclusion)

---

## Project Setup

- **Framework**: Django 5.2 with Django REST Framework.  
- **Database**: PostgreSQL (configured for production with environment variables).  
- **Environment Management**: `.env` using `django-environ`.  
- **Static/Media Storage**: AWS S3 bucket configured for static files and media.  
- **Server**: Gunicorn application server + Nginx as reverse proxy.  
- **Domain**: `royalboe.xyz` integrated via Route 53 / EC2 setup.  
- **OS**: Ubuntu 22.04 on AWS EC2 instance.  

---

## Core Features Implemented

### User Management
- Custom user model integrated.  
- User registration, login, and logout.  
- JWT authentication via **Djoser**.  
- Session-based fallback for unauthenticated carts.

### Product Catalog
- Models for products, categories, and inventory.  
- CRUD APIs for product management.  
- Media file handling (images uploaded to S3).  

### Cart & Checkout
- A user can only have **one active cart** at a time.  
- Guest users can add items via session-based carts (`cart_code`).  
- Cart is created automatically on the first item addition.  
- Items with the same product increment their quantity (instead of duplicating).  
- Cart total auto-calculates on every update.  

### Orders
- Orders linked to user’s cart.  
- Order creation workflow (cart → order).  
- Basic order tracking implemented.

---

## Authentication & Authorization

- **JWT-based auth** using `djoser` + `simplejwt`.  
- Endpoints under `/auth/` for registration, login, token refresh.  
- Authenticated users automatically associate carts with their accounts.  
- Guest sessions are maintained until upgrade (login/register).  

---

## Cart & Order Management

- **Challenges faced**:
  1. Handling the distinction between authenticated and guest carts.  
  2. Deciding whether to use `get_or_create` (discarded because it lost `validated_data`).  
  3. Settled on `update_or_create` with a custom `update` method to preserve validation.  
  4. Incrementing quantity instead of duplicating cart items required manual logic.  

- **Final Design**:
  - `CartItem.objects.update_or_create(cart=cart, product=product, defaults={"quantity": quantity})`  
  - Guests use session key (`cart_code`), logged-in users bind directly to their user.  
  - Cart retrieval automatically returns a single cart per user/session.  

---

## Deployment Setup

- **Application Server**: Gunicorn.  
- **Web Server**: Nginx for reverse proxy and static file serving.  
- **Static Files**: Stored in S3 (with CloudFront possible for future CDN).  
- **Domain Integration**: `royalboe.xyz` configured and pointed to EC2.  
- **Allowed Hosts Issue**: Fixed by properly stripping commas/spaces in `.env` and using:  

  ```python
  ALLOWED_HOSTS = [h.strip() for h in env.list("ALLOWED_HOSTS")]

- **SSL Termination**: Not yet implemented (pending Let’s Encrypt/Certbot setup).

---

## Challenges & Solutions

### 1. Cart Functionality

* **Problem**: Duplicate cart creation and duplicate items.
* **Solution**: `update_or_create` with custom update logic to increment quantities.

### 2. Order Flow

* **Problem**: Ensuring one cart per user and smooth cart-to-order transition.
* **Solution**: Forced unique cart per user, locked cart once converted to order.

### 3. SSH Access Loss

* **Problem**: EC2 SSH key issues (`Permission denied (publickey)`).
* **Solution**: Regenerated/re-attached new key pair via AWS console.

### 4. ERD (Entity Relationship Diagram)

* **Problem**: `pygraphviz` build errors on Windows.
* **Workaround**: Use `django-extensions graph_models` command with correct setup on Linux.

---

## Pending Features (WIP)

The following features are identified but not yet implemented:

1. **Payment Integration**

   * Gateway integration (e.g., Stripe, PayPal, Flutterwave).
   * Order status updates upon payment success/failure.

2. **Caching & Performance**

   * Redis for caching frequently accessed queries.
   * API response caching for product listings.

3. **Message Queues**

   * RabbitMQ/Celery for async tasks (emails, notifications, payment verification).

4. **Pagination**

   * DRF pagination for product catalog and order history.

5. **Logging & Monitoring**

   * Centralized logging with `structlog`/ELK stack.
   * Error monitoring with Sentry.

6. **CI/CD Pipeline**

   * GitHub Actions or GitLab CI for automated testing/deployment.
   * Auto-build and deploy to EC2 with zero-downtime strategy.

7. **Query Optimization**

   * Indexes for product and order queries.
   * Select-related/prefetch-related tuning.

8. **SSL Termination**

   * Let’s Encrypt with Certbot for HTTPS.

---

## Next Steps

* Implement payment gateway (Stripe or Flutterwave).
* Set up caching with Redis.
* Introduce Celery + RabbitMQ for async background tasks.
* Add pagination and optimize product queries.
* Configure monitoring/logging.
* Automate deployment with CI/CD.
* Enable HTTPS with SSL certificate.

---

## Conclusion

Over the past week, Commercia has evolved into a functional e-commerce backend with user authentication, product management, cart, and order functionality.
The project is deployed to AWS with a custom domain (`royalboe.xyz`) and S3-backed static file storage.

Major challenges such as cart logic, session vs user carts, and domain deployment have been solved.
Pending tasks focus on scaling, security, and reliability to move the project closer to production-grade readiness.
