document.addEventListener('DOMContentLoaded', async () => {
  try {
    const r = await fetch('/api/dashboard');
    const d = await r.json();
    if (!r.ok) throw new Error(d.error || 'No se pudo cargar');
    document.getElementById('kpiSocios').textContent = d.socios_activos ?? 0;
    document.getElementById('kpiVencen').textContent = d.membresias_vencer ?? 0;
    document.getElementById('kpiVentas').textContent = '$' + Number(d.ventas_mes || 0).toLocaleString('es-MX',{minimumFractionDigits:2});
    document.getElementById('kpiClases').textContent = d.clases_hoy ?? 0;
    const t=document.getElementById('actividad'); t.innerHTML='';
    (d.actividad||[]).forEach(x=>{const tr=document.createElement('tr'); tr.innerHTML=`<td>${x.fecha||''}</td><td>${x.usuario||''}</td><td>${x.accion||''}</td><td>${x.modulo||''}</td>`; t.appendChild(tr);});
    if(!t.children.length) t.innerHTML='<tr><td>—</td><td>—</td><td>Sin actividad registrada</td><td>—</td></tr>';
  } catch(e) {
    document.getElementById('actividad').innerHTML='<tr><td colspan="4">No se pudo consultar la base de datos.</td></tr>';
  }
});
