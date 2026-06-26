from .models import Cart, Category, Wishlist


def cart_context(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.total_items
    elif request.session.session_key:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()
        if cart:
            cart_count = cart.total_items
    return {'cart_count': cart_count}


def categories_context(request):
    categories = Category.objects.filter(is_active=True)
    return {'nav_categories': categories}
