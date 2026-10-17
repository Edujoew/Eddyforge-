/* ══════════════════════════════════════
   EDDYFORGE — SHARED NAV & UI LOGIC
══════════════════════════════════════ */

window.addEventListener('DOMContentLoaded', () => {
  
  // ── 1. NAV TOGGLE LOGIC ──
  const toggle = document.getElementById('navToggle');
  const links  = document.getElementById('navLinks');
  
  if (toggle && links) {
    // Toggle menu open/close
    toggle.addEventListener('click', (e) => {
      e.stopPropagation(); 
      const isOpen = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(isOpen));
    });

    // Close menu when clicking a link (important for mobile)
    links.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        links.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });

    // Close menu when clicking anywhere outside the menu
    document.addEventListener('click', (e) => {
      if (!links.contains(e.target) && !toggle.contains(e.target)) {
        links.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // ── 2. SCROLL REVEAL ANIMATION ──
  const reveals = document.querySelectorAll('.reveal');
  if (reveals.length > 0) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e, i) => {
        if (e.isIntersecting) {
          // Staggered appearance
          setTimeout(() => e.target.classList.add('visible'), i * 80);
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.1 });
    
    reveals.forEach(el => io.observe(el));
  }

  // ── 3. NAV ACTIVE LINK STATE ──
  // Checks the URL and highlights the current page link
  const currentPath = window.location.pathname;
  
  document.querySelectorAll('.nav-links a').forEach(a => {
    const linkPath = new URL(a.href).pathname;
    const isActive = linkPath === '/'
      ? currentPath === '/'
      : currentPath === linkPath || currentPath.startsWith(linkPath);
    if (isActive && !a.classList.contains('nav-cta')) {
      a.classList.add('active');
    }
  });

  // ── 4. NAV SCROLL EFFECT (DARKEN) ──
  const nav = document.querySelector('.nav-wrap');
  if (nav) {
    window.addEventListener('scroll', () => {
      // Adds 'scrolled' class after 40px of scrolling
      nav.classList.toggle('scrolled', window.scrollY > 40);
    }, { passive: true }); // Better performance
  }
});
