# Commercia Backend

Commercia is a Django + Django REST Framework backend for an e-commerce platform. This repo contains models, serializers, viewsets, admin config, signals and deployment settings used to power the product catalog, cart, orders, reviews, wishlists, and users.

> This README documents the work done over the past week-plus: implemented features, endpoints, challenges, and WIP items.

---

## Table of Contents

- [Commercia Backend](#commercia-backend)
  - [Table of Contents](#table-of-contents)
  - [Setup \& quick commands](#setup--quick-commands)
  - [Major implemented features](#major-implemented-features)
  - [Deployment summary](#deployment-summary)
  - [API Endpoints (full list)](#api-endpoints-full-list)
    - [Authentication (Djoser + Token + JWT)](#authentication-djoser--token--jwt)
      - [Register](#register)
      - [Obtain DRF Token](#obtain-drf-token)
      - [JWT (if using JWT endpoints)](#jwt-if-using-jwt-endpoints)
      - [Current user info](#current-user-info)
    - [Users](#users)
    - [Categories](#categories)
    - [Products](#products)
    - [Cart \& Cart Items](#cart--cart-items)
    - [Orders](#orders)
    - [Reviews](#reviews)
    - [Wishlists](#wishlists)
    - [Admin](#admin)
  - [Data model summary (entities)](#data-model-summary-entities)
  - [Important notes \& known quirks](#important-notes--known-quirks)
  - [Challenges encountered \& how we solved them](#challenges-encountered--how-we-solved-them)
  - [Work-in-progress / future improvements](#work-in-progress--future-improvements)
  - [API examples (curl)](#api-examples-curl)
  - [Final notes](#final-notes)

---

## Setup & quick commands

```bash
# create virtualenv, install requirements
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# run migrations (postgres example)
python manage.py migrate

# create a superuser
python manage.py createsuperuser

# run local server
python manage.py runserver

# collect static to S3 (when configured)
python manage.py collectstatic
```

Make sure your `.env` includes DB and AWS credentials, JWT settings and `ALLOWED_HOSTS`.

---

## Major implemented features

* Custom `User` model (email-based authentication).
* CRUD APIs for Products and Categories (with nested relationship: each `Category` lists its products).
* Cart & CartItem models supporting:

  * single cart per user,
  * guest session cart via `cart_code` (session key),
  * adding items by product `slug`, incrementing quantity when same product added.
* Orders & OrderItem models capturing `price_at_order` at creation.
* Reviews with a signal that keeps product average rating (`ProductRating`) up to date.
* Wishlist per user (toggle behavior).
* Admin customization to allow adding `OrderItem` inline and record `price_at_order`.
* Deployment skeleton for EC2 + Gunicorn + Nginx and S3-backed static/media storage.

---

## Deployment summary

* Gunicorn application server + Nginx as reverse proxy recommended for production.
* AWS RDS (Postgres) used as the production DB.
* AWS S3 + `django-storages` for static + media files.
* Use environment variables (via `django-environ`) to store secrets and service credentials.
* Basic production security settings included (secure cookies, SSL redirect, X-Frame options) — ensure you have SSL termination in place (Nginx / load balancer + cert).

---

## API Endpoints (full list)

Base URL: `/api/` (router)

> Authentication endpoints served under `/auth/` by Djoser and djoser token/jwt modules.

---

### Authentication (Djoser + Token + JWT)

#### Register

* `POST /auth/users/`
* Payload:

```json
{
  "email": "alice@example.com",
  "username": "alice",
  "password": "supersecret"
}
```

* Response: created user (Djoser default fields).

#### Obtain DRF Token

* `POST /auth/token/login/`
* Payload:

```json
{
  "email": "alice@example.com",
  "password": "supersecret"
}
```

* Response:

```json
{"auth_token": "693cdc6d218..."}
```

* Use header: `Authorization: Token 693cdc6d218...`

#### JWT (if using JWT endpoints)

* `POST /auth/jwt/create/`

```json
{"email":"alice@example.com","password":"supersecret"}
```

* Response includes `access` and `refresh`.
* Use header: `Authorization: Bearer <access_token>`

#### Current user info

* `GET /auth/users/me/` (Djoser)
* Requires auth header.

---

### Users

* Base: `/api/users/`

| Path                    |      Method | Description            |
| ----------------------- | ----------: | ---------------------- |
| `/api/users/`           |       `GET` | List users             |
| `/api/users/`           |      `POST` | Create user (register) |
| `/api/users/{user_id}/` |       `GET` | Retrieve user          |
| `/api/users/{user_id}/` | `PUT/PATCH` | Update user            |
| `/api/users/{user_id}/` |    `DELETE` | Delete user            |

**Create payload example** (user creation via serializer):

```json
{
  "email": "alice@example.com",
  "username": "alice",
  "password": "supersecret",
  "first_name": "Alice",
  "last_name": "Smith",
  "phone_number": "+11234567890",
  "address": "123 Any Street",
  "date_of_birth": "1990-01-01"
}
```

> Note: password is WRITE ONLY and gets hashed before saving (see `UserCreateUpdateSerializer`).

---

### Categories

* Base: `/api/categories/`
* `CategoryViewSet` uses `lookup_field = 'slug'` — **category retrieve uses slug**.

| Path                      |             Method | Description                        |
| ------------------------- | -----------------: | ---------------------------------- |
| `/api/categories/`        |              `GET` | List categories                    |
| `/api/categories/`        |             `POST` | Create category                    |
| `/api/categories/{slug}/` |              `GET` | Retrieve category and its products |
| `/api/categories/{slug}/` | `PUT/PATCH/DELETE` | Update / delete                    |

**Create payload example:**

```json
{
  "name": "Home Appliances",
  "description": "Appliances for home use"
}
```

**Response (detail)** includes `products` (list of nested products).

---

### Products

* Base: `/api/products/`
* `ProductViewSet` uses `lookup_field = 'slug'`.

| Path                    |             Method | Description             |
| ----------------------- | -----------------: | ----------------------- |
| `/api/products/`        |              `GET` | List products           |
| `/api/products/`        |             `POST` | Create product          |
| `/api/products/{slug}/` |              `GET` | Retrieve product detail |
| `/api/products/{slug}/` | `PUT/PATCH/DELETE` | Update / delete product |

**Create payload example** (JSON or multipart if uploading `image_field`):

```json
{
  "name": "Electric Iron",
  "description": "Steam iron with auto-shutoff",
  "price": "29.99",
  "stock": 50,
  "categories": ["<category_uuid1>", "<category_uuid2>"]
}
```

**Notes**

* Product listing and detail include `slug` and `image_field`.
* Images uploaded are stored using the configured storage backend (S3 in production).

---

### Cart & Cart Items

* Base: `/api/carts/`

`Cart` design notes:

* One cart per authenticated user (OneToOne). Guest carts rely on `cart_code` (session key).
* When adding items for a logged-in user, the API will look for the user's cart or create one on first add.
* `CartCreateUpdateSerializer` expects `items` with product `slug` and `quantity`.

| Path                    |      Method | Description                                              |
| ----------------------- | ----------: | -------------------------------------------------------- |
| `/api/carts/`           |       `GET` | List carts (when authenticated returns user's cart only) |
| `/api/carts/`           |      `POST` | Add/update cart items (create cart if none exists)       |
| `/api/carts/{cart_id}/` |       `GET` | Retrieve cart detail                                     |
| `/api/carts/{cart_id}/` | `PUT/PATCH` | Update cart (items)                                      |
| `/api/carts/{cart_id}/` |    `DELETE` | Delete cart                                              |

**Add item(s) payload (POST /api/carts/)**:

```json
{
  "items": [
    {"product": "electric-iron", "quantity": 2},
    {"product": "coffee-mug", "quantity": 1}
  ]
}
```

* `product` uses slug (because `ItemInputSerializer` is a `SlugRelatedField`).
* For logged-in requests, your viewset `perform_create` sets `user` automatically. For guest requests, session key saved to `cart_code`.

**Behavior**

* If the same product is posted multiple times, logic increments the `CartItem.quantity` rather than creating duplicates.
* `CartSerializer` returns nested items and `cart_total` (sum of active item subtotals).

---

### Orders

* Base: `/api/orders/`

| Path                      |      Method | Description    |
| ------------------------- | ----------: | -------------- |
| `/api/orders/`            |       `GET` | List orders    |
| `/api/orders/`            |      `POST` | Create order   |
| `/api/orders/{order_id}/` |       `GET` | Retrieve order |
| `/api/orders/{order_id}/` | `PUT/PATCH` | Update order   |
| `/api/orders/{order_id}/` |    `DELETE` | Delete order   |

**Create order payload** (current implementation expects product primary keys):

```json
{
  "user": "<user_uuid>",
  "items": [
    {"product": "<product_uuid>", "quantity": 2},
    {"product": "<product_uuid2>", "quantity": 1}
  ],
  "status": "pending"
}
```

**Important**

* `OrderItem.price_at_order` is set using the product's price at the time of order creation (server-side).
* The current API **requires `user`** in the order POST (this is a known quirk — you may want to switch to `request.user` inside `perform_create` to avoid sending user id from front-end).
* `Order.calculate_total()` computes and saves the order total (captured at order creation or when items change).

---

### Reviews

* Base: `/api/reviews/`

| Path                        |             Method | Description                             |
| --------------------------- | -----------------: | --------------------------------------- |
| `/api/reviews/`             |              `GET` | List reviews                            |
| `/api/reviews/`             |             `POST` | Create review (authenticated preferred) |
| `/api/reviews/{review_id}/` |              `GET` | Get review                              |
| `/api/reviews/{review_id}/` | `PUT/PATCH/DELETE` | modify / delete                         |

**Create payload** (ReviewCreateSerializer expects `product` as slug):

```json
{
  "product": "electric-iron",
  "rating": 4,
  "comment": "Heats quickly, light and easy to use."
}
```

* `ReviewViewSet.perform_create` attaches `user=self.request.user` automatically when logged in.
* A post_save/post_delete signal recalculates the `ProductRating` (average & total).

---

### Wishlists

* Base: `/api/wishlists/`
* `WishlistViewSet` restricted to authenticated users.

| Path                            |      Method | Description                                   |
| ------------------------------- | ----------: | --------------------------------------------- |
| `/api/wishlists/`               |       `GET` | Get current user's wishlist                   |
| `/api/wishlists/`               |      `POST` | Toggle a product in the wishlist (add/remove) |
| `/api/wishlists/{wishlist_id}/` |       `GET` | Get wishlist detail                           |
| `/api/wishlists/{wishlist_id}/` | `PUT/PATCH` | Update wishlist                               |
| `/api/wishlists/{wishlist_id}/` |    `DELETE` | Remove wishlist                               |

**Toggle payload (create/update)**:

```json
{
  "product": "electric-iron"
}
```

* The serializer/viewset logic does `get_or_create(user=request.user)` and toggles the product: if present => remove, otherwise add.
* Response shape currently returns a serialized wishlist (read serializer).

---

### Admin

* Django admin interface: `/admin/`
* Custom admin config permits inline creation of `OrderItem` for orders; `OrderAdmin.save_formset()` ensures `price_at_order` is populated from product price if not provided.

---

## Data model summary (entities)

* `User` (custom `AbstractUser`, primary key `user_id`, uses `email` as USERNAME_FIELD)
* `Category` (slug, image, products many-to-many)
* `Product` (slug, image, price, stock, categories m2m)
* `Cart` (OneToOne with User OR guest `cart_code`, CartItems related_name `items`)
* `CartItem` (cart FK, product FK, quantity, is_active)
* `Order` (user FK, through `OrderItem`, status, total_amount)
* `OrderItem` (order FK, product FK, quantity, price_at_order)
* `Review` (product FK, user FK, rating, comment)
* `ProductRating` (one-to-one product rating aggregated from reviews)
* `Wishlist` (user FK, products m2m)

---

## Important notes & known quirks

* **Products & Categories use `slug` lookups**: `ProductViewSet` and `CategoryViewSet` use `lookup_field='slug'`. Use the slug for retrieving product/category detail.
* **Order creation currently requires `user`** in serializer payload (server-side fix recommended: use `perform_create` to attach `request.user` instead).
* **Cart behavior**:

  * Only one cart per authenticated user (`OneToOneField`).
  * If user is not authenticated, cart uses session key `cart_code`.
  * When user logs in, `signals.handle_cart_merge` attempts to merge session cart items into user cart.
* **`calculate_total()` quirk**: ensure your `Order.calculate_total()` writes to `total_amount` field — earlier versions accidentally set `total_price` attribute which doesn’t exist on `Order`. (Fix: set `self.total_amount = total` then `self.save()`.)
* **Wishlist toggle**: serializer returns the wishlist's products (ensure you return a serializable representation — use the read serializer to return the final wishlist).
* **Collectstatic**: ensure `STATIC_ROOT` is set for local `collectstatic` when not using S3. For S3-backed storage, `STATICFILES_STORAGE` and `DEFAULT_FILE_STORAGE` are set to custom S3 backends in `api.storage_backends`.
* **Allowed hosts**: make sure `.env` `ALLOWED_HOSTS` is parsed correctly and stripped of whitespace.

---

## Challenges encountered & how we solved them

* **Cart merging (guest -> user)**: Use session `cart_code` and a `user_logged_in` signal to merge (with atomic transaction).
* **Duplicate cart creation**: Ensure we `get_or_create()` properly and use `.exists()` and `.get()` checks rather than blind `create()`.
* **Order item `price_at_order`**: Admin inline `save_formset` and order creation logic ensures `price_at_order` is set from `Product.price` before insertion.
* **pygraphviz / ERD generation on Windows**: building `pygraphviz` from source can fail on Windows without Visual C++ Build Tools. Use Linux or WSL / prebuilt binaries, or alternatives (e.g., `erdantic`, or export model info programmatically).
* **SSH publickey issues**: re-generate / re-attach EC2 keypair via AWS console or add your public key to `~/.ssh/authorized_keys` on the instance.

---

## Work-in-progress / future improvements

Planned items (WIP):

* Payment integration (Stripe, Paystack, or Flutterwave).
* Caching & Redis for sessions & query caching.
* Background processing: Celery + RabbitMQ (email sending, background jobs).
* Pagination for product lists and orders (DRF pagination).
* Query optimization (indexes, select_related / prefetch_related).
* Logging & monitoring: Sentry + structured logs; centralized logging stack.
* CI/CD pipeline (GitHub Actions) for testing and automated deploy.
* SSL termination & certificate automation (Let’s Encrypt / Certbot).
* Add tests coverage for endpoints and critical flows.

---

## API examples (curl)

**Get product list**

```bash
curl -X GET "https://royalboe.xyz/api/products/" -H "Accept: application/json"
```

**Create cart (authenticated)**

```bash
curl -X POST "https://royalboe.xyz/api/carts/" \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{"items":[{"product":"electric-iron","quantity":2}]}'
```

**Toggle wishlist (authenticated)**

```bash
curl -X POST "https://royalboe.xyz/api/wishlists/" \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{"product":"electric-iron"}'
```

**Create order** (current serializer expects `user` and product PKs)

```bash
curl -X POST "https://royalboe.xyz/api/orders/" \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user":"<user_uuid>",
    "items":[{"product":"<product_uuid>","quantity":2}]
  }'
```

---

## Final notes

* This README documents current behavior and known issues so you (or future contributors) can quickly understand the API and the decisions made.
* If you want, I can:

  * Add auto-generated OpenAPI docs into the repo (we already have `drf_spectacular` configured).
  * Make a short `API_DOCS.md` with example responses for each endpoint (more sample JSON).
  * Fix the order-create quirk (attach `request.user` automatically) and adjust tests + docs accordingly.
  * Add Postman collection or OpenAPI YAML export.

