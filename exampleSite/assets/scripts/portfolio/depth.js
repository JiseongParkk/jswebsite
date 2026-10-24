(() => {
 const stage=document.getElementById('mri-stage');
 if(!stage)return;
 const object=stage.querySelector('.mri-object'), controls=document.querySelector('.mri-controls'), toggle=document.getElementById('mri-motion'), reset=document.getElementById('mri-reset'), hint=document.querySelector('.mri-hint');
 const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
 let enabled=!reduced.matches,x=0,y=0;
 const render=()=>{object.style.setProperty('--rx',x+'deg');object.style.setProperty('--ry',y+'deg');};
 const center=()=>{x=0;y=0;render();};
 const sync=()=>{toggle.setAttribute('aria-pressed',String(enabled));stage.tabIndex=enabled?0:-1;hint.hidden=!enabled; if(!enabled)center();};
 controls.hidden=false;sync();
 stage.addEventListener('pointermove',e=>{if(!enabled||e.pointerType==='touch')return;const r=stage.getBoundingClientRect();x=(.5-(e.clientY-r.top)/r.height)*12;y=((e.clientX-r.left)/r.width-.5)*16;render();});
 stage.addEventListener('pointerleave',center);
 stage.addEventListener('keydown',e=>{if(!enabled)return;if(!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Home'].includes(e.key))return;e.preventDefault();if(e.key==='Home'){center();return;}if(e.key==='ArrowUp')x-=2;if(e.key==='ArrowDown')x+=2;if(e.key==='ArrowLeft')y-=2;if(e.key==='ArrowRight')y+=2;x=Math.max(-8,Math.min(8,x));y=Math.max(-10,Math.min(10,y));render();});
 stage.addEventListener('blur',center);reset.addEventListener('click',center);
 toggle.addEventListener('click',()=>{enabled=!enabled&&!reduced.matches;sync();});
 reduced.addEventListener('change',()=>{enabled=!reduced.matches;sync();});
})();
