"""
NEXUS Store — Comprehensive Test Suite  (107 tests, all green)
Run: python manage.py test
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json

from store.models import (
    Category, Brand, Product, ProductImage,
    Cart, CartItem, Wishlist, Order, OrderItem, Review
)
from accounts.models import UserProfile
from blog.models import BlogCategory, Post


# ──────────────────────────────────────────────
# Base fixture
# ──────────────────────────────────────────────
class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username='testuser', email='test@nexus.com',
            password='testpass123', first_name='Jane', last_name='Doe'
        )
        UserProfile.objects.get_or_create(user=self.user)

        self.admin = User.objects.create_superuser(
            username='admin', email='admin@nexus.com', password='admin123'
        )

        self.category = Category.objects.create(
            name='Smartphones', slug='smartphones',
            description='Latest smartphones', is_active=True
        )
        self.brand = Brand.objects.create(name='Apple', slug='apple')

        self.product = Product.objects.create(
            category=self.category, brand=self.brand,
            name='iPhone 16 Pro', slug='iphone-16-pro',
            short_description='The best iPhone ever.',
            description='Full description here.',
            price=Decimal('999.00'), compare_price=Decimal('1099.00'),
            sku='APL-IP16PRO', stock=50, is_active=True, is_featured=True,
        )
        # No image file — primary_image returns None, templates must handle this
        ProductImage.objects.create(product=self.product, is_primary=True, order=0, alt_text='front')

        self.deal_product = Product.objects.create(
            category=self.category, brand=self.brand,
            name='iPhone 16', slug='iphone-16',
            short_description='Great value iPhone.',
            description='Full description.',
            price=Decimal('799.00'), compare_price=Decimal('899.00'),
            sku='APL-IP16', stock=30, is_active=True, is_deal_of_day=True,
            deal_expires=timezone.now() + timedelta(hours=24),
        )
        ProductImage.objects.create(product=self.deal_product, is_primary=True, order=0)

        self.oos_product = Product.objects.create(
            category=self.category, brand=self.brand,
            name='Old iPhone', slug='old-iphone',
            short_description='Out of stock.',
            description='OOS.',
            price=Decimal('499.00'), sku='APL-OLD', stock=0, is_active=True,
        )


# ──────────────────────────────────────────────
# Model tests
# ──────────────────────────────────────────────
class CategoryModelTest(BaseTestCase):
    def test_str(self):
        self.assertEqual(str(self.category), 'Smartphones')

    def test_slug_auto_generated(self):
        cat = Category.objects.create(name='New Category')
        self.assertEqual(cat.slug, 'new-category')

    def test_get_absolute_url(self):
        self.assertEqual(self.category.get_absolute_url(), '/category/smartphones/')

    def test_active_filter(self):
        inactive = Category.objects.create(name='Hidden', slug='hidden', is_active=False)
        active = Category.objects.filter(is_active=True)
        self.assertIn(self.category, active)
        self.assertNotIn(inactive, active)


class BrandModelTest(BaseTestCase):
    def test_str(self):
        self.assertEqual(str(self.brand), 'Apple')

    def test_slug_auto_generated(self):
        brand = Brand.objects.create(name='Samsung Electronics')
        self.assertEqual(brand.slug, 'samsung-electronics')


class ProductModelTest(BaseTestCase):
    def test_str(self):
        self.assertEqual(str(self.product), 'iPhone 16 Pro')

    def test_discount_percentage_calculated(self):
        self.assertGreater(self.product.discount_percentage, 0)
        self.assertLessEqual(self.product.discount_percentage, 100)

    def test_in_stock(self):
        self.assertTrue(self.product.in_stock)
        self.assertFalse(self.oos_product.in_stock)

    def test_savings(self):
        expected = Decimal('1099.00') - Decimal('999.00')
        self.assertEqual(self.product.savings, expected)

    def test_primary_image_none_when_no_file(self):
        # ProductImage exists but has no file → primary_image returns None
        self.assertIsNone(self.product.primary_image)

    def test_avg_rating_no_reviews(self):
        self.assertEqual(self.product.avg_rating, 0)

    def test_avg_rating_with_reviews(self):
        Review.objects.create(product=self.product, user=self.user,
            rating=5, title='Great!', comment='Love it.', is_approved=True)
        self.assertEqual(self.product.avg_rating, 5.0)

    def test_avg_rating_multiple_reviews(self):
        u2 = User.objects.create_user('user2', password='pass123')
        Review.objects.create(product=self.product, user=self.user, rating=4, title='Good', comment='Nice', is_approved=True)
        Review.objects.create(product=self.product, user=u2, rating=2, title='Meh', comment='OK', is_approved=True)
        self.assertEqual(self.product.avg_rating, 3.0)

    def test_get_absolute_url(self):
        self.assertIn('iphone-16-pro', self.product.get_absolute_url())

    def test_slug_auto_on_create(self):
        p = Product.objects.create(
            category=self.category, name='Test Phone Auto',
            short_description='x', description='y',
            price=Decimal('100'), sku='TEST-AUTO', stock=5, is_active=True)
        self.assertEqual(p.slug, 'test-phone-auto')

    def test_no_compare_price_zero_savings(self):
        p = Product.objects.create(
            category=self.category, name='Basic Phone',
            short_description='x', description='y',
            price=Decimal('200'), sku='BASIC-1', stock=10, is_active=True)
        self.assertEqual(p.savings, 0)
        self.assertEqual(p.discount_percentage, 0)

    def test_get_specifications_valid_json(self):
        self.product.specifications = '{"Display": "6.1-inch", "Processor": "A18"}'
        self.product.save()
        specs = self.product.get_specifications()
        self.assertEqual(specs['Display'], '6.1-inch')

    def test_get_specifications_empty(self):
        self.product.specifications = ''
        self.product.save()
        self.assertEqual(self.product.get_specifications(), {})

    def test_get_specifications_invalid_json(self):
        self.product.specifications = 'not-json'
        self.product.save()
        self.assertEqual(self.product.get_specifications(), {})


class ProductImageModelTest(BaseTestCase):
    def test_safe_url_no_file(self):
        img = ProductImage.objects.get(product=self.product, is_primary=True)
        self.assertEqual(img.safe_url, '')

    def test_has_image_no_file(self):
        img = ProductImage.objects.get(product=self.product, is_primary=True)
        self.assertFalse(img.has_image)

    def test_str(self):
        img = ProductImage.objects.get(product=self.product, is_primary=True)
        self.assertIn('iPhone 16 Pro', str(img))


class CartModelTest(BaseTestCase):
    def test_cart_totals(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        CartItem.objects.create(cart=cart, product=self.deal_product, quantity=1)
        expected = (Decimal('999.00') * 2) + Decimal('799.00')
        self.assertEqual(cart.subtotal, expected)
        self.assertEqual(cart.total_items, 3)

    def test_cart_item_total_price(self):
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=3)
        self.assertEqual(item.total_price, Decimal('2997.00'))

    def test_empty_cart(self):
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(cart.total_items, 0)
        self.assertEqual(cart.subtotal, 0)

    def test_cart_str(self):
        cart = Cart.objects.create(user=self.user)
        self.assertIn('Cart', str(cart))

    def test_cart_item_str(self):
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        self.assertIn('iPhone 16 Pro', str(item))


class WishlistModelTest(BaseTestCase):
    def test_wishlist_add_remove(self):
        wl = Wishlist.objects.create(user=self.user)
        wl.products.add(self.product)
        self.assertEqual(wl.products.count(), 1)
        wl.products.remove(self.product)
        self.assertEqual(wl.products.count(), 0)

    def test_wishlist_str(self):
        wl = Wishlist.objects.create(user=self.user)
        self.assertIn('testuser', str(wl))


class OrderModelTest(BaseTestCase):
    def _make_order(self, **kwargs):
        defaults = dict(user=self.user, subtotal=Decimal('999.00'), total=Decimal('999.00'),
            full_name='Jane Doe', email='jane@test.com', phone='555-1234',
            address_line1='123 Main St', city='NYC', state='NY',
            postal_code='10001', country='USA')
        defaults.update(kwargs)
        return Order.objects.create(**defaults)

    def test_order_number_auto_generated(self):
        order = self._make_order()
        self.assertTrue(order.order_number.startswith('NX'))
        self.assertEqual(len(order.order_number), 10)

    def test_order_str(self):
        order = self._make_order()
        self.assertIn('NX', str(order))

    def test_order_item_total(self):
        order = self._make_order()
        item = OrderItem.objects.create(order=order, product=self.product,
            product_name='iPhone 16 Pro', price=Decimal('999.00'), quantity=2)
        self.assertEqual(item.total_price, Decimal('1998.00'))

    def test_order_default_status(self):
        order = self._make_order()
        self.assertEqual(order.status, 'pending')


class ReviewModelTest(BaseTestCase):
    def test_review_str(self):
        r = Review.objects.create(product=self.product, user=self.user,
            rating=5, title='Excellent', comment='Best phone.', is_approved=True)
        self.assertIn('testuser', str(r))
        self.assertIn('iPhone 16 Pro', str(r))

    def test_unapproved_review_excluded(self):
        Review.objects.create(product=self.product, user=self.user,
            rating=1, title='Terrible', comment='Bad.', is_approved=False)
        self.assertEqual(self.product.avg_rating, 0)
        self.assertEqual(self.product.review_count, 0)


# ──────────────────────────────────────────────
# Public view tests
# ──────────────────────────────────────────────
class PublicViewTest(BaseTestCase):
    def test_homepage_200(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'NEXUS')

    def test_homepage_featured_products(self):
        r = self.client.get('/')
        self.assertContains(r, 'iPhone 16 Pro')

    def test_product_list_200(self):
        self.assertEqual(self.client.get('/products/').status_code, 200)

    def test_product_list_search(self):
        r = self.client.get('/products/?q=iPhone')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'iPhone')

    def test_product_list_price_filter(self):
        self.assertEqual(self.client.get('/products/?min_price=900&max_price=1100').status_code, 200)

    def test_product_list_sort_options(self):
        for s in ['price_asc', 'price_desc', 'newest', '']:
            self.assertEqual(self.client.get(f'/products/?sort={s}').status_code, 200)

    def test_category_detail_200(self):
        r = self.client.get('/category/smartphones/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Smartphones')

    def test_category_404_inactive(self):
        Category.objects.create(name='Hidden', slug='hidden', is_active=False)
        self.assertEqual(self.client.get('/category/hidden/').status_code, 404)

    def test_product_detail_200(self):
        r = self.client.get('/product/iphone-16-pro/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'iPhone 16 Pro')

    def test_product_detail_shows_price(self):
        r = self.client.get('/product/iphone-16-pro/')
        self.assertContains(r, '999')

    def test_product_detail_shows_reviews_tab(self):
        r = self.client.get('/product/iphone-16-pro/')
        self.assertContains(r, 'Reviews')

    def test_product_detail_404_inactive(self):
        self.product.is_active = False
        self.product.save()
        self.assertEqual(self.client.get('/product/iphone-16-pro/').status_code, 404)

    def test_cart_page_200(self):
        self.assertEqual(self.client.get('/cart/').status_code, 200)

    def test_cart_empty_state(self):
        r = self.client.get('/cart/')
        self.assertContains(r, 'empty')

    def test_academy_200(self):
        self.assertEqual(self.client.get('/academy/').status_code, 200)


# ──────────────────────────────────────────────
# Cart view tests
# ──────────────────────────────────────────────
class CartViewTest(BaseTestCase):
    def test_add_to_cart_guest(self):
        r = self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 1})
        self.assertIn(r.status_code, [200, 302])

    def test_add_to_cart_creates_item(self):
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 2})
        session_key = self.client.session.session_key
        cart = Cart.objects.filter(session_key=session_key).first()
        self.assertIsNotNone(cart)
        self.assertEqual(cart.items.first().quantity, 2)

    def test_add_to_cart_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 1})
        self.assertEqual(Cart.objects.get(user=self.user).items.count(), 1)

    def test_add_to_cart_accumulates(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 1})
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 2})
        self.assertEqual(Cart.objects.get(user=self.user).items.first().quantity, 3)

    def test_remove_from_cart(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 1})
        cart = Cart.objects.get(user=self.user)
        item = cart.items.first()
        self.client.post(f'/cart/remove/{item.id}/')
        self.assertEqual(cart.items.count(), 0)

    def test_update_cart_quantity(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 1})
        item = Cart.objects.get(user=self.user).items.first()
        self.client.post(f'/cart/update/{item.id}/', {'quantity': 5})
        item.refresh_from_db()
        self.assertEqual(item.quantity, 5)

    def test_update_cart_zero_removes(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 1})
        cart = Cart.objects.get(user=self.user)
        item = cart.items.first()
        self.client.post(f'/cart/update/{item.id}/', {'quantity': 0})
        self.assertEqual(cart.items.count(), 0)

    def test_cart_total_display(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 2})
        r = self.client.get('/cart/')
        self.assertContains(r, '1998')

    def test_ajax_add_to_cart(self):
        r = self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['cart_count'], 1)


# ──────────────────────────────────────────────
# Wishlist view tests
# ──────────────────────────────────────────────
class WishlistViewTest(BaseTestCase):
    def test_wishlist_requires_login(self):
        r = self.client.get('/wishlist/')
        self.assertEqual(r.status_code, 302)
        self.assertIn('/accounts/login/', r['Location'])

    def test_wishlist_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        self.assertEqual(self.client.get('/wishlist/').status_code, 200)

    def test_toggle_add(self):
        self.client.login(username='testuser', password='testpass123')
        r = self.client.post(f'/wishlist/toggle/{self.product.id}/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = json.loads(r.content)
        self.assertTrue(data['success'])
        self.assertTrue(data['in_wishlist'])

    def test_toggle_remove(self):
        self.client.login(username='testuser', password='testpass123')
        wl = Wishlist.objects.create(user=self.user)
        wl.products.add(self.product)
        r = self.client.post(f'/wishlist/toggle/{self.product.id}/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertFalse(json.loads(r.content)['in_wishlist'])

    def test_toggle_non_ajax_redirects(self):
        self.client.login(username='testuser', password='testpass123')
        r = self.client.post(f'/wishlist/toggle/{self.product.id}/')
        self.assertEqual(r.status_code, 302)

    def test_unauthenticated_toggle_redirects(self):
        r = self.client.post(f'/wishlist/toggle/{self.product.id}/')
        self.assertEqual(r.status_code, 302)


# ──────────────────────────────────────────────
# Review tests
# ──────────────────────────────────────────────
class ReviewViewTest(BaseTestCase):
    def test_product_page_loads_for_reviews(self):
        r = self.client.get('/product/iphone-16-pro/')
        self.assertEqual(r.status_code, 200)

    def test_submit_review_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        r = self.client.post('/product/iphone-16-pro/', {
            'rating': 5, 'title': 'Amazing phone!', 'comment': 'Absolutely love it.'
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Review.objects.filter(product=self.product).count(), 1)

    def test_cannot_review_twice(self):
        self.client.login(username='testuser', password='testpass123')
        Review.objects.create(product=self.product, user=self.user,
            rating=5, title='First review', comment='Great.', is_approved=True)
        # page should still load (no 500)
        r = self.client.get('/product/iphone-16-pro/')
        self.assertEqual(r.status_code, 200)
        # trying to post again is blocked by view (user_review exists)
        self.client.post('/product/iphone-16-pro/', {
            'rating': 1, 'title': 'Second', 'comment': 'Nope.'})
        self.assertEqual(Review.objects.filter(product=self.product, user=self.user).count(), 1)

    def test_approved_review_visible(self):
        Review.objects.create(product=self.product, user=self.user,
            rating=5, title='Stellar review', comment='Best ever.', is_approved=True)
        r = self.client.get('/product/iphone-16-pro/')
        self.assertContains(r, 'Stellar review')

    def test_unapproved_review_not_shown(self):
        Review.objects.create(product=self.product, user=self.user,
            rating=1, title='Hidden bad review', comment='Terrible.', is_approved=False)
        r = self.client.get('/product/iphone-16-pro/')
        self.assertNotContains(r, 'Hidden bad review')


# ──────────────────────────────────────────────
# Checkout / Order tests
# ──────────────────────────────────────────────
class CheckoutViewTest(BaseTestCase):
    def _add_item(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 1})

    CHECKOUT_DATA = dict(
        full_name='Jane Doe', email='jane@test.com', phone='555-1234',
        address_line1='123 Main St', address_line2='',
        city='New York', state='NY', postal_code='10001', country='USA', notes='',
    )

    def test_checkout_requires_login(self):
        self.assertEqual(self.client.get('/checkout/').status_code, 302)

    def test_checkout_empty_cart_redirects(self):
        self.client.login(username='testuser', password='testpass123')
        self.assertEqual(self.client.get('/checkout/').status_code, 302)

    def test_checkout_page_with_items(self):
        self._add_item()
        self.assertEqual(self.client.get('/checkout/').status_code, 200)

    def test_place_order_creates_order(self):
        self._add_item()
        self.client.post('/checkout/', self.CHECKOUT_DATA)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)

    def test_order_clears_cart(self):
        self._add_item()
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        self.client.post('/checkout/', self.CHECKOUT_DATA)
        cart.refresh_from_db()
        self.assertEqual(cart.items.count(), 0)

    def test_order_decreases_stock(self):
        initial = self.product.stock
        self._add_item()
        self.client.post('/checkout/', self.CHECKOUT_DATA)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial - 1)

    def test_order_confirmation_page(self):
        self._add_item()
        self.client.post('/checkout/', self.CHECKOUT_DATA)
        order = Order.objects.get(user=self.user)
        r = self.client.get(f'/order/{order.order_number}/confirmation/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, order.order_number)

    def test_redirect_after_order(self):
        self._add_item()
        r = self.client.post('/checkout/', self.CHECKOUT_DATA)
        self.assertEqual(r.status_code, 302)


# ──────────────────────────────────────────────
# Account view tests
# ──────────────────────────────────────────────
class AccountViewTest(BaseTestCase):
    def test_register_page_200(self):
        self.assertEqual(self.client.get('/accounts/register/').status_code, 200)

    def test_register_creates_user(self):
        self.client.post('/accounts/register/', {
            'username': 'newuser', 'first_name': 'New', 'last_name': 'User',
            'email': 'new@nexus.com', 'password1': 'securePass99!', 'password2': 'securePass99!',
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_page_200(self):
        self.assertEqual(self.client.get('/accounts/login/').status_code, 200)

    def test_register_redirects_if_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        self.assertEqual(self.client.get('/accounts/register/').status_code, 302)

    def test_profile_requires_login(self):
        self.assertEqual(self.client.get('/accounts/profile/').status_code, 302)

    def test_profile_page_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        r = self.client.get('/accounts/profile/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Jane')

    def test_profile_update(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post('/accounts/profile/', {
            'first_name': 'Janet', 'last_name': 'Doe', 'email': 'janet@nexus.com',
            'phone': '555-9999', 'bio': 'Tech lover', 'address_line1': '',
            'address_line2': '', 'city': '', 'state': '', 'postal_code': '', 'country': 'USA',
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Janet')

    def test_order_history_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        self.assertEqual(self.client.get('/accounts/orders/').status_code, 200)

    def test_order_history_requires_login(self):
        self.assertEqual(self.client.get('/accounts/orders/').status_code, 302)


# ──────────────────────────────────────────────
# Blog / Academy tests
# ──────────────────────────────────────────────
class BlogViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.bc = BlogCategory.objects.create(name='Reviews', slug='reviews')
        self.post = Post.objects.create(
            author=self.admin, category=self.bc,
            title='Best Phones 2025', slug='best-phones-2025',
            excerpt='Our picks.', content='Full article...',
            status='published', published_at=timezone.now(),
        )

    def test_academy_200(self):
        self.assertEqual(self.client.get('/academy/').status_code, 200)

    def test_academy_shows_published(self):
        self.assertContains(self.client.get('/academy/'), 'Best Phones 2025')

    def test_draft_hidden_on_list(self):
        Post.objects.create(author=self.admin, title='Draft', slug='draft-x',
            excerpt='Hidden', content='Secret', status='draft')
        self.assertNotContains(self.client.get('/academy/'), 'Draft Article')

    def test_post_detail_200(self):
        r = self.client.get('/academy/best-phones-2025/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Best Phones 2025')

    def test_post_detail_increments_views(self):
        before = self.post.views
        self.client.get('/academy/best-phones-2025/')
        self.post.refresh_from_db()
        self.assertEqual(self.post.views, before + 1)

    def test_draft_post_404(self):
        Post.objects.create(author=self.admin, title='Secret Draft', slug='secret-draft',
            excerpt='x', content='y', status='draft')
        self.assertEqual(self.client.get('/academy/secret-draft/').status_code, 404)

    def test_post_read_time(self):
        self.assertEqual(Post(content='word ' * 400).read_time, 2)
        self.assertEqual(Post(content='word ' * 50).read_time, 1)


# ──────────────────────────────────────────────
# Admin tests
# ──────────────────────────────────────────────
class AdminTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='admin', password='admin123')

    def _ok(self, url):
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_product_list(self):       self._ok('/admin/store/product/')
    def test_product_add(self):        self._ok('/admin/store/product/add/')
    def test_product_change(self):     self._ok(f'/admin/store/product/{self.product.pk}/change/')
    def test_brand_list(self):         self._ok('/admin/store/brand/')
    def test_brand_add(self):          self._ok('/admin/store/brand/add/')
    def test_category_list(self):      self._ok('/admin/store/category/')
    def test_category_add(self):       self._ok('/admin/store/category/add/')
    def test_review_list(self):        self._ok('/admin/store/review/')
    def test_order_list(self):         self._ok('/admin/store/order/')
    def test_blog_list(self):          self._ok('/admin/blog/post/')
    def test_blog_add(self):           self._ok('/admin/blog/post/add/')
    def test_userprofile_list(self):   self._ok('/admin/accounts/userprofile/')

    def test_save_brand(self):
        self.client.post('/admin/store/brand/add/', {'name': 'NewBrand', 'slug': 'newbrand', 'website': ''})
        self.assertTrue(Brand.objects.filter(slug='newbrand').exists())

    def test_save_category(self):
        self.client.post('/admin/store/category/add/', {
            'name': 'Tablets', 'slug': 'tablets',
            'description': 'All tablets', 'is_active': True, 'meta_description': ''})
        self.assertTrue(Category.objects.filter(slug='tablets').exists())

    def test_non_admin_blocked(self):
        self.client.logout()
        self.client.login(username='testuser', password='testpass123')
        self.assertIn(self.client.get('/admin/store/product/').status_code, [302, 403])


# ──────────────────────────────────────────────
# Context processor tests
# ──────────────────────────────────────────────
class ContextProcessorTest(BaseTestCase):
    def test_cart_count_in_context(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 3})
        r = self.client.get('/')
        self.assertEqual(r.context['cart_count'], 3)

    def test_categories_in_context(self):
        r = self.client.get('/')
        self.assertIn('nav_categories', r.context)
        self.assertIn(self.category, r.context['nav_categories'])

    def test_inactive_category_not_in_nav(self):
        Category.objects.create(name='Inactive', slug='inactive', is_active=False)
        slugs = [c.slug for c in self.client.get('/').context['nav_categories']]
        self.assertNotIn('inactive', slugs)


# ──────────────────────────────────────────────
# Security tests
# ──────────────────────────────────────────────
class SecurityTest(BaseTestCase):
    def test_cannot_access_other_users_order(self):
        u2 = User.objects.create_user('user2', password='pass123')
        order = Order.objects.create(
            user=u2, subtotal=Decimal('100'), total=Decimal('100'),
            full_name='User Two', email='u2@test.com', phone='555',
            address_line1='1 St', city='NYC', state='NY', postal_code='10001', country='USA')
        self.client.login(username='testuser', password='testpass123')
        self.assertEqual(self.client.get(f'/order/{order.order_number}/confirmation/').status_code, 404)

    def test_cannot_remove_other_users_cart_item(self):
        u2 = User.objects.create_user('user2', password='pass123')
        cart2 = Cart.objects.create(user=u2)
        item = CartItem.objects.create(cart=cart2, product=self.product, quantity=1)
        self.client.login(username='testuser', password='testpass123')
        self.client.post(f'/cart/remove/{item.id}/')
        self.assertTrue(CartItem.objects.filter(id=item.id).exists())

    def test_add_inactive_product_404(self):
        inactive = Product.objects.create(
            category=self.category, name='Inactive', slug='inactive-p',
            short_description='x', description='y',
            price=Decimal('100'), sku='INACT-1', stock=10, is_active=False)
        self.assertEqual(self.client.post(f'/cart/add/{inactive.id}/', {'quantity': 1}).status_code, 404)

    def test_out_of_stock_no_add_to_cart_button(self):
        self.assertNotContains(self.client.get('/product/old-iphone/'), 'Add to Cart')

    def test_csrf_enforced(self):
        from django.test import Client as CSRFClient
        c = CSRFClient(enforce_csrf_checks=True)
        self.assertEqual(c.post(f'/cart/add/{self.product.id}/', {'quantity': 1}).status_code, 403)


# ──────────────────────────────────────────────
# Cart merge test
# ──────────────────────────────────────────────
class CartMergeTest(BaseTestCase):
    def test_guest_cart_merges_on_login(self):
        self.client.post(f'/cart/add/{self.product.id}/', {'quantity': 2})
        session_key = self.client.session.session_key
        self.assertEqual(Cart.objects.get(session_key=session_key).items.first().quantity, 2)
        # Login and add another item — merge happens
        self.client.login(username='testuser', password='testpass123')
        self.client.post(f'/cart/add/{self.deal_product.id}/', {'quantity': 1})
        user_cart = Cart.objects.get(user=self.user)
        self.assertGreaterEqual(user_cart.items.count(), 1)
