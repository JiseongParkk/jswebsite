(() => {
  const button = document.querySelector('.menu-toggle');
  const nav = document.getElementById('main-nav');
  if (!button || !nav) return;
  const compact = window.matchMedia('(max-width: 900px)');
  button.hidden = false;
  document.documentElement.classList.add('menu-ready');
  function setOpen(open) {
    button.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('is-open', open);
  }
  button.addEventListener('click', () => setOpen(button.getAttribute('aria-expanded') !== 'true'));
  nav.addEventListener('click', event => { if (event.target.closest('a')) setOpen(false); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
      setOpen(false); button.focus();
    }
  });
  compact.addEventListener('change', () => setOpen(false));
})();
