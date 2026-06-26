from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Product, Category, Cart, CartItem, Wishlist, Order, OrderItem, Review, Brand
from .forms import ReviewForm, CheckoutForm, ProductSearchForm


def home(request):
    featured = Product.objects.filter(is_active=True, is_featured=True).prefetch_related('images')[:8]
    deals = Product.objects.filter(is_active=True, is_deal_of_day=True).prefetch_related('images')[:4]
    categories = Category.objects.filter(is_active=True)
    phones = Product.objects.filter(is_active=True, category__slug='smartphones').prefetch_related('images')[:6]
    laptops = Product.objects.filter(is_active=True, category__slug='laptops').prefetch_related('images')[:6]
    cameras = Product.objects.filter(is_active=True, category__slug='cameras').prefetch_related('images')[:6]
    return render(request, 'store/home.html', {
        'featured_products': featured,
        'deal_products': deals,
        'categories': categories,
        'phones': phones,
        'laptops': laptops,
        'cameras': cameras,
    })


def product_list(request):
    form = ProductSearchForm(request.GET)
    products = Product.objects.filter(is_active=True).prefetch_related('images', 'brand', 'category')
    category = None

    if form.is_valid():
        q = form.cleaned_data.get('q')
        cat_slug = form.cleaned_data.get('category') or request.GET.get('category', '')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        sort = form.cleaned_data.get('sort') or request.GET.get('sort', '')

        if q:
            products = products.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(brand__name__icontains=q))
        if cat_slug:
            category = Category.objects.filter(slug=cat_slug).first()
            if category:
                products = products.filter(category=category)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        if sort == 'price_asc':
            products = products.order_by('price')
        elif sort == 'price_desc':
            products = products.order_by('-price')
        elif sort == 'newest':
            products = products.order_by('-created_at')
        else:
            products = products.order_by('-is_featured', '-created_at')

    paginator = Paginator(products, 12)
    products_page = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.filter(is_active=True)

    return render(request, 'store/product_list.html', {
        'products': products_page,
        'form': form,
        'categories': categories,
        'current_category': category,
        'total_count': paginator.count,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(is_active=True, category=category).prefetch_related('images', 'brand')
    sort = request.GET.get('sort', '')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')

    paginator = Paginator(products, 12)
    return render(request, 'store/category_detail.html', {
        'category': category,
        'products': paginator.get_page(request.GET.get('page')),
        'sort': sort,
        'total_count': paginator.count,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    images = product.images.all()
    reviews = product.reviews.filter(is_approved=True).select_related('user')
    related = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id).prefetch_related('images')[:4]

    review_form = ReviewForm()
    user_review = None
    in_wishlist = False

    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        wl = Wishlist.objects.filter(user=request.user).first()
        if wl:
            in_wishlist = wl.products.filter(id=product.id).exists()

        if request.method == 'POST' and not user_review:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                r = review_form.save(commit=False)
                r.product = product
                r.user = request.user
                r.save()
                messages.success(request, 'Review submitted!')
                return redirect('store:product_detail', slug=slug)

    # Rating breakdown
    rating_counts = {i: reviews.filter(rating=i).count() for i in range(1, 6)}
    specs = product.get_specifications()

    return render(request, 'store/product_detail.html', {
        'product': product,
        'images': images,
        'reviews': reviews,
        'related_products': related,
        'review_form': review_form,
        'user_review': user_review,
        'in_wishlist': in_wishlist,
        'rating_counts': rating_counts,
        'specs': specs,
    })


def cart_detail(request):
    cart = _get_or_create_cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = _get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
    item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.total_items,
                             'message': f'"{product.name}" added to cart'})
    messages.success(request, f'"{product.name}" added to your cart!')
    return redirect(request.META.get('HTTP_REFERER', 'store:cart'))


def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    cart = _get_or_create_cart(request)
    if item.cart == cart:
        item.delete()
        messages.success(request, 'Item removed.')
    return redirect('store:cart')


def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    cart = _get_or_create_cart(request)
    if item.cart == cart:
        qty = int(request.POST.get('quantity', 1))
        if qty > 0:
            item.quantity = qty
            item.save()
        else:
            item.delete()
    return redirect('store:cart')


@login_required
def checkout(request):
    cart = _get_or_create_cart(request)
    if not cart.items.exists():
        return redirect('store:cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.subtotal = cart.subtotal
            order.total = cart.total
            order.save()
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order, product=item.product,
                    product_name=item.product.name,
                    price=item.product.price, quantity=item.quantity,
                )
                item.product.stock = max(0, item.product.stock - item.quantity)
                item.product.save(update_fields=['stock'])
            cart.items.all().delete()
            messages.success(request, f'Order #{order.order_number} placed successfully!')
            return redirect('store:order_confirmation', order_number=order.order_number)
    else:
        initial = {'full_name': request.user.get_full_name(), 'email': request.user.email}
        form = CheckoutForm(initial=initial)

    return render(request, 'store/checkout.html', {'cart': cart, 'form': form})


@login_required
def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'store/order_confirmation.html', {'order': order})


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    if wishlist.products.filter(id=product_id).exists():
        wishlist.products.remove(product)
        in_wishlist, msg = False, 'Removed from wishlist'
    else:
        wishlist.products.add(product)
        in_wishlist, msg = True, 'Added to wishlist'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'in_wishlist': in_wishlist, 'message': msg})
    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def wishlist(request):
    wl, _ = Wishlist.objects.get_or_create(user=request.user)
    products = wl.products.filter(is_active=True).prefetch_related('images', 'brand')
    return render(request, 'store/wishlist.html', {'products': products})


def _get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Merge anonymous cart on login
        if request.session.session_key:
            session_cart = Cart.objects.filter(
                session_key=request.session.session_key, user__isnull=True
            ).first()
            if session_cart and session_cart.id != cart.id:
                for item in session_cart.items.all():
                    ci, created = CartItem.objects.get_or_create(cart=cart, product=item.product)
                    if not created:
                        ci.quantity += item.quantity
                        ci.save()
                session_cart.delete()
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(
            session_key=request.session.session_key, user__isnull=True
        )
        return cart
