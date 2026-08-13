/* ══════════════════════════════════════
   EDDYFORGE — CONTENT RENDERER
   Loads content.json (or a locally saved
   admin preview) and fills in any page
   that has matching containers / data-cms
   attributes. Safe to include everywhere.
══════════════════════════════════════ */

function cmsResolve(obj, path) {
  return path.split('.').reduce((o, k) => (o == null ? undefined : o[k]), obj);
}

function cmsIcon(cls) {
  return `<i class="bi ${cls}"></i>`;
}

function renderServicesGrid(data) {
  const el = document.getElementById('services-grid');
  if (!el) return;
  el.innerHTML = data.services.map((s, i) => `
    <div class="tech-card reveal" style="display:grid;grid-template-columns:80px 1fr auto;gap:32px;align-items:center;">
      <div style="width:72px;height:72px;border-radius:16px;background:var(--cyan-dim);border:1px solid var(--border-h);display:grid;place-items:center;font-size:2rem;color:var(--cyan);flex-shrink:0;">${cmsIcon(s.icon)}</div>
      <div>
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:10px;">
          <span style="font-family:var(--display);font-weight:700;font-size:1.3rem;color:#fff;">${s.title}</span>
          <span style="font-family:var(--mono);font-size:.65rem;color:var(--muted);letter-spacing:.1em;border:1px solid var(--border);padding:3px 10px;border-radius:50px;">${String(i + 1).padStart(2, '0')}</span>
        </div>
        <p style="color:var(--muted);font-size:.95rem;line-height:1.8;max-width:620px;">${s.longDescription || s.description}</p>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:16px;">
          ${(s.tags || []).map(t => `<span style="font-family:var(--mono);font-size:.7rem;color:var(--cyan);background:var(--cyan-dim);padding:4px 10px;border-radius:6px;">${t}</span>`).join('')}
        </div>
      </div>
      <a href="contact.html" class="btn-ghost" style="white-space:nowrap;flex-shrink:0;">Get Quote <i class="bi bi-arrow-right"></i></a>
    </div>
  `).join('');
}

function renderServicesPreview(data) {
  const el = document.getElementById('services-preview');
  if (!el) return;
  el.innerHTML = data.services.slice(0, 3).map((s, i) => `
    <div class="tech-card reveal">
      <div style="width:52px;height:52px;border-radius:12px;background:var(--cyan-dim);display:grid;place-items:center;font-size:1.4rem;color:var(--cyan);margin-bottom:24px;">${cmsIcon(s.icon)}</div>
      <div style="font-family:var(--display);font-weight:700;font-size:1.1rem;color:#fff;margin-bottom:8px;">${s.title}</div>
      <p style="color:var(--muted);font-size:.93rem;">${s.description}</p>
      <span style="position:absolute;bottom:20px;right:20px;font-family:var(--mono);font-size:.7rem;color:var(--border-h);">${String(i + 1).padStart(2, '0')}</span>
    </div>
  `).join('');
}

function renderProjectsFeatured(data) {
  const el = document.getElementById('projects-featured');
  if (!el) return;
  el.innerHTML = data.projects.map((p) => {
    const media = `
      <div style="background:var(--bg-2);border:1px solid var(--border);border-radius:10px;height:260px;display:grid;place-items:center;position:relative;overflow:hidden;${p.imageFirst ? 'order:-1;' : ''}">
        <div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(${p.accent},.06),transparent);"></div>
        <div style="text-align:center;position:relative;z-index:1;">
          <i class="bi ${p.icon}" style="font-size:4rem;color:rgb(${p.accent});opacity:.4;display:block;margin-bottom:12px;"></i>
          <div style="font-family:var(--mono);font-size:.72rem;color:var(--muted);letter-spacing:.1em;text-transform:uppercase;">${p.iconLabel}</div>
        </div>
      </div>`;
    const info = `
      <div>
        <div style="display:inline-flex;align-items:center;gap:6px;background:rgba(${p.accent},.1);border:1px solid rgba(${p.accent},.25);color:rgb(${p.accent});font-family:var(--mono);font-size:.7rem;padding:4px 14px;border-radius:50px;margin-bottom:20px;">${cmsIcon(p.badgeIcon)} ${p.badge}</div>
        <h3 style="font-family:var(--display);font-weight:800;font-size:1.8rem;color:#fff;letter-spacing:-.03em;margin-bottom:16px;">${p.title}</h3>
        <p style="color:var(--muted);font-size:.97rem;line-height:1.85;margin-bottom:24px;">${p.description}</p>
        <div style="display:flex;flex-direction:column;gap:10px;margin-bottom:28px;">
          ${p.highlights.map(h => `<div style="display:flex;align-items:center;gap:10px;font-size:.9rem;color:var(--text);"><i class="bi bi-check-circle-fill" style="color:var(--cyan);"></i> ${h}</div>`).join('')}
        </div>
        <a href="${p.repo}" target="_blank" class="btn-primary-c"><i class="bi bi-github"></i> View Repository</a>
      </div>`;
    return `
      <div class="tech-card reveal" style="margin-bottom:28px;display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:center;">
        ${p.imageFirst ? media + info : info + media}
      </div>`;
  }).join('');
}

