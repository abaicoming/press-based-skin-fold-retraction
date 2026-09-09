(() => {
  function showMissingAsset(container, source) {
    if (container.querySelector('.media-error')) return;
    const message = document.createElement('p');
    message.className = 'media-error';
    message.textContent = `Add ${source} to display this media.`;
    container.append(message);
  }

  function loadVideo(container) {
    if (container.dataset.loaded === 'true') return;
    const source = container.dataset.video;
    if (!source) return;

    container.dataset.loaded = 'true';
    const video = document.createElement('video');
    video.className = 'loaded-video';
    video.src = source;
    video.controls = true;
    video.playsInline = true;
    video.preload = 'metadata';
    video.setAttribute('aria-label', container.dataset.label || 'Project video');
    video.addEventListener('error', () => showMissingAsset(container, source), { once: true });
    container.append(video);
    video.play().catch(() => {});
  }

  document.querySelectorAll('[data-video]').forEach((container) => {
    const trigger = container.querySelector('.video-trigger');
    if (trigger) trigger.addEventListener('click', () => loadVideo(container));
  });

  function loadImage(container) {
    if (container.dataset.imageLoaded === 'true') return;
    const source = container.dataset.image;
    if (!source) return;

    container.dataset.imageLoaded = 'true';
    const image = document.createElement('img');
    image.src = source;
    image.alt = container.dataset.alt || '';
    image.loading = 'lazy';
    image.decoding = 'async';
    image.addEventListener('error', () => image.remove(), { once: true });
    container.append(image);
  }

  const imageSlots = document.querySelectorAll('[data-image]');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        loadImage(entry.target);
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '180px 0px' });
    imageSlots.forEach((slot) => observer.observe(slot));
  } else {
    imageSlots.forEach(loadImage);
  }
})();
