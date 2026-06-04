document.addEventListener('DOMContentLoaded', function () {

  // Auto-dismiss flash messages
  document.querySelectorAll('.flash').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-8px)';
      setTimeout(() => el.remove(), 600);
    }, 4500);
  });

  // Staggered card entrance animation
  const cards = document.querySelectorAll('.card, .stat-card, .activity-card, .badge-card, .challenge-card');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }, i * 60);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });

  cards.forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(18px)';
    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease, box-shadow 0.3s, border-color 0.2s';
    observer.observe(card);
  });

  // Animate progress bars
  setTimeout(() => {
    document.querySelectorAll('.progress-bar-fill').forEach(bar => {
      const target = bar.style.width;
      bar.style.width = '0%';
      setTimeout(() => { bar.style.width = target; }, 200);
    });
  }, 300);

  // Animate score numbers counting up
  document.querySelectorAll('.score-number').forEach(el => {
    const target = parseInt(el.textContent.replace(/\D/g, ''));
    if (!target) return;
    let current = 0;
    const step = Math.ceil(target / 60);
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current.toLocaleString();
      if (current >= target) clearInterval(timer);
    }, 20);
  });

  // Animate stat numbers
  document.querySelectorAll('.stat-number').forEach(el => {
    const raw = el.textContent.trim();
    const numeric = parseFloat(raw.replace(/[^0-9.]/g, ''));
    const suffix = raw.replace(/[0-9.,]/g, '').trim();
    if (!numeric || isNaN(numeric)) return;
    let current = 0;
    const isFloat = raw.includes('.');
    const duration = 900;
    const start = performance.now();
    function update(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      current = numeric * eased;
      el.textContent = (isFloat ? current.toFixed(1) : Math.round(current).toLocaleString()) + (suffix ? ' ' + suffix : '');
      if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
  });

});