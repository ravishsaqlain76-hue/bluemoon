/* ===== Blue Moon Residency — Client-side JS ===== */
(function () {
  'use strict';

  /* ---------- Scroll-to-top button ---------- */
  var scrollBtn = document.getElementById('scroll-to-top');
  if (scrollBtn) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 300) {
        scrollBtn.classList.add('visible');
      } else {
        scrollBtn.classList.remove('visible');
      }
    });
    scrollBtn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ---------- Fade-in on scroll (IntersectionObserver) ---------- */
  var fadeEls = document.querySelectorAll('.fade-in-section');
  if (fadeEls.length && 'IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    fadeEls.forEach(function (el) {
      observer.observe(el);
    });
  } else {
    // Fallback: show everything immediately
    fadeEls.forEach(function (el) {
      el.classList.add('is-visible');
    });
  }

  /* ---------- Form submit spinner ---------- */
  var overlay = document.getElementById('form-loading-overlay');
  if (overlay) {
    document.querySelectorAll('form').forEach(function (form) {
      // Skip search/filter forms (GET) — only intercept POST forms
      if (form.method && form.method.toUpperCase() !== 'POST') return;
      form.addEventListener('submit', function () {
        var btn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (btn) {
          btn.disabled = true;
        }
        overlay.classList.add('active');
      });
    });
  }

  /* ---------- Active nav link highlighting (backup) ---------- */
  var navLinks = document.querySelectorAll('.navbar-dark-custom .nav-item .nav-link');
  var currentPath = window.location.pathname;
  navLinks.forEach(function (link) {
    var href = link.getAttribute('href');
    if (href && href !== '/' && currentPath.startsWith(href)) {
      link.closest('.nav-item').classList.add('active');
    } else if (href === '/' && currentPath === '/') {
      link.closest('.nav-item').classList.add('active');
    }
  });
})();
