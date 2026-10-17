document.addEventListener('click', (event) => {
  const trigger = event.target.closest('[data-lightbox-trigger]');
  if (!trigger) return;

  const dialog = document.getElementById('image-lightbox');
  const image = dialog && dialog.querySelector('img');
  if (!dialog || !image) return;

  image.src = trigger.dataset.lightboxTrigger;
  image.alt = trigger.dataset.lightboxAlt || '';
  dialog.showModal();
});

document.addEventListener('click', (event) => {
  const closeButton = event.target.closest('[data-lightbox-close]');
  if (closeButton) {
    const dialog = document.getElementById('image-lightbox');
    if (dialog) dialog.close();
  }
});

document.addEventListener('DOMContentLoaded', () => {
  if (window.hljs) {
    document.querySelectorAll('.blog-body pre code').forEach(block => {
      window.hljs.highlightElement(block);
    });
  }

  document.querySelectorAll('.blog-body pre').forEach(pre => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-code-button';
    button.textContent = 'Copy code';
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(pre.querySelector('code')?.innerText || pre.innerText);
        button.textContent = 'Copied';
      } catch (error) {
        button.textContent = 'Select code to copy';
      }
    });
    pre.before(button);
  });

  const progress = document.getElementById('reading-progress');
  const article = document.getElementById('article-body');
  if (progress && article) {
    const updateProgress = () => {
      const bounds = article.getBoundingClientRect();
      const total = bounds.height + window.innerHeight;
      const read = Math.min(100, Math.max(0, (window.innerHeight - bounds.top) / total * 100));
      progress.style.transform = `scaleX(${read / 100})`;
      progress.setAttribute('aria-valuenow', String(Math.round(read)));
    };
    window.addEventListener('scroll', updateProgress, { passive: true });
    updateProgress();
  }

  const copyLink = document.querySelector('[data-copy-link]');
  if (copyLink) {
    copyLink.addEventListener('click', async () => {
      const status = document.getElementById('copy-link-status');
      try {
        await navigator.clipboard.writeText(window.location.href);
        if (status) status.textContent = 'Article link copied.';
      } catch (error) {
        if (status) status.textContent = `Copy unavailable. Article URL: ${window.location.href}`;
      }
    });
  }
});
