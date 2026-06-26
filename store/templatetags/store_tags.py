from django import template

register = template.Library()

@register.simple_tag
def product_img_url(product, fallback=''):
    """Return the primary image URL for a product, or fallback."""
    try:
        img = product.primary_image
        if img and img.image and img.image.name:
            return img.image.url
    except Exception:
        pass
    return fallback

@register.simple_tag
def img_url(image_obj, fallback=''):
    """Safely return URL from any ImageField object."""
    try:
        if image_obj and image_obj.name:
            return image_obj.url
    except Exception:
        pass
    return fallback

@register.filter
def safe_img_url(image_obj):
    """Filter version: {{ item.image|safe_img_url }}"""
    try:
        if image_obj and image_obj.name:
            return image_obj.url
    except Exception:
        pass
    return ''

@register.filter
def star_range(rating):
    """Return list for star rendering."""
    rating = int(rating or 0)
    return range(1, 6)

@register.simple_tag
def rating_stars(rating, max_stars=5):
    filled = int(round(float(rating or 0)))
    return {'filled': range(filled), 'empty': range(max_stars - filled)}
