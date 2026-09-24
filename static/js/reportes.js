const $=id=>document.getElementById(id);
const esc=v=>String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
let reporteActual=null;
const COLORS=['#00B4FF','#00D084','#FFB020','#FF4757','#8B5CF6','#FF6B9D','#22D3EE','#A3E635'];

function fechaParams(){const p=new URLSearchParams();if($('desde').value)p.set('desde',$('desde').value);if($('hasta').value)p.set('hasta',$('hasta').value);return p.toString()}
function canvasClear(c){const x=c.getContext('2d'),r=c.getBoundingClientRect(),d=Math.min(window.devicePixelRatio||1,2),w=Math.max(320,Math.floor(r.width||c.parentElement?.clientWidth||420)),h=280;c.style.width='100%';c.style.height=h+'px';c.width=Math.floor(w*d);c.height=Math.floor(h*d);x.setTransform(d,0,0,d,0,0);x.clearRect(0,0,w,h);x.font='12px system-ui';return[x,w,h]}
function money(n){return '$'+Number(n||0).toLocaleString('es-MX',{minimumFractionDigits:2,maximumFractionDigits:2})}
function nice(n){return Number(n||0).toLocaleString('es-MX',{maximumFractionDigits:2})}
function emptyChart(x){x.fillStyle='#8C98B3';x.font='13px system-ui';x.fillText('Sin datos para el periodo seleccionado',20,35)}

function drawAxes(x,w,h,left=55,bottom=48,top=20,right=20){
  x.strokeStyle='rgba(140,152,179,.28)';x.lineWidth=1;
  for(let i=0;i<=4;i++){const y=top+(h-top-bottom)*i/4;x.beginPath();x.moveTo(left,y);x.lineTo(w-right,y);x.stroke()}
  x.strokeStyle='rgba(140,152,179,.5)';x.beginPath();x.moveTo(left,top);x.lineTo(left,h-bottom);x.lineTo(w-right,h-bottom);x.stroke();
}

function linea(id,data,labelKey,valueKey){
  const c=$(id);if(!c)return;const [x,w,h]=canvasClear(c),a=data||[];
  if(!a.length){emptyChart(x);return}
  const vals=a.map(v=>Number(v[valueKey])||0),max=Math.max(...vals,1),min=Math.min(...vals,0),range=max-min||1,left=55,right=20,top=25,bottom=55;
  drawAxes(x,w,h,left,bottom,top,right);
  x.beginPath();
  vals.forEach((v,i)=>{const px=left+(a.length===1?(w-left-right)/2:(w-left-right)*i/(a.length-1)),py=top+(h-top-bottom)*(1-(v-min)/range);i?x.lineTo(px,py):x.moveTo(px,py)});
  x.lineTo(w-right,h-bottom);x.lineTo(left,h-bottom);x.closePath();x.fillStyle='rgba(0,180,255,.10)';x.fill();
  x.beginPath();vals.forEach((v,i)=>{const px=left+(a.length===1?(w-left-right)/2:(w-left-right)*i/(a.length-1)),py=top+(h-top-bottom)*(1-(v-min)/range);i?x.lineTo(px,py):x.moveTo(px,py)});x.strokeStyle='#00B4FF';x.lineWidth=3;x.stroke();
  vals.forEach((v,i)=>{const px=left+(a.length===1?(w-left-right)/2:(w-left-right)*i/(a.length-1)),py=top+(h-top-bottom)*(1-(v-min)/range);x.fillStyle='#00B4FF';x.beginPath();x.arc(px,py,5,0,Math.PI*2);x.fill();x.fillStyle='#F4F7FB';x.font='11px system-ui';x.textAlign='center';x.fillText(money(v),px,Math.max(13,py-10));x.fillStyle='#8C98B3';x.fillText(String(a[i][labelKey]??'').slice(0,11),px,h-24)})
}

