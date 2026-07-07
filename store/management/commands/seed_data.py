import json, os, random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
from django.utils import timezone
from datetime import timedelta
from store.models import Category, Brand, Product, ProductImage, Review
from accounts.models import UserProfile
from blog.models import BlogCategory, Post
from django.utils.text import slugify


SMARTPHONES = [
    {"name": "Apple iPhone 16 Pro Max", "brand": "Apple", "price": "1199.00", "compare": "1299.00", "stock": 45, "sku": "APL-IP16PM", "featured": True, "short": "Titanium design, A18 Pro chip, 5x Tetraprism camera, 33hr battery.", "specs": {"Display": "6.9-inch Super Retina XDR ProMotion 120Hz","Processor": "A18 Pro (3nm)","RAM": "8GB","Storage": "256GB / 512GB / 1TB","Main Camera": "48MP + 48MP UW + 12MP 5x","Battery": "4685 mAh","OS": "iOS 18","Connectivity": "5G, Wi-Fi 7, USB-C"}},
    {"name": "Samsung Galaxy S25 Ultra", "brand": "Samsung", "price": "1299.00", "compare": "1399.00", "stock": 38, "sku": "SAM-GS25U", "featured": True, "short": "Galaxy AI, 200MP camera, S Pen, Snapdragon 8 Elite.", "specs": {"Display": "6.9-inch QHD+ AMOLED 120Hz","Processor": "Snapdragon 8 Elite","RAM": "12GB","Storage": "256GB – 1TB","Main Camera": "200MP + 50MP UW + 10MP + 50MP 5x","Battery": "5000 mAh 45W","OS": "Android 15 One UI 7","Special": "Built-in S Pen"}},
    {"name": "Google Pixel 9 Pro XL", "brand": "Google", "price": "1099.00", "compare": "1199.00", "stock": 30, "sku": "GOG-PX9PXL", "featured": True, "short": "Tensor G4, 7 years of updates, best computational photography.", "specs": {"Display": "6.8-inch LTPO OLED 120Hz","Processor": "Google Tensor G4","RAM": "16GB","Storage": "128GB – 1TB","Main Camera": "50MP 5x + 48MP UW + 48MP Main","Battery": "5060 mAh 37W","OS": "Android 15 (7yr updates)"}},
    {"name": "OnePlus 13 5G", "brand": "OnePlus", "price": "899.00", "compare": "999.00", "stock": 55, "sku": "OP-13-5G", "featured": True, "short": "100W SUPERVOOC, Hasselblad cameras, 6000mAh.", "specs": {"Display": "6.82-inch 2K LTPO AMOLED 120Hz","Processor": "Snapdragon 8 Elite","RAM": "12GB / 16GB","Camera": "50MP Hasselblad + 50MP UW + 50MP 3x","Battery": "6000 mAh 100W + 50W wireless","OS": "OxygenOS 15"}},
    {"name": "Xiaomi 15 Pro", "brand": "Xiaomi", "price": "999.00", "compare": "1099.00", "stock": 40, "sku": "XIA-15PRO", "short": "Leica Summilux optics, Snapdragon 8 Elite, 90W HyperCharge.", "specs": {"Display": "6.73-inch WQHD+ AMOLED 120Hz","Processor": "Snapdragon 8 Elite","Camera": "50MP Leica + 50MP UW + 50MP 5x","Battery": "6100 mAh 90W","OS": "HyperOS 2"}},
    {"name": "Sony Xperia 1 VI", "brand": "Sony", "price": "1099.00", "compare": "1199.00", "stock": 22, "sku": "SNY-XP1VI", "short": "Zeiss optics, 4K OLED display, Snapdragon 8 Gen 3.", "specs": {"Display": "6.5-inch 4K OLED 120Hz","Processor": "Snapdragon 8 Gen 3","Camera": "48MP Zeiss + 12MP UW + 12MP Periscope","Battery": "5000 mAh 30W"}},
    {"name": "Apple iPhone 16", "brand": "Apple", "price": "799.00", "compare": "899.00", "stock": 90, "sku": "APL-IP16", "deal": True, "short": "A18 chip, Action Button, Camera Control, Apple Intelligence.", "specs": {"Display": "6.1-inch Super Retina XDR","Processor": "A18 (3nm)","RAM": "8GB","Camera": "48MP + 12MP UW","Battery": "3561 mAh","OS": "iOS 18"}},
    {"name": "Samsung Galaxy A55 5G", "brand": "Samsung", "price": "449.00", "compare": "499.00", "stock": 120, "sku": "SAM-A55", "short": "50MP OIS, 6.6-inch AMOLED, IP67, premium mid-range.", "specs": {"Display": "6.6-inch FHD+ AMOLED 120Hz","Processor": "Exynos 1480","Camera": "50MP OIS + 12MP UW + 5MP Macro","Battery": "5000 mAh 25W"}},
    {"name": "Nothing Phone (3)", "brand": "Nothing", "price": "699.00", "compare": "749.00", "stock": 35, "sku": "NTH-PH3", "short": "Glyph Interface 2.0, Snapdragon 8 Gen 2, clean Nothing OS.", "specs": {"Display": "6.77-inch LTPO OLED 120Hz","Processor": "Snapdragon 8 Gen 2","Camera": "50MP OIS + 50MP UW","Battery": "5000 mAh 45W","OS": "Nothing OS 3"}},
    {"name": "Motorola Edge 50 Ultra", "brand": "Motorola", "price": "599.00", "compare": "699.00", "stock": 48, "sku": "MOT-E50U", "short": "125W TurboPower, 50MP periscope zoom, 144Hz pOLED.", "specs": {"Display": "6.67-inch FHD+ pOLED 144Hz","Processor": "Snapdragon 8s Gen 3","Camera": "50MP + 50MP UW + 64MP 3x Periscope","Battery": "4500 mAh 125W"}},
]

