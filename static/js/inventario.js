let productos=[];
const $=id=>document.getElementById(id);
const esc=v=>String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
async function cargarCategorias(){
  try{const r=await fetch('/api/categorias-productos');const d=await r.json();if(!r.ok)throw Error(d.error);const s=$('id_categoria');if(!s)return;s.innerHTML='<option value="">Seleccione categoría</option>';(d.data||[]).forEach(c=>s.insertAdjacentHTML('beforeend',`<option value="${c.id_categoria}">${esc(c.nombre)}</option>`));}catch(e){console.warn(e);}
}
async function cargarProductos(){
  const q=$('buscarProducto')?.value.trim()||'';const estado=$('filtroProducto')?.value||'';const stock=$('filtroStock')?.value||'';
  try{const r=await fetch(`/api/productos?q=${encodeURIComponent(q)}&estado=${encodeURIComponent(estado)}&stock=${encodeURIComponent(stock)}`);const d=await r.json();if(!r.ok)throw Error(d.error);productos=d.data||[];render();}
  catch(e){const t=$('tablaProductos');if(t)t.innerHTML=`<tr><td colspan="7">${esc(e.message||'Error al consultar productos')}</td></tr>`;}
}
function render(){const t=$('tablaProductos');if(!t)return;t.innerHTML='';if(!productos.length){t.innerHTML='<tr><td colspan="7">No hay productos que coincidan con el filtro.</td></tr>';return;}
  productos.forEach(p=>{const bajo=Number(p.stock_actual||0)<=Number(p.stock_minimo||0);const tr=document.createElement('tr');tr.innerHTML=`<td>${esc(p.producto)}</td><td>${esc(p.categoria||p.id_categoria||'')}</td><td>$${Number(p.precio_venta||0).toLocaleString('es-MX',{minimumFractionDigits:2})}</td><td>${p.stock_actual??0}</td><td>${p.stock_minimo??0}</td><td>${esc(p.estado||'Activo')}</td><td><button type="button" data-edit="${p.id_producto}">Editar</button> <button type="button" data-del="${p.id_producto}">Dar de baja</button></td>`;if(bajo)tr.classList.add('stock-bajo');t.appendChild(tr);});
}
function editar(id){const p=productos.find(x=>String(x.id_producto)===String(id));if(!p)return;$('id_producto').value=p.id_producto??'';$('producto').value=p.producto??'';$('id_categoria').value=p.id_categoria??'';$('descripcion').value=p.descripcion??'';$('precio_venta').value=p.precio_venta??'';$('stock_actual').value=p.stock_actual??0;$('stock_minimo').value=p.stock_minimo??0;$('estado').value=p.estado??'Activo';document.querySelector('#productoForm')?.scrollIntoView({behavior:'smooth',block:'start'});}
$('buscarProducto')?.addEventListener('input',cargarProductos);$('filtroProducto')?.addEventListener('change',cargarProductos);$('filtroStock')?.addEventListener('change',cargarProductos);
$('nuevoProducto')?.addEventListener('click',()=>{$('productoForm')?.reset();if($('id_producto'))$('id_producto').value='';});
$('tablaProductos')?.addEventListener('click',e=>{const edit=e.target.dataset.edit,del=e.target.dataset.del;if(edit)editar(edit);if(del&&confirm('¿Dar de baja este producto?'))fetch('/api/productos/'+del,{method:'DELETE'}).then(async r=>{if(!r.ok){const d=await r.json();throw Error(d.error);}cargarProductos();}).catch(err=>alert(err.message));});
$('productoForm')?.addEventListener('submit',async e=>{e.preventDefault();const data=Object.fromEntries(new FormData(e.target));const id=data.id_producto;delete data.id_producto;try{const r=await fetch(id?'/api/productos/'+id:'/api/productos',{method:id?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});const d=await r.json();if(!r.ok)throw Error(d.error);$('productoMessage').textContent='Producto guardado correctamente en la base de datos.';e.target.reset();$('id_producto').value='';await cargarProductos();}catch(err){$('productoMessage').textContent=err.message||'No se pudo guardar.';}});
document.addEventListener('DOMContentLoaded',()=>{cargarCategorias();cargarProductos();});