function renderProjectsTeaser(data) {
  const el = document.getElementById('projects-teaser');
  if (!el) return;
  el.innerHTML = data.projects.slice(0, 2).map(p => `
    <div class="tech-card reveal" style="display:flex;flex-direction:column;gap:16px;">
      <div style="display:inline-flex;align-items:center;gap:6px;background:rgba(${p.accent},.1);border:1px solid rgba(${p.accent},.25);color:rgb(${p.accent});font-family:var(--mono);font-size:.7rem;padding:4px 12px;border-radius:50px;width:fit-content;">${cmsIcon(p.badgeIcon)} ${p.badge}</div>
      <div style="font-family:var(--display);font-weight:700;font-size:1.2rem;color:#fff;">${p.shortTitle}</div>
      <p style="color:var(--muted);font-size:.92rem;flex:1;">${p.shortDescription}</p>
      <a href="projects.html" class="project-link" style="display:inline-flex;align-items:center;gap:8px;font-family:var(--mono);font-size:.75rem;color:var(--cyan);text-decoration:none;letter-spacing:.06em;text-transform:uppercase;">View Project <i class="bi bi-arrow-right"></i></a>
    </div>
  `).join('');
}

function renderTestimonials(data) {
  document.querySelectorAll('[id="testimonials-grid"]').forEach(el => {
    el.innerHTML = data.testimonials.map(t => `
      <div class="tech-card reveal" style="position:relative;">
        <i class="bi bi-quote" style="font-size:2.5rem;color:var(--cyan);opacity:.12;position:absolute;top:24px;right:24px;"></i>
        <p style="font-style:italic;color:var(--text);font-size:1rem;line-height:1.8;margin-bottom:28px;">"${t.quote}"</p>
        <div style="display:flex;align-items:center;gap:14px;">
          <div style="width:42px;height:42px;border-radius:50%;background:var(--cyan-dim);color:var(--cyan);display:grid;place-items:center;font-family:var(--display);font-weight:700;font-size:.85rem;flex-shrink:0;">${t.initials}</div>
          <div>
            <span style="font-weight:700;color:#fff;display:block;">${t.name}</span>
            <span style="font-family:var(--mono);font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;">${t.role}</span>
          </div>
        </div>
      </div>
    `).join('');
  });
}

function renderStats(data) {
  const p = document.getElementById('stat-projects');
  if (p) p.textContent = data.projects.length;
  const y = document.getElementById('stat-years');
  if (y) y.textContent = data.stats.yearsBuilding;
  const r = document.getElementById('stat-remote');
  if (r) r.textContent = data.stats.remotePercent;
}

function renderCmsFields(data) {
  document.querySelectorAll('[data-cms]').forEach(el => {
    const path = el.getAttribute('data-cms');
    const val = cmsResolve(data, path);
    if (val === undefined || val === null) return;
    const attr = el.getAttribute('data-cms-attr');
    const prefix = el.getAttribute('data-cms-prefix') || '';
    if (attr) {
      el.setAttribute(attr, prefix + val);
    } else {
      el.textContent = prefix + val;
    }
  });
}

// Live-preview override: the admin panel writes edited content here so
// changes are visible immediately in this browser without a redeploy.
const CMS_OVERRIDE_KEY = 'eddyforge_content_override';

async function loadCms() {
  try {
    let data;
    const override = localStorage.getItem(CMS_OVERRIDE_KEY);
    if (override) {
      data = JSON.parse(override);
    } else {
      const res = await fetch('content.json', { cache: 'no-store' });
      data = await res.json();
    }
    renderServicesGrid(data);
    renderServicesPreview(data);
    renderProjectsFeatured(data);
    renderProjectsTeaser(data);
    renderTestimonials(data);
    renderStats(data);
    renderCmsFields(data);
    // CMS containers are filled AFTER nav.js's IntersectionObserver already
    // ran on page load, so freshly injected .reveal nodes would never be
    // observed and stay invisible. Show them immediately instead.
    ['services-grid', 'services-preview', 'projects-featured', 'projects-teaser'].forEach(id => {
      const c = document.getElementById(id);
      if (c) c.querySelectorAll('.reveal').forEach(r => r.classList.add('visible'));
    });
    document.querySelectorAll('[id="testimonials-grid"]').forEach(c => {
      c.querySelectorAll('.reveal').forEach(r => r.classList.add('visible'));
    });
    document.dispatchEvent(new CustomEvent('cms:ready', { detail: data }));
  } catch (err) {
    console.warn('Eddyforge CMS: could not load content.json — showing static fallback markup.', err);
  }
}

document.addEventListener('DOMContentLoaded', loadCms);
