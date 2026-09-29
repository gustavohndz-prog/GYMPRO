# GYMPRO – Sistema Integral de Gestión de Gimnasio

Versión funcional para MySQL/MariaDB. Conserva la estructura visual y el CSS original; la configuración del servidor queda a cargo de la empresa.

## Inicio de sesión
El usuario ya **no selecciona un rol**. Escribe únicamente usuario y contraseña. GYMPRO consulta `usuarios` y obtiene automáticamente el rol almacenado en la base de datos. Después redirige al área correspondiente.

## Módulos
- Dashboard con KPIs y gráficas.
- Registro y administración de socios.
- Consulta de clientes.
- Membresías y catálogo.
- Clases, cupos y cancelaciones.
- Control de acceso.
- Punto de venta e inventario.
- Proveedores.
- Promociones.
- Reportes independientes y reporte general.
- Usuarios.
- Auditoría.
- Configuración.
- Portal del cliente: perfil, membresía, pagos, asistencias, clases y promociones.

## Reportes
1. **Ventas:** únicamente ventas, total vendido, ventas por día y productos vendidos.
2. **Inventario:** únicamente productos, existencias y stock bajo.
3. **Membresías:** únicamente socios, membresías y estados.
4. **General:** consolida los tres anteriores.

El botón **Imprimir reporte** abre una hoja formal independiente, sin menú lateral ni elementos de navegación. Las gráficas se convierten a imagen para que también aparezcan al imprimir o guardar como PDF.

## Configuración local
1. Inicia MySQL desde XAMPP.
2. Verifica la base `gimnasio`.
3. Instala dependencias: `pip install -r requirements.txt`.
4. Ejecuta: `python gym.py`.
5. Abre `http://127.0.0.1:5000/`.

## Configuración de base de datos
La conexión de GYMPRO se configura en `db.py`. La infraestructura y configuración del servidor donde se publique el sistema quedan fuera del proyecto.

## Roles
- `recepcion`: registro de socios, consulta, acceso, clases/cupos y POS.
- `gerente`: membresías, inventario, proveedores, promociones y reportes.
- `dueno`: reportes, usuarios, auditoría, configuración y vista global.
- `cliente`: portal personal.

Las rutas están protegidas en Flask; ocultar un botón no es el mecanismo de seguridad.

## Despliegue en la nube (PostgreSQL)
El motor se elige por variables de entorno (no hay que tocar el codigo):
- **PostgreSQL:** define `DATABASE_URL` (p. ej. `postgresql://user:pass@host:5432/gimnasio?sslmode=require`) o bien `GYMPRO_DB_ENGINE=postgres` con `GYMPRO_DB_HOST/PORT/USER/PASSWORD/NAME` (y opcional `GYMPRO_DB_SSLMODE`).
- **MySQL/MariaDB (local con XAMPP):** sin `DATABASE_URL`, usa `GYMPRO_DB_*` como antes.
- Siempre define `SECRET_KEY`. Comando de arranque: `gunicorn gym:app` (ver `Procfile`).
- Al migrar el esquema a PostgreSQL convierte `TINYINT(1)` a `SMALLINT` (no `BOOLEAN`) y usa columnas `SERIAL`/`IDENTITY` para los ids; el codigo espera `estado` como 1/0 o texto.
