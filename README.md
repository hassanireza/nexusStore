# NEXUS Store — Production-Ready Django E-Commerce

## Quick Start (3 commands)

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Visit **http://127.0.0.1:8000**

## Credentials
| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | `admin`  | `admin123`|
| Demo  | `demo`   | `demo123` |

Admin panel: **http://127.0.0.1:8000/admin**

## Features
- 30 products: 10 smartphones · 10 laptops · 10 cameras (5 images each)
- Cart (guest + authenticated, auto-merges on login)
- Wishlist / Save for later
- User registration, profiles, order history
- Product reviews + star ratings
- Deals of the Day with live countdown timers
- Search, filter by category/price, sort
- Full checkout → order confirmation flow
- Academy blog (add articles via admin)
- Employee admin panel (add products + images inline, manage orders, approve reviews)
- SEO meta tags on every page
- Mobile-first responsive design

## Run Tests
```bash
python manage.py test          # 119 tests, all pass
```

## Add Real Product Images
Go to `/admin/store/product/` → click a product → upload images in the **Images** section.

## Production Checklist
- [ ] Set `DEBUG = False` and real `SECRET_KEY` via env vars
- [ ] Switch to PostgreSQL
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Add Stripe/PayPal payment integration
- [ ] Set up email backend (SendGrid / SES)
- [ ] Upload real product images
- [ ] Run `python manage.py collectstatic`
- [ ] Deploy with gunicorn + nginx (or Railway/Render/Heroku)