LAPTOPS = [
    {"name": "Apple MacBook Pro 16 M4 Max", "brand": "Apple", "price": "3499.00", "compare": "3799.00", "stock": 25, "sku": "APL-MBP16M4", "featured": True, "short": "M4 Max, 48GB RAM, Liquid Retina XDR, 22-hour battery.", "specs": {"Display": "16.2-inch Liquid Retina XDR 120Hz","Processor": "Apple M4 Max 16-core","RAM": "48GB Unified Memory","Storage": "1TB SSD","Battery": "22 hours","Weight": "2.14 kg","OS": "macOS Sequoia"}},
    {"name": "Dell XPS 15 (2025)", "brand": "Dell", "price": "2199.00", "compare": "2499.00", "stock": 30, "sku": "DEL-XPS15-25", "featured": True, "short": "Intel Core Ultra 9, 4K OLED touch, RTX 4070.", "specs": {"Display": "15.6-inch 4K OLED Touch","Processor": "Intel Core Ultra 9 185H","RAM": "32GB DDR5","GPU": "NVIDIA RTX 4070 8GB","Battery": "10 hours","Weight": "1.86 kg"}},
    {"name": "ASUS ROG Zephyrus G16 2025", "brand": "ASUS", "price": "2699.00", "compare": "2999.00", "stock": 20, "sku": "ASU-ROGG16", "featured": True, "short": "RTX 4090 Mobile, 240Hz OLED, Ryzen AI 9.", "specs": {"Display": "16-inch QHD+ OLED 240Hz","Processor": "AMD Ryzen AI 9 HX 365","RAM": "32GB DDR5","GPU": "RTX 4090 16GB Mobile","Storage": "2TB PCIe 5.0","Weight": "1.85 kg"}},
    {"name": "Lenovo ThinkPad X1 Carbon Gen 13", "brand": "Lenovo", "price": "1899.00", "compare": "2199.00", "stock": 42, "sku": "LEN-X1C13", "featured": True, "short": "1.12 kg ultrabook, 2.8K OLED, Intel Core Ultra 7.", "specs": {"Display": "14-inch 2.8K OLED 90Hz","Processor": "Intel Core Ultra 7 258V","RAM": "32GB LPDDR5","Battery": "15 hours","Weight": "1.12 kg","Cert": "MIL-STD-810H"}},
    {"name": "HP Spectre x360 14 2025", "brand": "HP", "price": "1699.00", "compare": "1899.00", "stock": 35, "sku": "HP-SPX36014", "short": "2-in-1 OLED, Core Ultra 7, 17hr battery, stylus.", "specs": {"Display": "14-inch 2.8K OLED Touch","Processor": "Intel Core Ultra 7 258V","RAM": "32GB","Battery": "17 hours","Weight": "1.43 kg"}},
    {"name": "Microsoft Surface Laptop 7 15", "brand": "Microsoft", "price": "1699.00", "compare": "1899.00", "stock": 28, "sku": "MSF-SL7-15", "short": "Snapdragon X Elite Copilot+, 22hr battery, PixelSense touch.", "specs": {"Display": "15-inch PixelSense 120Hz Touch","Processor": "Snapdragon X Elite","RAM": "32GB LPDDR5","Battery": "22 hours","Weight": "1.66 kg","OS": "Windows 11 Copilot+"}},
    {"name": "Razer Blade 18 (2025)", "brand": "Razer", "price": "3999.00", "compare": "4299.00", "stock": 15, "sku": "RAZ-BL18-25", "short": "RTX 4090, i9-14900HX, 18-inch 300Hz QHD+ gaming beast.", "specs": {"Display": "18-inch QHD+ 300Hz IPS","Processor": "Intel Core i9-14900HX","RAM": "32GB DDR5","GPU": "RTX 4090 16GB","Storage": "2TB SSD","Weight": "3.03 kg"}},
    {"name": "LG Gram 17 2025", "brand": "LG", "price": "1599.00", "compare": "1799.00", "stock": 38, "sku": "LG-GRAM17-25", "short": "World's lightest 17-inch at 1.35 kg, 25hr battery.", "specs": {"Display": "17-inch 2560x1600 IPS","Processor": "Intel Core Ultra 7 155H","RAM": "32GB DDR5","Battery": "25 hours (MIL-STD-810H)","Weight": "1.35 kg"}},
    {"name": "Apple MacBook Air 13 M4", "brand": "Apple", "price": "1099.00", "compare": "1299.00", "stock": 80, "sku": "APL-MBA13M4", "deal": True, "short": "M4 chip, 18hr battery, fanless, Liquid Retina display.", "specs": {"Display": "13.6-inch Liquid Retina 2560x1664","Processor": "Apple M4 10-core","RAM": "16GB Unified","Storage": "256GB – 1TB SSD","Battery": "18 hours","Weight": "1.24 kg","OS": "macOS Sequoia"}},
    {"name": "ASUS ProArt Studiobook 16 OLED", "brand": "ASUS", "price": "2999.00", "compare": "3299.00", "stock": 18, "sku": "ASU-PAST16", "short": "4K OLED, RTX 4070, PANTONE Validated, ASUS Dial.", "specs": {"Display": "16-inch 4K OLED 120Hz PANTONE","Processor": "Intel Core Ultra 9 185H","RAM": "32GB DDR5","GPU": "RTX 4070 8GB","Weight": "1.85 kg","OS": "Windows 11 Pro"}},
]

