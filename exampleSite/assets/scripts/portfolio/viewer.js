(() => {
  const controls = document.querySelector('.viewer-controls');
  const image = document.getElementById('ct-image');
  const slider = document.getElementById('ct-brightness');
  const output = document.getElementById('ct-brightness-value');
  const reset = document.getElementById('ct-reset');
  if (!controls || !image || !slider || !output || !reset) return;
  const update = () => {
    image.style.filter = `brightness(${Number(slider.value) / 100})`;
    output.value = `${slider.value}%`;
  };
  slider.addEventListener('input', update);
  reset.addEventListener('click', () => { slider.value = '100'; update(); });
  controls.hidden = false;
})();