function barras(id,data,labelKey,valueKey){
  const c=$(id);if(!c)return;const [x,w,h]=canvasClear(c),a=(data||[]).slice(0,12);
  if(!a.length){emptyChart(x);return}
  const vals=a.map(v=>Number(v[valueKey])||0),max=Math.max(...vals,1),left=55,bottom=58,top=25,right=20,gap=10,bw=Math.max(16,(w-left-right-gap*(a.length-1))/a.length);
  drawAxes(x,w,h,left,bottom,top,right);
  a.forEach((v,i)=>{const val=Number(v[valueKey])||0,bh=(h-bottom-top)*val/max,xx=left+i*(bw+gap),yy=h-bottom-bh;x.fillStyle=COLORS[i%COLORS.length];x.shadowColor=COLORS[i%COLORS.length];x.shadowBlur=10;x.fillRect(xx,yy,bw,bh);x.shadowBlur=0;x.fillStyle='#F4F7FB';x.font='11px system-ui';x.textAlign='center';x.fillText(nice(val),xx+bw/2,Math.max(14,yy-7));x.fillStyle='#8C98B3';const t=String(v[labelKey]??'Sin nombre');x.fillText(t.length>14?t.slice(0,13)+'…':t,xx+bw/2,h-24)})
}

function tabla(rows){if(!rows?.length)return '<p class="chart-info">Sin datos para el periodo seleccionado.</p>';const keys=Object.keys(rows[0]);return '<div class="table-container"><table><thead><tr>'+keys.map(k=>`<th>${esc(k.replaceAll('_',' '))}</th>`).join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+keys.map(k=>`<td>${esc(r[k])}</td>`).join('')+'</tr>').join('')+'</tbody></table></div>'}
function bloque(t,html){return `<div class="report-block"><h3>${t}</h3>${html}</div>`}
function ocultar(){document.querySelectorAll('.chart-box').forEach(e=>e.style.display='none')}
function mostrar(...ids){ids.forEach(id=>{const e=$(id);if(e)e.style.display='block'})}
function encabezado(t){$('encabezadoReporte').innerHTML=`<div class="report-header"><h2>GYMPRO</h2><p class="subtitle">Sistema Integral de Gestión de Gimnasio</p><h3>${t}</h3><p class="chart-info">Periodo: ${$('desde').value||'Inicio'} al ${$('hasta').value||'Actualidad'} · Generado: ${new Date().toLocaleString('es-MX')}</p></div>`}
function resumen(items){return `<div class="report-summary">${items.map(x=>`<div class="summary-item"><small>${x[0]}</small><strong>${x[1]}</strong></div>`).join('')}</div>`}
function renderGeneral(d){const v=d.ventas||{},i=d.inventario||{},m=d.membresias||{};const html=resumen([['Total vendido',money(v.total_ventas)],['Productos registrados',nice((i.productos||[]).length)],['Socios registrados',nice((m.clientes||[]).length)]])+bloque('1. Ventas',`<p class="chart-info">Resumen de ingresos y productos vendidos.</p>${tabla(v.productos_mas_vendidos||[])}`)+bloque('2. Inventario',`<p class="chart-info">Existencias actuales y productos en nivel mínimo.</p>${tabla(i.stock_bajo||[])}`)+bloque('3. Membresías y socios',`<p class="chart-info">Distribución de membresías y estados de los socios.</p>${tabla(m.membresias_por_tipo||[])}${tabla(m.socios_por_estado||[])}`);$('resultadoReporte').innerHTML=html}