CAMERAS = [
    {"name": "Sony Alpha A7R V", "brand": "Sony", "price": "3499.00", "compare": "3799.00", "stock": 20, "sku": "SNY-A7RV", "featured": True, "short": "61MP full-frame, AI tracking, 8-stop IBIS, 4K 60fps.", "specs": {"Sensor": "61MP Full-Frame BSI CMOS","AF": "693-point Phase + AI","IBIS": "8-stop","Video": "4K 60fps / 8K 25fps","Viewfinder": "9.44M-dot OLED","Weight": "723g"}},
    {"name": "Canon EOS R5 Mark II", "brand": "Canon", "price": "4299.00", "compare": "4599.00", "stock": 15, "sku": "CAN-R5MK2", "featured": True, "short": "45MP, 8K RAW 60fps, Dual Pixel AF II, 30fps burst.", "specs": {"Sensor": "45MP Full-Frame CMOS","AF": "Dual Pixel CMOS AF II","IBIS": "8-stop","Video": "8K RAW 60fps / 4K 120fps","Burst": "30fps electronic","Weight": "746g"}},
    {"name": "Nikon Z8", "brand": "Nikon", "price": "3999.00", "compare": "4299.00", "stock": 18, "sku": "NIK-Z8", "featured": True, "short": "45.7MP stacked BSI, 8K 60fps, 20fps, AI subject detection.", "specs": {"Sensor": "45.7MP Stacked BSI CMOS","AF": "AI Subject Detection","IBIS": "6-stop","Video": "8K 60fps RAW / 4K 120fps","Burst": "20fps","Weight": "910g"}},
    {"name": "Fujifilm X-T5", "brand": "Fujifilm", "price": "1699.00", "compare": "1899.00", "stock": 35, "sku": "FUJ-XT5", "featured": True, "short": "40MP APS-C, 20 Film Simulations, 7-stop IBIS, 6.2K video.", "specs": {"Sensor": "40.2MP APS-C X-Trans","IBIS": "7-stop","Video": "6.2K 30fps / 4K 60fps","Film Simulations": "20 presets","Weight": "557g"}},
    {"name": "OM System OM-1 Mark II", "brand": "OM System", "price": "2199.00", "compare": "2499.00", "stock": 25, "sku": "OMS-OM1MK2", "short": "8.5-stop IBIS, 50fps burst, 80MP hand-held Hi-Res, IP53.", "specs": {"Sensor": "20.4MP MFT Stacked BSI","AF": "1053-point AI","IBIS": "8.5-stop","Video": "4K 60fps 10-bit","Burst": "50fps","Weather": "IP53 -25C","Weight": "599g"}},
    {"name": "Leica Q3", "brand": "Leica", "price": "5995.00", "compare": "6295.00", "stock": 8, "sku": "LEI-Q3", "short": "60MP full-frame, Summilux 28mm f/1.7, 8K video.", "specs": {"Sensor": "60MP Full-Frame BSI","Lens": "Summilux 28mm f/1.7 ASPH (fixed)","Video": "8K 30fps / 4K 60fps","Viewfinder": "5.76M-dot OLED","Weight": "743g","Special": "Leica craftsmanship"}},
    {"name": "GoPro HERO13 Black", "brand": "GoPro", "price": "399.00", "compare": "449.00", "stock": 90, "sku": "GOP-H13B", "deal": True, "short": "5.3K 60fps, HyperSmooth 6.0, 27MP, waterproof 10m.", "specs": {"Video": "5.3K 60fps / 4K 120fps","Photo": "27MP RAW","Stabilization": "HyperSmooth 6.0","Waterproof": "10m","Weight": "154g"}},
    {"name": "DJI Osmo Pocket 3", "brand": "DJI", "price": "519.00", "compare": "569.00", "stock": 65, "sku": "DJI-OP3", "short": "1-inch CMOS, 4K 120fps, 3-axis gimbal, flip screen.", "specs": {"Sensor": "1-inch CMOS","Video": "4K 120fps HDR","Gimbal": "3-axis","Display": "2-inch flip touchscreen","Battery": "1300mAh","Weight": "179g"}},
    {"name": "Sony ZV-E10 II", "brand": "Sony", "price": "799.00", "compare": "899.00", "stock": 55, "sku": "SNY-ZVE10II", "short": "26MP APS-C vlog camera, 4K 120fps, AI auto-frame.", "specs": {"Sensor": "26MP APS-C Exmor R","AF": "759-point AI AF","Video": "4K 120fps","Display": "3-inch vari-angle touch","Mount": "Sony E-Mount","Weight": "291g"}},
    {"name": "Ricoh GR IIIx", "brand": "Ricoh", "price": "1099.00", "compare": "1199.00", "stock": 30, "sku": "RIC-GR3X", "short": "40mm f/2.8 APS-C, 24MP, IBIS, pocketable street camera.", "specs": {"Sensor": "24.24MP APS-C","Lens": "40mm f/2.8 fixed","IBIS": "3-axis","Display": "3-inch touchscreen","Weight": "262g"}},
]


