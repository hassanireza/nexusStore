# NEXUS Store

<p align="center">
  <img src="./assets/banner.png" width="100%" alt="Nexus Store">
</p>

<h1 align="center">NEXUS Store</h1>

<p align="center">
Production-ready Django e-commerce platform.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/PostgreSQL-Ready-336791?style=for-the-badge&logo=postgresql">
  <img src="https://img.shields.io/badge/Tests-119_Passing-success?style=for-the-badge">
  <img src="https://img.shields.io/badge/Responsive-Mobile_First-orange?style=for-the-badge">
</p>

---

## Experience

<p align="center">

```mermaid
graph LR

A[Customer]
B[Product Discovery]
C[Cart & Wishlist]
D[Checkout]
E[Orders]
F[NEXUS Academy]
G[Admin Panel]

A --> B
B --> C
C --> D
D --> E
A --> F
G --> B
G --> E
G --> F
```

</p>

---

## Overview

NEXUS Store is a full-stack Django commerce platform combining shopping, editorial content, customer accounts, and administration tools inside a unified ecosystem.

It delivers a premium shopping experience with modern UI patterns, scalable architecture, and production-ready workflows.

---

## Highlights

| Feature           | Included |
| ----------------- | -------- |
| Product Catalog   | ✅        |
| Cart Persistence  | ✅        |
| Wishlist          | ✅        |
| User Accounts     | ✅        |
| Reviews & Ratings | ✅        |
| Order History     | ✅        |
| Academy Blog      | ✅        |
| Search & Filters  | ✅        |
| Admin Dashboard   | ✅        |
| SEO Meta Tags     | ✅        |
| Responsive Design | ✅        |
| Automated Tests   | ✅        |

---

# Features

<table>
<tr>
<td width="50%">

### 🛍 Commerce

* Product catalog
* Product galleries
* Deals of the Day
* Search
* Sorting
* Filtering
* Cart system
* Wishlist

</td>
<td width="50%">

### 👤 Customer

* Authentication
* Profiles
* Order history
* Reviews
* Ratings
* Review moderation

</td>
</tr>

<tr>
<td>

### 📰 Academy

* Buying guides
* Product reviews
* Editorial articles
* Content management

</td>

<td>

### ⚙ Administration

* Product management
* Image uploads
* Order management
* Review approval
* Employee dashboard

</td>
</tr>
</table>

---

# Technology Stack

| Layer          | Technology              |
| -------------- | ----------------------- |
| Backend        | Django                  |
| Language       | Python                  |
| Database       | SQLite / PostgreSQL     |
| Frontend       | HTML · CSS · JavaScript |
| Authentication | Django Auth             |
| Testing        | Django Test Framework   |
| Deployment     | Gunicorn · Nginx        |

---

# System Architecture

```mermaid
flowchart TD

User --> Frontend

Frontend --> Products
Frontend --> Accounts
Frontend --> Cart
Frontend --> Orders
Frontend --> Academy

Products --> Database
Accounts --> Database
Orders --> Database
Academy --> Database

Admin --> Products
Admin --> Orders
Admin --> Reviews
```

---

# Product Dataset

| Category    | Products |
| ----------- | -------: |
| Smartphones |       10 |
| Laptops     |       10 |
| Cameras     |       10 |
| **Total**   |   **30** |

Each product includes:

* Multiple images
* Ratings
* Reviews
* Pricing
* Discounts
* Categories

---

# Screens

| Home              | Products  | Academy       |
| ----------------- | --------- | ------------- |
| Hero Banner       | Filtering | Articles      |
| Featured Products | Search    | Buying Guides |
| Trust Section     | Sorting   | Reviews       |

---

# Project Structure

```text
nexus_store/
│
├── accounts/
├── academy/
├── store/
├── orders/
├── static/
├── templates/
├── media/
├── tests/
│
├── manage.py
└── requirements.txt
```

---

# Quick Start

```bash
pip install -r requirements.txt

python manage.py migrate

python manage.py seed_data

python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000
```

---

# Demo Accounts

| Role  | Username | Password |
| ----- | -------- | -------- |
| Admin | admin    | admin123 |
| Demo  | demo     | demo123  |

Admin panel:

```text
http://127.0.0.1:8000/admin
```

---

# Application Flow

```mermaid
sequenceDiagram

User->>Store: Browse products
Store->>Cart: Add items
Cart->>Checkout: Submit order
Checkout->>Orders: Create order
Orders->>Profile: Order history
```

---

# Testing

```bash
python manage.py test
```

### Test Status

| Tests | Status    |
| ----: | --------- |
|   119 | ✅ Passing |

---

# Production Checklist

| Task               | Status |
| ------------------ | ------ |
| DEBUG=False        | ⬜      |
| PostgreSQL         | ⬜      |
| Stripe Integration | ⬜      |
| PayPal Integration | ⬜      |
| Email Service      | ⬜      |
| collectstatic      | ⬜      |
| Gunicorn           | ⬜      |
| Nginx              | ⬜      |
| HTTPS              | ⬜      |

---

# Design Principles

| Principle | Description             |
| --------- | ----------------------- |
| Discover  | Fast product discovery  |
| Decide    | Trusted information     |
| Purchase  | Seamless checkout       |
| Scale     | Production architecture |

---

# Roadmap

```mermaid
timeline

title Future Development

2025 : Stripe Integration
     : PayPal Support

2026 : AI Recommendations
     : Analytics Dashboard

2027 : Inventory Management
     : Marketing Automation
```

---

# Deployment

```bash
python manage.py collectstatic

gunicorn nexus.wsgi

nginx
```

Supported platforms:

* Railway
* Render
* DigitalOcean
* AWS
* Heroku

---

# Repository Assets

```text
assets/
│
├── banner.png
├── thumbnail.png
├── homepage.png
├── products.png
├── academy.png
├── architecture.svg
└── workflow.svg
```

---

<p align="center">

### Built with Django. Designed like a product.

</p>
