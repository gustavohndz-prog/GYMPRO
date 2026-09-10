const carrito = [];

const $ = id => document.getElementById(id);
const esc = v => String(v ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));

function totalCarrito(){
  return carrito.reduce((s,x)=>s + Number(x.precio)*Number(x.cantidad), 0);
}

function pintar(){
  const t = $('carrito');
  if(!t) return;
  t.innerHTML = '';
  carrito.forEach(x=>{
    const sub = Number(x.precio) * Number(x.cantidad);
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${esc(x.nombre)}</td><td>${x.cantidad}</td><td>$${Number(x.precio).toFixed(2)}</td><td>$${sub.toFixed(2)}</td>`;
    t.appendChild(tr);
  });
  if($('totalVenta')) $('totalVenta').textContent = 'Total: $' + totalCarrito().toFixed(2);
}

function renderProductos(lista){
  const box = $('listaProductos');
  if(!box) return;
  box.innerHTML = '';
  if(!lista.length){
    box.innerHTML = '<p>No hay productos disponibles.</p>';
    return;
  }
  lista.forEach(x=>{
    const stock = Number(x.stock_actual ?? 0);
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'producto';
    b.dataset.id = x.id_producto;
    b.dataset.precio = x.precio_venta ?? 0;
    b.dataset.nombre = x.producto ?? x.nombre ?? '';
    b.disabled = stock <= 0;
    b.innerHTML = `${esc(b.dataset.nombre)} — $${Number(b.dataset.precio).toFixed(2)} <small>Stock: ${stock}</small>`;
    box.appendChild(b);
  });
}

async function cargarProductos(){
  try{
    const q = ($('buscarVenta')?.value || '').trim();
    const r = await fetch('/api/productos?q=' + encodeURIComponent(q));
    const d = await r.json();
    if(!r.ok) throw Error(d.error || 'No se pudieron cargar los productos.');
    renderProductos((d.data || []).filter(x => Number(x.stock_actual ?? 0) > 0));
  }catch(e){
    const box = $('listaProductos');
    if(box) box.innerHTML = `<p>${esc(e.message)}</p>`;
  }
}

async function cobrar(){
  const msg = $('ventaMessage');
  if(!carrito.length){ if(msg) msg.textContent = 'Agrega al menos un producto.'; return; }

  const metodo = ($('metodoPago')?.value || '').toLowerCase();
  const clienteTexto = ($('clienteVenta')?.value || '').trim();
  if(msg) msg.textContent = 'Registrando venta...';

  try{
    const r = await fetch('/api/ventas', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        cliente: clienteTexto || null,
        metodo_pago: metodo,
        detalles: carrito.map(x=>({id:Number(x.id), cantidad:Number(x.cantidad), precio:Number(x.precio)}))
      })
    });
    const d = await r.json().catch(()=>({}));
    if(!r.ok) throw Error(d.error || 'No se pudo registrar la venta.');
    if(msg) msg.textContent = `Venta #${d.id_venta} registrada correctamente. Total: $${Number(d.total).toFixed(2)}`;
    carrito.length = 0;
    pintar();
    if($('clienteVenta')) $('clienteVenta').value = '';
    await cargarProductos();
  }catch(e){
    if(msg) msg.textContent = e.message;
  }
}

document.addEventListener('click', e=>{
  const b = e.target.closest('.producto');
  if(!b || b.disabled) return;
  const id = String(b.dataset.id);
  const x = carrito.find(p=>String(p.id) === id);
  if(x) x.cantidad++;
  else carrito.push({id, nombre:b.dataset.nombre, precio:Number(b.dataset.precio), cantidad:1});
  pintar();
});

document.addEventListener('DOMContentLoaded', ()=>{
  cargarProductos();
  $('buscarVenta')?.addEventListener('input', cargarProductos);
  $('cobrar')?.addEventListener('click', cobrar);
});
