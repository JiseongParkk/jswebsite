(() => {
  const links = Array.from(document.querySelectorAll('#main-nav a[href^="#"]'));
  const sections = links.map(link => document.querySelector(link.getAttribute('href'))).filter(Boolean);
  if (!sections.length || !('IntersectionObserver' in window)) return;
  const visible = new Set();
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => { if (entry.isIntersecting) visible.add(entry.target); else visible.delete(entry.target); });
    const current = sections.find(section => visible.has(section));
    links.forEach(link => {
      if (current && link.getAttribute('href') === `#${current.id}`) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }, { rootMargin: '-105px 0px -35% 0px', threshold: 0 });
  sections.forEach(section => observer.observe(section));
})();