class Command(BaseCommand):
    help = 'Seed database with 30 products, users, and blog posts'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('Seeding NEXUS store...'))

        # Superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@nexus.com', 'admin123')
            self.stdout.write('  ✓ Admin: admin / admin123')

        # Demo user
        if not User.objects.filter(username='demo').exists():
            u = User.objects.create_user('demo', 'demo@nexus.com', 'demo123', first_name='Alex', last_name='Johnson')
            UserProfile.objects.get_or_create(user=u)
            self.stdout.write('  ✓ Demo user: demo / demo123')

        # Categories
        cats = {}
        for name, sl, desc in [
            ('Smartphones', 'smartphones', 'Latest flagship and mid-range smartphones'),
            ('Laptops', 'laptops', 'Ultrabooks, gaming laptops, and workstations'),
            ('Cameras', 'cameras', 'Mirrorless, compact, and action cameras'),
        ]:
            c, _ = Category.objects.get_or_create(slug=sl, defaults={'name': name, 'description': desc})
            cats[sl] = c
            self.stdout.write(f'  ✓ Category: {name}')

        # Brands
        brand_names = [
            'Apple','Samsung','Google','OnePlus','Xiaomi','Sony','Motorola','Nothing',
            'Canon','Nikon','Fujifilm','OM System','Leica','GoPro','DJI','Ricoh',
            'Dell','ASUS','Lenovo','HP','Microsoft','Razer','LG',
        ]
        brands = {}
        for n in brand_names:
            b, _ = Brand.objects.get_or_create(slug=slugify(n), defaults={'name': n})
            brands[n] = b

        # Blog
        bc, _ = BlogCategory.objects.get_or_create(name='Reviews', defaults={'slug': 'reviews'})
        bc2, _ = BlogCategory.objects.get_or_create(name='Buying Guides', defaults={'slug': 'buying-guides'})
        admin_user = User.objects.get(username='admin')

        blog_posts = [
            ('Best Smartphones of 2025 Complete Buyer Guide', 'reviews', 'We tested all major 2025 flagships. Here is our definitive ranking and buying advice.'),
            ('MacBook Air M4 vs Dell XPS 15 Which Should You Buy', 'buying-guides', 'Two of the best laptops of the year go head to head in our comprehensive comparison.'),
            ('Best Mirrorless Cameras for Beginners in 2025', 'reviews', 'Starting your photography journey? These cameras make it easy and rewarding.'),
            ('iPhone 16 Pro Max Full Review After 30 Days', 'reviews', 'A month with the best iPhone ever made. Here is what we found day to day.'),
            ('The Ultimate Laptop Buying Guide 2025', 'buying-guides', 'Everything you need to know to choose the perfect laptop for your workflow.'),
            ('Sony A7R V vs Canon R5 II The Professional Choice', 'reviews', 'Two flagship mirrorless cameras battle it out for the professional photographer crown.'),
        ]
        for title, cat_slug, excerpt in blog_posts:
            if not Post.objects.filter(slug=slugify(title)).exists():
                bl_cat = bc if cat_slug == 'reviews' else bc2
                Post.objects.create(
                    author=admin_user, category=bl_cat, title=title,
                    slug=slugify(title), excerpt=excerpt,
                    content=f"{excerpt}\n\nThis is a placeholder article. Add your full content here through the Django admin panel at /admin/blog/post/.\n\nNEXUS Academy brings you expert reviews, buying guides, and the latest in tech news. Stay tuned for more detailed content coming soon.",
                    status='published', published_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                    views=random.randint(50, 2000),
                )
        self.stdout.write(f'  ✓ Blog posts created')

        # Products
        all_sets = [
            (SMARTPHONES, 'smartphones'),
            (LAPTOPS, 'laptops'),
            (CAMERAS, 'cameras'),
        ]

        img_base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 'media', 'products')

        product_count = 0
        for data_list, cat_slug in all_sets:
            cat = cats[cat_slug]
            for i, d in enumerate(data_list):
                if Product.objects.filter(sku=d['sku']).exists():
                    self.stdout.write(f'  - Skipped (exists): {d["name"]}')
                    continue

                brand = brands.get(d['brand'])
                is_deal = d.get('deal', False)
                is_featured = d.get('featured', False)
                deal_expires = timezone.now() + timedelta(hours=random.randint(8, 36)) if is_deal else None
                specs_json = json.dumps(d.get('specs', {}))

                p = Product.objects.create(
                    category=cat, brand=brand,
                    name=d['name'], short_description=d['short'],
                    description=d['short'] + '\n\nThis product represents the pinnacle of modern technology. Engineered for professionals and enthusiasts alike, it delivers uncompromising performance in every scenario.\n\nAvailable now at NEXUS with free shipping on orders over $99, 30-day returns, and a 2-year warranty.',
                    price=Decimal(d['price']), compare_price=Decimal(d['compare']) if d.get('compare') else None,
                    sku=d['sku'], stock=d['stock'], is_active=True,
                    is_featured=is_featured, is_deal_of_day=is_deal,
                    deal_expires=deal_expires, specifications=specs_json,
                    meta_title=f"{d['name']} — Buy at NEXUS Store",
                    meta_description=d['short'][:155],
                )

                # Attach product images (prefer real photo formats, fall back to SVG placeholder)
                for j in range(5):
                    img_path = None
                    ext = None
                    for candidate_ext in ('webp', 'jpg', 'jpeg', 'png', 'svg'):
                        candidate = os.path.join(img_base, f'{cat_slug}_{i+1}_view{j+1}.{candidate_ext}')
                        if os.path.exists(candidate):
                            img_path = candidate
                            ext = candidate_ext
                            break
                    if img_path:
                        with open(img_path, 'rb') as f:
                            from django.core.files import File as DjangoFile
                            pi = ProductImage(product=p, is_primary=(j == 0), order=j, alt_text=f'{p.name} view {j+1}')
                            pi.image.save(f'{cat_slug}_{i+1}_v{j+1}.{ext}', DjangoFile(f), save=True)
                    else:
                        ProductImage.objects.create(product=p, is_primary=(j == 0), order=j)

                # Add reviews
                demo = User.objects.filter(username='demo').first()
                if demo and not Review.objects.filter(product=p, user=demo).exists():
                    Review.objects.create(
                        product=p, user=demo,
                        rating=random.choice([4, 5, 5, 5]),
                        title=random.choice(['Excellent product!', 'Highly recommend', 'Great value', 'Worth every penny']),
                        comment=f'I bought the {p.name} last month and I am absolutely thrilled. The performance is exceptional and it lives up to all the hype. Build quality is superb and delivery was fast through NEXUS.',
                        is_approved=True, is_verified_purchase=True,
                    )

                self.stdout.write(f'  ✓ {p.name}')
                product_count += 1

        self.stdout.write(self.style.SUCCESS(f'\n✅ Done! {product_count} products created.'))
        self.stdout.write(f'   Admin panel:  http://127.0.0.1:8000/admin  (admin / admin123)')
        self.stdout.write(f'   Store:        http://127.0.0.1:8000')
        self.stdout.write(f'   Demo login:   demo / demo123')
