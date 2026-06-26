// NEXUS Store — Main JS

document.addEventListener('DOMContentLoaded', function() {

  // ── CART: AJAX Add to Cart ──
  document.querySelectorAll('.ajax-add-cart').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const productId = this.dataset.productId;
      const qty = document.getElementById('qty-' + productId);
      const quantity = qty ? qty.value : 1;
      const csrfToken = getCsrfToken();

      fetch('/cart/add/' + productId + '/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'quantity=' + quantity
      })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          showToast(data.message || 'Added to cart!');
          // Update cart badge
          document.querySelectorAll('.cart-badge').forEach(function(badge) {
            badge.textContent = data.cart_count;
            badge.style.display = data.cart_count > 0 ? 'flex' : 'none';
          });
          // Flash button
          btn.textContent = '✓ Added';
          btn.style.background = 'var(--success)';
          setTimeout(function() {
            btn.innerHTML = '<i class="bi bi-bag-plus"></i>';
            btn.style.background = '';
          }, 1500);
        }
      })
      .catch(err => console.error('Cart error:', err));
    });
  });

  // ── WISHLIST: AJAX Toggle ──
  document.querySelectorAll('.ajax-wishlist').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const productId = this.dataset.productId;
      const csrfToken = getCsrfToken();

      fetch('/wishlist/toggle/' + productId + '/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest',
        }
      })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          showToast(data.message);
          if (data.in_wishlist) {
            this.classList.add('active');
            this.querySelector('i').className = 'bi bi-heart-fill';
            this.style.color = 'var(--danger)';
          } else {
            this.classList.remove('active');
            this.querySelector('i').className = 'bi bi-heart';
            this.style.color = '';
          }
        }
      })
      .catch(() => { window.location.href = '/accounts/login/'; });
    });
  });

  // ── QUANTITY CONTROLS ──
  document.querySelectorAll('.qty-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const input = this.closest('.qty-control').querySelector('.qty-input');
      let val = parseInt(input.value) || 1;
      if (this.dataset.action === 'inc') val = Math.min(val + 1, 99);
      if (this.dataset.action === 'dec') val = Math.max(val - 1, 1);
      input.value = val;
    });
  });

  // ── PRODUCT IMAGE GALLERY ──
  document.querySelectorAll('.product-thumb').forEach(function(thumb) {
    thumb.addEventListener('click', function() {
      const mainImg = document.getElementById('main-product-img');
      if (mainImg) {
        mainImg.src = this.dataset.img;
        document.querySelectorAll('.product-thumb').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
      }
    });
  });

  // ── COUNTDOWN TIMERS ──
  document.querySelectorAll('[data-countdown]').forEach(function(el) {
    const end = new Date(el.dataset.countdown).getTime();
    function update() {
      const now = Date.now();
      const diff = end - now;
      if (diff <= 0) { el.innerHTML = '<span>Expired</span>'; return; }
      const h = Math.floor(diff / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      const s = Math.floor((diff % 60000) / 1000);
      const pad = n => String(n).padStart(2, '0');
      el.querySelectorAll('.timer-num')[0] && (el.querySelectorAll('.timer-num')[0].textContent = pad(h));
      el.querySelectorAll('.timer-num')[1] && (el.querySelectorAll('.timer-num')[1].textContent = pad(m));
      el.querySelectorAll('.timer-num')[2] && (el.querySelectorAll('.timer-num')[2].textContent = pad(s));
    }
    update();
    setInterval(update, 1000);
  });

  // ── STICKY HEADER SHADOW ──
  const header = document.querySelector('.main-header');
  if (header) {
    window.addEventListener('scroll', function() {
      header.style.boxShadow = window.scrollY > 10 ? '0 4px 20px rgba(0,0,0,.4)' : '0 2px 12px rgba(0,0,0,.3)';
    });
  }

  // ── MESSAGES AUTO-DISMISS ──
  setTimeout(function() {
    document.querySelectorAll('.alert').forEach(function(el) {
      if (el.classList.contains('show')) {
        el.style.transition = 'opacity .4s';
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 400);
      }
    });
  }, 5000);

});

function showToast(msg) {
  const toastEl = document.getElementById('cartToast');
  const msgEl = document.getElementById('toastMessage');
  if (!toastEl || !msgEl) return;
  msgEl.textContent = msg;
  const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
  toast.show();
}

function getCsrfToken() {
  const cookie = document.cookie.split('; ').find(r => r.startsWith('csrftoken='));
  return cookie ? cookie.split('=')[1] : '';
}
