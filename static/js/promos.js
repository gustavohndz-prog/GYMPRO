async function cargarPromos(){
  try{
    const r=await fetch('/api/promociones');
    const d=await r.json();
    if(!r.ok) throw Error(d.error||'No se pudieron consultar las promociones');
    const tb=document.querySelector('table tbody');
    if(!tb)return;
    tb.innerHTML='';
    (d.data||[]).forEach(x=>{
      const tr=document.createElement('tr');
      tr.innerHTML=`<td>${x.nombre??''}</td><td>${x.descripcion??''}</td><td>${x.tipo??''}</td><td>${x.valor??''}</td><td>${x.fecha_inicio??''}</td><td>${x.fecha_fin??''}</td><td>${x.estado??''}</td><td>—</td>`;
      tb.appendChild(tr);
    });
  }catch(e){
    const m=document.getElementById('promoMessage');
    if(m)m.textContent=e.message;
  }
}

document.addEventListener('DOMContentLoaded',()=>{
  cargarPromos();
  const form=document.getElementById('promoForm');
  form?.addEventListener('submit',async e=>{
    e.preventDefault();
    const message=document.getElementById('promoMessage');
    const data=Object.fromEntries(new FormData(form));
    try{
      const r=await fetch('/api/promociones',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
      const d=await r.json().catch(()=>({}));
      if(!r.ok) throw Error(d.detail||d.error||'No se pudo guardar la promoción.');
      message.textContent='Promoción guardada correctamente.';
      form.reset();
      await cargarPromos();
    }catch(err){
      message.textContent=err.message;
    }
  });
});