async function generar(tipo){
  $('reportMessage').textContent='Generando reporte...';
  ocultar();
  try{
    const r=await fetch('/api/reportes/'+tipo+'?'+fechaParams());
    const d=await r.json();
    if(!r.ok)throw Error(d.detail||d.error||'No se pudo generar');
    reporteActual=d;
    encabezado(tipo==='general'?'REPORTE GENERAL':`REPORTE DE ${tipo.toUpperCase()}`);
    if(tipo==='ventas'){
      const dias=d.ventas?.ventas_por_dia||d.graficas?.ventas_por_dia||[];
      const prods=d.productos_mas_vendidos||d.ventas?.productos_mas_vendidos||d.graficas?.productos_mas_vendidos||[];
      $('resultadoReporte').innerHTML=resumen([
        ['Total vendido',money(d.total_ventas)],
        ['Días con ventas',nice(dias.length)],
        ['Productos vendidos',nice(prods.length)]
      ])+'<p class="chart-info">Este reporte contiene exclusivamente operaciones de venta.</p>'+tabla(d.data||prods);
      mostrar('boxVentas','boxProductos');
      linea('graficaVentas',dias,'periodo','total');
      barras('graficaProductos',prods,'producto','unidades');
    }else if(tipo==='inventario'){
      const rows=d.data||[];
      const low=d.inventario?.stock_bajo||d.graficas?.stock_bajo||[];
      const totalStock=rows.reduce((a,r)=>a+Number(r.stock_actual??r.stock??r.existencia??0),0);
      $('resultadoReporte').innerHTML=resumen([
        ['Productos',nice(rows.length)],
        ['Stock bajo',nice(low.length)],
        ['Existencias totales',nice(totalStock)]
      ])+'<p class="chart-info">Este reporte contiene exclusivamente información de inventario.</p>'+tabla(rows);
      mostrar('boxStock');
      barras('graficaStock',d.graficas?.stock_por_producto||[],'producto','stock');
    }else if(tipo==='membresias'){
      const rows=d.data||[];
      const mt=d.graficas?.membresias_por_tipo||[];
      const es=d.graficas?.socios_por_estado||[];
      $('resultadoReporte').innerHTML=resumen([
        ['Socios',nice(rows.length)],
        ['Tipos de membresía',nice(mt.length)],
        ['Estados',nice(es.length)]
      ])+'<p class="chart-info">Este reporte contiene exclusivamente socios y membresías.</p>'+tabla(rows);
      mostrar('boxMembresias','boxEstados');
      barras('graficaMembresias',mt,'membresia','cantidad');
      barras('graficaEstados',es,'estado','cantidad');
    }else{
      renderGeneral(d);
      mostrar('boxVentas','boxProductos','boxMembresias','boxEstados','boxStock');
      linea('graficaVentas',d.graficas?.ventas_por_dia||[],'periodo','total');
      barras('graficaProductos',d.graficas?.productos_mas_vendidos||[],'producto','unidades');
      barras('graficaMembresias',d.graficas?.membresias_por_tipo||[],'membresia','cantidad');
      barras('graficaEstados',d.graficas?.socios_por_estado||[],'estado','cantidad');
      barras('graficaStock',d.graficas?.stock_por_producto||[],'producto','stock');
    }
    $('reportMessage').textContent='Reporte generado correctamente.';
  }catch(e){
    $('reportMessage').textContent='Error: '+e.message;
    $('resultadoReporte').innerHTML='';
  }
}

function imprimir(){if(!reporteActual){alert('Primero genera un reporte.');return}const blocks=[...document.querySelectorAll('.report-print-area')].filter(e=>getComputedStyle(e).display!=='none');const contenido=blocks.map(e=>{const c=e.cloneNode(true);e.querySelectorAll('canvas').forEach((orig,i)=>{const clone=c.querySelectorAll('canvas')[i];if(!clone)return;const img=document.createElement('img');img.src=orig.toDataURL('image/png');img.style.width='100%';img.style.height='280px';img.style.objectFit='contain';clone.replaceWith(img)});return c.outerHTML}).join('');const w=window.open('','_blank','width=1100,height=800');w.document.write(`<!doctype html><html lang="es"><head><meta charset="utf-8"><title>GYMPRO - Reporte</title><style>@page{size:A4;margin:16mm}*{box-sizing:border-box}body{font-family:Arial,sans-serif;color:#182033;background:#fff;margin:0}h2{font-size:26px;margin:0 0 3px}h3{font-size:16px;margin:18px 0 8px;text-transform:uppercase;letter-spacing:.5px}.subtitle,.chart-info{color:#657089;font-size:11px}.report-header{border-bottom:2px solid #00B4FF;padding-bottom:12px;margin-bottom:18px}.report-block{page-break-inside:avoid;border-top:1px solid #d8dee9;padding:13px 0}.report-summary{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:12px 0 18px}.summary-item{border:1px solid #d8dee9;border-radius:8px;padding:10px}.summary-item small{display:block;color:#657089;text-transform:uppercase;font-size:9px}.summary-item strong{display:block;font-size:18px;margin-top:5px}table{width:100%;border-collapse:collapse;margin:10px 0 18px;font-size:10px}th,td{border:1px solid #cfd6e2;padding:6px;text-align:left}th{background:#eef3f8;text-transform:uppercase;font-size:9px}article{page-break-inside:avoid;margin:12px 0}.chart-box{page-break-inside:avoid}.chart-box h3{margin-top:4px}img{max-width:100%;display:block;margin:auto}</style></head><body>${contenido}</body></html>`);w.document.close();setTimeout(()=>{w.focus();w.print()},400)}

document.addEventListener('DOMContentLoaded',()=>{document.querySelectorAll('.generar').forEach(b=>b.addEventListener('click',()=>generar(b.dataset.tipo)));$('generarTodo').onclick=()=>generar('general');$('imprimirReporte').onclick=imprimir;ocultar()});
