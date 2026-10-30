(() => {
  const root = document.querySelector('.ct-project');
  if (!root) return;
  const cases = [...root.querySelectorAll('.project-case')];
  const buttons = [...root.querySelectorAll('[data-projection]')];
  const status = root.querySelector('#ct-result-status');
  if (!cases.length || !buttons.length || !status) return;
  function select(count) {
    cases.forEach(item => { item.hidden = item.dataset.count !== count; });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.projection === count)));
    const current = cases.find(item => item.dataset.count === count);
    status.textContent = current.querySelector('figcaption span').textContent;
  }
  root.querySelector('.project-explorer').classList.add('is-interactive');
  root.querySelector('.project-selector').hidden = false;
  buttons.forEach(button => button.addEventListener('click', () => select(button.dataset.projection)));
  select('30');
})();
