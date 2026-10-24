(() => {
  const rotor = document.getElementById('ct-rotor');
  const play = document.getElementById('scan-play');
  const reset = document.getElementById('scan-reset');
  const angleOutput = document.getElementById('scan-angle');
  const controls = document.querySelector('.scanner-controls');
  if (!rotor || !play || !reset || !angleOutput || !controls) return;
  let running = false, angle = 0, previous = null, frame = null;
  function render() {
    rotor.setAttribute('transform', `rotate(${angle} 240 195)`);
    angleOutput.value = `${Math.floor(angle)}°`;
  }
  function tick(time) {
    if (!running) return;
    if (previous !== null) angle = (angle + Math.min(time - previous, 80) * 0.035) % 360;
    previous = time; render(); frame = requestAnimationFrame(tick);
  }
  function stop() {
    running = false; cancelAnimationFrame(frame); previous = null;
    play.textContent = play.dataset.play;
    play.setAttribute('aria-pressed', 'false');
  }
  play.addEventListener('click', () => {
    if (running) { stop(); return; }
    running = true; play.textContent = play.dataset.pause;
    play.setAttribute('aria-pressed', 'true'); frame = requestAnimationFrame(tick);
  });
  reset.addEventListener('click', () => { stop(); angle = 0; render(); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
  controls.hidden = false;
})();
