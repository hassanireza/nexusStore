from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Brand, Product, ProductImage,
    Review, Cart, CartItem, Order, OrderItem, Wishlist
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order', 'preview']
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.pk and obj.image and obj.image.name:
            try:
                return format_html(
                    '<img src="{}" style="height:52px;width:52px;object-fit:contain;border-radius:4px;background:#f3f4f6;padding:2px;" />',
                    obj.image.url
                )
            except Exception:
                pass
        return '—'
    preview.short_description = 'Preview'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'price', 'quantity', 'line_total']
    fields = ['product_name', 'price', 'quantity', 'line_total']

    def line_total(self, obj):
        if obj.pk:
            return f'${obj.total_price:.2f}'
        return '—'
    line_total.short_description = 'Total'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active']
    list_editable = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = '# Products'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'website']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'image_tag', 'name', 'category', 'brand', 'price', 'compare_price',
        'discount_percentage', 'stock', 'is_active', 'is_featured', 'is_deal_of_day',
    ]
    list_filter = ['is_active', 'is_featured', 'is_deal_of_day', 'category', 'brand']
    list_editable = ['price', 'stock', 'is_active', 'is_featured', 'is_deal_of_day']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['discount_percentage', 'created_at', 'updated_at']
    inlines = [ProductImageInline]
    save_on_top = True
    fieldsets = (
        ('Basic Info', {
            'fields': ('category', 'brand', 'name', 'slug', 'sku')
        }),
        ('Description', {
            'fields': ('short_description', 'description', 'specifications')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price', 'discount_percentage')
        }),
        ('Inventory', {
            'fields': ('stock', 'weight')
        }),
        ('Visibility', {
            'fields': ('is_active', 'is_featured', 'is_deal_of_day', 'deal_expires')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def image_tag(self, obj):
        img = obj.primary_image
        if img:
            try:
                return format_html(
                    '<img src="{}" style="height:42px;width:42px;object-fit:contain;border-radius:6px;background:#f3f4f6;padding:2px;" />',
                    img.image.url
                )
            except Exception:
                pass
        return format_html('<span style="font-size:1.4rem">{}</span>', '📦')
    image_tag.short_description = ''


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'title', 'is_approved', 'is_verified_purchase', 'created_at']
    list_filter = ['is_approved', 'rating', 'is_verified_purchase']
    list_editable = ['is_approved']
    search_fields = ['user__username', 'product__name', 'title', 'comment']
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'full_name', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    search_fields = ['order_number', 'user__username', 'full_name', 'email']
    readonly_fields = ['order_number', 'subtotal', 'shipping_cost', 'tax', 'total', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Totals', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'total')
        }),
        ('Shipping Address', {
            'fields': ('full_name', 'email', 'phone', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product_count', 'created_at']
    search_fields = ['user__username']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = '# Saved'


# Cart is mostly for debugging; keep it simple
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'total_items', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'Items'


admin.site.site_header = 'NEXUS Store — Admin'
admin.site.site_title = 'NEXUS Admin'
admin.site.index_title = 'Store Management'


# ── Admin forms with auto-generated slugs ─────────────────────────────────────
from django import forms as _forms
from django.utils.text import slugify as _slugify


class AutoSlugForm(_forms.ModelForm):
    """Make slug optional in admin — auto-generates from name on save."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'slug' in self.fields:
            self.fields['slug'].required = False
            self.fields['slug'].help_text = 'Leave blank to auto-generate from name.'

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('slug'):
            name = cleaned.get('name', '')
            if name:
                base = _slugify(name)
                # Ensure uniqueness
                slug = base
                model = self._meta.model
                qs = model.objects.filter(slug=slug)
                if self.instance and self.instance.pk:
                    qs = qs.exclude(pk=self.instance.pk)
                counter = 1
                while qs.exists():
                    slug = f'{base}-{counter}'
                    counter += 1
                    qs = model.objects.filter(slug=slug)
                    if self.instance and self.instance.pk:
                        qs = qs.exclude(pk=self.instance.pk)
                cleaned['slug'] = slug
        return cleaned


class CategoryAdminForm(AutoSlugForm):
    class Meta:
        model = Category
        fields = '__all__'


class BrandAdminForm(AutoSlugForm):
    class Meta:
        model = Brand
        fields = '__all__'


CategoryAdmin.form = CategoryAdminForm
BrandAdmin.form = BrandAdminForm
