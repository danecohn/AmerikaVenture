'use strict';
const tick=()=>{document.querySelector('#clock').textContent=new Intl.DateTimeFormat(undefined,{weekday:'short',month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}).format(new Date());};tick();setInterval(tick,30000);
