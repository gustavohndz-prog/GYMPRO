document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('proveedorForm');
    const tabla = document.querySelector('table tbody');
    const buscar = document.getElementById('buscarProveedor');
    const mensaje = document.getElementById('mensajeProveedor');

    function escapeHtml(value) {
        return String(value ?? '')
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    }

    function mostrarMensaje(texto, ok = false) {
        if (!mensaje) return;
        mensaje.textContent = texto;
        mensaje.style.display = 'block';
        mensaje.style.fontWeight = '600';
    }

    async function cargarProveedores() {
        try {
            const r = await fetch('/api/proveedores');
            const d = await r.json();
            if (!r.ok) throw new Error(d.error || 'No se pudieron cargar los proveedores');

            tabla.innerHTML = '';
            (d.data || []).forEach(x => {
                const tr = document.createElement('tr');
                tr.dataset.search = `${x.nombre ?? ''} ${x.producto ?? x.productos ?? ''} ${x.contacto ?? x.nombre_contacto ?? ''} ${x.telefono ?? ''} ${x.email ?? ''}`.toLowerCase();
                tr.innerHTML = `
                    <td>${escapeHtml(x.nombre)}</td>
                    <td>${escapeHtml(x.producto ?? x.productos ?? x.producto_abastece)}</td>
                    <td>${escapeHtml(x.contacto ?? x.nombre_contacto ?? x.persona_contacto)}</td>
                    <td>${escapeHtml(x.telefono)}</td>
                    <td>${escapeHtml(x.email ?? x.correo)}</td>
                    <td>${escapeHtml(x.estado ?? 'Activo')}</td>
                    <td>—</td>`;
                tabla.appendChild(tr);
            });
        } catch (e) {
            mostrarMensaje(e.message, false);
        }
    }

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const payload = {
                nombre: document.getElementById('provNombre').value.trim(),
                producto: document.getElementById('provProducto').value.trim(),
                contacto: document.getElementById('provContacto').value.trim(),
                telefono: document.getElementById('provTelefono').value.trim(),
                email: document.getElementById('provEmail').value.trim(),
                direccion: document.getElementById('provDireccion').value.trim()
            };

            if (!payload.nombre || !payload.producto) {
                mostrarMensaje('Nombre y producto son obligatorios.');
                return;
            }

            try {
                const r = await fetch('/api/proveedores', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const d = await r.json();
                if (!r.ok) throw new Error(d.detail || d.error || 'No se pudo guardar el proveedor');

                mostrarMensaje('Proveedor guardado correctamente.', true);
                form.reset();
                await cargarProveedores();
            } catch (e) {
                mostrarMensaje(`Error: ${e.message}`);
            }
        });
    }

    if (buscar) {
        buscar.addEventListener('input', () => {
            const q = buscar.value.trim().toLowerCase();
            tabla.querySelectorAll('tr').forEach(tr => {
                tr.style.display = !q || (tr.dataset.search || '').includes(q) ? '' : 'none';
            });
        });
    }

    cargarProveedores();
});
