(() => {
  const plate = document.querySelector('.documentary-mri');
  if (!plate) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const pointer = matchMedia('(pointer: fine)');
  const button = plate.querySelector('.cinematic-control');
  if (!button) return;
  let enabled = !reduce.matches && pointer.matches;
  const reset = () => { plate.style.removeProperty('--plate-x'); plate.style.removeProperty('--plate-y'); };
  const sync = () => { button.hidden = !pointer.matches || reduce.matches; button.setAttribute('aria-pressed', String(enabled)); if (!enabled) {plate.style.setProperty('--plate-x','0deg');plate.style.setProperty('--plate-y','0deg');} else reset(); };
  plate.addEventListener('pointermove', e => {
    if (!enabled || e.pointerType === 'touch') return;
    const r = plate.getBoundingClientRect();
    plate.style.setProperty('--plate-x', ((.5-(e.clientY-r.top)/r.height)*5)+'deg');
    plate.style.setProperty('--plate-y', (((e.clientX-r.left)/r.width-.5)*9)+'deg');
  });
  plate.addEventListener('pointerleave', () => { if(enabled) reset(); });
  button.addEventListener('click', () => {enabled=!enabled;sync();});
  reduce.addEventListener('change', () => {enabled=!reduce.matches&&pointer.matches;sync();});
  sync();
})();
