-- Script convertido para PostgreSQL
-- Base de datos: gimnasio

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE roles (
  id_rol SERIAL PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL,
  descripcion TEXT DEFAULT NULL,
  activo SMALLINT DEFAULT 1
);

-- Volcado de datos para la tabla `roles`
INSERT INTO roles (id_rol, nombre, descripcion, activo) VALUES
(1, 'recepcion', 'Personal encargado de recepción y atención de socios', 1),
(2, 'gerente', 'Administrador y gerente del gimnasio', 1),
(3, 'dueno', 'Propietario del gimnasio', 1),
(4, 'cliente', 'Usuario cliente del gimnasio', 1);

SELECT setval('roles_id_rol_seq', (SELECT MAX(id_rol) FROM roles));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE usuarios (
  id_usuario SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  usuario VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  id_rol INTEGER NOT NULL REFERENCES roles(id_rol),
  activo SMALLINT DEFAULT 1,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

-- Volcado de datos para la tabla `usuarios`
INSERT INTO usuarios (id_usuario, nombre, usuario, password, id_rol, activo, fecha_creacion, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 'Administrador Recepción', 'recepcion01', 'recepcion123', 1, 1, '2026-09-01 19:02:44', 1, NULL, NULL),
(2, 'Administrador Gerente', 'gerente01', 'gerente123', 2, 1, '2026-09-01 19:02:44', 2, NULL, NULL),
(3, 'Propietario Gimnasio', 'dueno01', 'dueno123', 3, 1, '2026-09-01 19:02:44', 3, NULL, NULL),
(4, 'Cliente Demo', 'cliente01', 'cliente123', 4, 1, '2026-09-01 19:02:44', 4, NULL, NULL);

SELECT setval('usuarios_id_usuario_seq', (SELECT MAX(id_usuario) FROM usuarios));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `beneficios`
--

CREATE TABLE beneficios (
  id_beneficio SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT DEFAULT NULL,
  estado SMALLINT DEFAULT 1,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

-- Volcado de datos para la tabla `beneficios`
INSERT INTO beneficios (id_beneficio, nombre, descripcion, estado, fecha_creacion, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 'Acceso al gimnasio', 'Acceso general a las instalaciones', 1, '2026-09-01 19:02:44', 2, NULL, NULL),
(2, 'Acceso a clases', 'Acceso a clases disponibles', 1, '2026-09-01 19:02:44', 2, NULL, NULL),
(3, 'Descuento en productos', 'Descuento en productos seleccionados', 1, '2026-09-01 19:02:44', 2, NULL, NULL),
(4, 'Evaluación física', 'Evaluación física inicial', 1, '2026-09-01 19:02:44', 2, NULL, NULL),
(5, 'Entrenamiento personalizado', 'Sesión personalizada con entrenador', 1, '2026-09-01 19:02:44', 2, NULL, NULL);

SELECT setval('beneficios_id_beneficio_seq', (SELECT MAX(id_beneficio) FROM beneficios));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `membresias`
--

CREATE TABLE membresias (
  id_membresia SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT DEFAULT NULL,
  duracion_dias INTEGER NOT NULL,
  precio NUMERIC(10,2) NOT NULL,
  estado VARCHAR(20) DEFAULT 'ACTIVA' CHECK (UPPER(estado) IN ('ACTIVA','INACTIVA')),
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

-- Volcado de datos para la tabla `membresias`
INSERT INTO membresias (id_membresia, nombre, descripcion, duracion_dias, precio, estado, fecha_creacion, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 'Mensual', 'Acceso al gimnasio durante 30 días', 30, 500.00, 'ACTIVA', '2026-09-01 19:02:44', 2, NULL, NULL),
(2, 'Trimestral', 'Acceso al gimnasio durante 3 meses', 90, 1350.00, 'ACTIVA', '2026-09-01 19:02:44', 2, NULL, NULL),
(3, 'Semestral', 'Acceso al gimnasio durante 6 meses', 180, 2400.00, 'ACTIVA', '2026-09-01 19:02:44', 2, NULL, NULL),
(4, 'Anual', 'Acceso al gimnasio durante 12 meses', 365, 4200.00, 'ACTIVA', '2026-09-01 19:02:44', 2, NULL, NULL),
(5, 'Premium', 'Membresía premium con beneficios adicionales', 30, 750.00, 'ACTIVA', '2026-09-01 19:02:44', 2, NULL, NULL);

SELECT setval('membresias_id_membresia_seq', (SELECT MAX(id_membresia) FROM membresias));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `membresia_beneficio`
--

CREATE TABLE membresia_beneficio (
  id_membresia INTEGER REFERENCES membresias(id_membresia) ON DELETE CASCADE,
  id_beneficio INTEGER REFERENCES beneficios(id_beneficio) ON DELETE CASCADE,
  PRIMARY KEY (id_membresia, id_beneficio)
);

INSERT INTO membresia_beneficio (id_membresia, id_beneficio) VALUES
(1, 1),
(2, 1),
(2, 2),
(3, 1),
(3, 2),
(3, 3),
(4, 1),
(4, 2),
(4, 3),
(4, 4),
(5, 1),
(5, 2),
(5, 3),
(5, 4),
(5, 5);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE clientes (
  id_cliente SERIAL PRIMARY KEY,
  no_socio VARCHAR(30) NOT NULL UNIQUE,
  nombre VARCHAR(100) NOT NULL,
  apellido VARCHAR(100) NOT NULL,
  fecha_nacimiento DATE DEFAULT NULL,
  genero VARCHAR(20) CHECK (UPPER(genero) IN ('FEMENINO','MASCULINO','OTRO')),
  telefono VARCHAR(20) DEFAULT NULL,
  email VARCHAR(150) DEFAULT NULL,
  direccion VARCHAR(255) DEFAULT NULL,
  fecha_ingreso DATE NOT NULL,
  id_membresia INTEGER NOT NULL REFERENCES membresias(id_membresia),
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

-- Volcado de datos para la tabla `clientes`
INSERT INTO clientes (id_cliente, no_socio, nombre, apellido, fecha_nacimiento, genero, telefono, email, direccion, fecha_ingreso, id_membresia, fecha_creacion, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 'SOC-0001', 'Carlos', 'Ramírez', '1998-05-12', 'MASCULINO', '5551000001', 'carlos.ramirez@email.com', 'Av. Central 101', '2026-09-01', 1, '2026-09-01 19:02:45', 1, NULL, NULL),
(2, 'SOC-0002', 'Mariana', 'López', '1997-09-22', 'FEMENINO', '5551000002', 'mariana.lopez@email.com', 'Calle Reforma 205', '2026-09-01', 2, '2026-09-01 19:02:45', 1, NULL, NULL),
(3, 'SOC-0003', 'Luis', 'Hernández', '1995-02-18', 'MASCULINO', '5551000003', 'luis.hernandez@email.com', 'Av. Hidalgo 305', '2026-09-01', 3, '2026-09-01 19:02:45', 1, NULL, NULL),
(4, 'SOC-0004', 'Sofía', 'Martínez', '2000-11-03', 'FEMENINO', '5551000004', 'sofia.martinez@email.com', 'Calle Juárez 405', '2026-09-01', 5, '2026-09-01 19:02:45', 1, NULL, NULL),
(5, 'SOC-0005', 'Diego', 'García', '1994-07-30', 'MASCULINO', '5551000005', 'diego.garcia@email.com', 'Av. Universidad 505', '2026-09-01', 4, '2026-09-01 19:02:45', 1, NULL, NULL),
(6, '15', 'gabriel', 'lopez', NULL, 'FEMENINO', '5589563490', 'gabri@gmail.com', 'san miguel llano grande', '2026-09-02', 1, '2026-09-02 10:39:48', NULL, NULL, NULL);

SELECT setval('clientes_id_cliente_seq', (SELECT MAX(id_cliente) FROM clientes));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias_productos`
--

CREATE TABLE categorias_productos (
  id_categoria SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT DEFAULT NULL,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

INSERT INTO categorias_productos (id_categoria, nombre, descripcion, fecha_creacion, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 'Bebidas', 'Bebidas para consumo', '2026-09-01 19:03:27', 2, NULL, NULL),
(2, 'Suplementos', 'Suplementos deportivos', '2026-09-01 19:03:27', 2, NULL, NULL),
(3, 'Accesorios', 'Accesorios para entrenamiento', '2026-09-01 19:03:27', 2, NULL, NULL),
(4, 'Ropa', 'Ropa deportiva', '2026-09-01 19:03:27', 2, NULL, NULL);

SELECT setval('categorias_productos_id_categoria_seq', (SELECT MAX(id_categoria) FROM categorias_productos));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE productos (
  id_producto SERIAL PRIMARY KEY,
  id_categoria INTEGER NOT NULL REFERENCES categorias_productos(id_categoria),
  nombre VARCHAR(150) NOT NULL,
  descripcion TEXT DEFAULT NULL,
  precio_venta NUMERIC(10,2) NOT NULL,
  stock_actual INTEGER DEFAULT 0,
  stock_minimo INTEGER DEFAULT 0,
  estado SMALLINT DEFAULT 1,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

INSERT INTO productos (id_producto, id_categoria, nombre, descripcion, precio_venta, stock_actual, stock_minimo, estado, fecha_creacion, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 1, 'Agua Natural', 'Botella de agua de 600 ml', 20.00, 50, 10, 1, '2026-09-01 19:03:27', 2, NULL, NULL),
(2, 1, 'Bebida Isotónica', 'Bebida deportiva', 35.00, 39, 10, 1, '2026-09-01 19:03:27', 2, NULL, NULL),
(3, 2, 'Proteína Whey', 'Proteína en polvo', 900.00, 14, 5, 1, '2026-09-01 19:03:27', 2, NULL, NULL),
(4, 3, 'Guantes de Entrenamiento', 'Guantes para entrenamiento', 250.00, 19, 5, 1, '2026-09-01 19:03:27', 2, NULL, NULL),
(5, 4, 'Playera Deportiva', 'Playera deportiva del gimnasio', 350.00, 25, 5, 1, '2026-09-01 19:03:27', 2, NULL, NULL),
(6, 2, 'creatina', 'creatina de 550 gramos sabor mora', 300.00, 6, 5, 0, '2026-09-03 10:05:45', NULL, NULL, NULL);

SELECT setval('productos_id_producto_seq', (SELECT MAX(id_producto) FROM productos));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proveedores`
--

CREATE TABLE proveedores (
  id_proveedor SERIAL PRIMARY KEY,
  nombre VARCHAR(150) NOT NULL,
  producto VARCHAR(150) DEFAULT NULL,
  contacto VARCHAR(100) DEFAULT NULL,
  telefono VARCHAR(20) DEFAULT NULL,
  email VARCHAR(150) DEFAULT NULL,
  direccion VARCHAR(255) DEFAULT NULL,
  estado SMALLINT DEFAULT 1,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

INSERT INTO proveedores (id_proveedor, nombre, producto, contacto, telefono, email, direccion, estado, fecha_creacion, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 'Distribuidora Fitness', 'Proteína Whey', 'Roberto Sánchez', '5553000001', 'ventas@fitness.com', 'Av. Industrial 100', 1, '2026-09-01 19:03:27', 2, NULL, NULL),
(2, 'Bebidas Deportivas MX', 'Bebidas isotónicas', 'Laura Pérez', '5553000002', 'ventas@bebidasmx.com', 'Av. Comercial 200', 1, '2026-09-01 19:03:27', 2, NULL, NULL),
(3, 'Accesorios Gym MX', 'Accesorios deportivos', 'Jorge Mendoza', '5553000003', 'ventas@accesoriosgym.com', 'Calle Industria 300', 1, '2026-09-01 19:03:27', 2, NULL, NULL),
(4, 'Creatina MX', 'Creatina', 'Juan Mendoza', '5534678903', 'jum@gmail.com', 'Puebla Estado de Mexico', 1, '2026-09-08 10:58:55', NULL, NULL, NULL),
(5, 'Ropa Deportiva MX', 'Ropa Deportiva', 'Usiel Martinez', '5546789054', 'ropasdepor@rp.com', 'San Luis Potosi', 1, '2026-09-08 11:04:56', NULL, NULL, NULL);

SELECT setval('proveedores_id_proveedor_seq', (SELECT MAX(id_proveedor) FROM proveedores));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `compras`
--

CREATE TABLE compras (
  id_compra SERIAL PRIMARY KEY,
  id_proveedor INTEGER NOT NULL REFERENCES proveedores(id_proveedor),
  fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  total NUMERIC(10,2) NOT NULL,
  metodo_pago VARCHAR(30) CHECK (UPPER(metodo_pago) IN ('EFECTIVO','TARJETA','TRANSFERENCIA')),
  observaciones TEXT DEFAULT NULL,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

INSERT INTO compras (id_compra, id_proveedor, fecha_compra, total, metodo_pago, observaciones, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 1, '2026-09-01 19:03:29', 1000.00, 'TRANSFERENCIA', 'Compra inicial de inventario', 2, NULL, NULL),
(2, 2, '2026-09-01 19:03:30', 500.00, 'EFECTIVO', 'Compra de bebidas', 2, NULL, NULL);

SELECT setval('compras_id_compra_seq', (SELECT MAX(id_compra) FROM compras));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalles_compra`
--

CREATE TABLE detalles_compra (
  id_detalle_compra SERIAL PRIMARY KEY,
  id_compra INTEGER NOT NULL REFERENCES compras(id_compra) ON DELETE CASCADE,
  id_producto INTEGER NOT NULL REFERENCES productos(id_producto),
  cantidad INTEGER NOT NULL,
  precio_unitario NUMERIC(10,2) NOT NULL,
  subtotal NUMERIC(10,2) NOT NULL
);

INSERT INTO detalles_compra (id_detalle_compra, id_compra, id_producto, cantidad, precio_unitario, subtotal) VALUES
(1, 2, 3, 5, 600.00, 3000.00);

SELECT setval('detalles_compra_id_detalle_compra_seq', (SELECT MAX(id_detalle_compra) FROM detalles_compra));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ventas`
--

CREATE TABLE ventas (
  id_venta SERIAL PRIMARY KEY,
  id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
  id_cliente INTEGER DEFAULT NULL REFERENCES clientes(id_cliente),
  fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  total NUMERIC(10,2) NOT NULL,
  metodo_pago VARCHAR(30) CHECK (UPPER(metodo_pago) IN ('EFECTIVO','TARJETA','TRANSFERENCIA')),
  estado VARCHAR(30) DEFAULT 'PAGADA' CHECK (UPPER(estado) IN ('PAGADA','CANCELADA','PENDIENTE','')),
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

INSERT INTO ventas (id_venta, id_usuario, id_cliente, fecha_venta, total, metodo_pago, estado, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 1, 1, '2026-09-01 19:03:30', 55.00, 'EFECTIVO', 'PAGADA', 1, NULL, NULL),
(2, 1, 2, '2026-09-01 19:03:30', 850.00, 'TARJETA', 'PAGADA', 1, NULL, NULL),
(13, 1, NULL, '2026-09-03 10:15:56', 520.00, 'EFECTIVO', '', NULL, NULL, NULL),
(14, 1, 6, '2026-09-03 10:39:39', 935.00, 'EFECTIVO', '', NULL, NULL, NULL);

SELECT setval('ventas_id_venta_seq', (SELECT MAX(id_venta) FROM ventas));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalles_venta`
--

CREATE TABLE detalles_venta (
  id_detalle_venta SERIAL PRIMARY KEY,
  id_venta INTEGER NOT NULL REFERENCES ventas(id_venta) ON DELETE CASCADE,
  id_producto INTEGER NOT NULL REFERENCES productos(id_producto),
  cantidad INTEGER NOT NULL,
  precio_unitario NUMERIC(10,2) NOT NULL,
  descuento NUMERIC(10,2) DEFAULT 0.00,
  subtotal NUMERIC(10,2) NOT NULL
);

INSERT INTO detalles_venta (id_detalle_venta, id_venta, id_producto, cantidad, precio_unitario, descuento, subtotal) VALUES
(1, 1, 1, 1, 20.00, 0.00, 20.00),
(2, 2, 3, 1, 850.00, 0.00, 850.00),
(3, 13, 6, 1, 270.00, 0.00, 270.00),
(4, 13, 4, 1, 250.00, 0.00, 250.00),
(5, 14, 2, 1, 35.00, 0.00, 35.00),
(6, 14, 3, 1, 900.00, 0.00, 900.00);

SELECT setval('detalles_venta_id_detalle_venta_seq', (SELECT MAX(id_detalle_venta) FROM detalles_venta));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `disciplinas`
--

CREATE TABLE disciplinas (
  id_disciplina SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT DEFAULT NULL,
  estado SMALLINT DEFAULT 1,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

INSERT INTO disciplinas (id_disciplina, nombre, descripcion, estado, fecha_creacion, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 'Musculación', 'Entrenamiento con pesas y máquinas', 1, '2026-09-01 19:02:45', 2, NULL, NULL),
(2, 'Spinning', 'Entrenamiento cardiovascular en bicicleta', 1, '2026-09-01 19:02:45', 2, NULL, NULL),
(3, 'Yoga', 'Disciplina de movilidad, fuerza y relajación', 1, '2026-09-01 19:02:45', 2, NULL, NULL),
(4, 'Cross Training', 'Entrenamiento funcional de alta intensidad', 1, '2026-09-01 19:02:45', 2, NULL, NULL),
(5, 'Zumba', 'Entrenamiento cardiovascular con baile', 1, '2026-09-01 19:02:45', 2, NULL, NULL);

SELECT setval('disciplinas_id_disciplina_seq', (SELECT MAX(id_disciplina) FROM disciplinas));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `entrenadores`
--

CREATE TABLE entrenadores (
  id_entrenador SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  apellido VARCHAR(100) NOT NULL,
  telefono VARCHAR(20) DEFAULT NULL,
  email VARCHAR(150) DEFAULT NULL,
  estado SMALLINT DEFAULT 1,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

INSERT INTO entrenadores (id_entrenador, nombre, apellido, telefono, email, estado, fecha_creacion, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 'Alejandro', 'Torres', '5552000001', 'alejandro.torres@email.com', 1, '2026-09-01 19:02:45', 2, NULL, NULL),
(2, 'Fernanda', 'Morales', '5552000002', 'fernanda.morales@email.com', 1, '2026-09-01 19:02:45', 2, NULL, NULL),
(3, 'Ricardo', 'Castillo', '5552000003', 'ricardo.castillo@email.com', 1, '2026-09-01 19:02:45', 2, NULL, NULL),
(4, 'Daniela', 'Vargas', '5552000004', 'daniela.vargas@email.com', 1, '2026-09-01 19:02:45', 2, NULL, NULL);

SELECT setval('entrenadores_id_entrenador_seq', (SELECT MAX(id_entrenador) FROM entrenadores));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `entrenador_disciplina`
--

CREATE TABLE entrenador_disciplina (
  id_entrenador INTEGER REFERENCES entrenadores(id_entrenador) ON DELETE CASCADE,
  id_disciplina INTEGER REFERENCES disciplinas(id_disciplina) ON DELETE CASCADE,
  PRIMARY KEY (id_entrenador, id_disciplina)
);

INSERT INTO entrenador_disciplina (id_entrenador, id_disciplina) VALUES
(1, 1),
(1, 4),
(2, 3),
(2, 5),
(3, 2),
(3, 4),
(4, 1),
(4, 3);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clases`
--

CREATE TABLE clases (
  id_clase SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT DEFAULT NULL,
  instructor VARCHAR(150) DEFAULT NULL,
  horario TIME NOT NULL,
  duracion_minutos INTEGER NOT NULL,
  dia_semana VARCHAR(20) CHECK (UPPER(dia_semana) IN ('LUNES','MARTES','MIERCOLES','JUEVES','VIERNES','SABADO','DOMINGO')),
  cupo_maximo INTEGER NOT NULL,
  estado VARCHAR(20) DEFAULT 'ACTIVA' CHECK (UPPER(estado) IN ('ACTIVA','INACTIVA','CANCELADA')),
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

INSERT INTO clases (id_clase, nombre, descripcion, instructor, horario, duracion_minutos, dia_semana, cupo_maximo, estado, fecha_creacion, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 'Musculación', 'Entrenamiento de fuerza', 'Alejandro Torres', '08:00:00', 60, 'LUNES', 20, 'ACTIVA', '2026-09-01 19:03:28', 1, NULL, NULL),
(2, 'Spinning', 'Clase de bicicleta estacionaria', 'Ricardo Castillo', '10:00:00', 45, 'MARTES', 15, 'ACTIVA', '2026-09-01 19:03:28', 1, NULL, NULL),
(3, 'Yoga', 'Clase de movilidad y relajación', 'Fernanda Morales', '18:00:00', 60, 'MIERCOLES', 20, 'ACTIVA', '2026-09-01 19:03:28', 1, NULL, NULL),
(4, 'Cross Training', 'Entrenamiento funcional', 'Alejandro Torres', '19:00:00', 60, 'JUEVES', 15, 'ACTIVA', '2026-09-01 19:03:28', 1, NULL, NULL),
(5, 'Zumba', 'Clase cardiovascular con baile', 'Fernanda Morales', '17:00:00', 60, 'VIERNES', 25, 'ACTIVA', '2026-09-01 19:03:28', 1, NULL, NULL);

SELECT setval('clases_id_clase_seq', (SELECT MAX(id_clase) FROM clases));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reservas_clases`
--

CREATE TABLE reservas_clases (
  id_reserva SERIAL PRIMARY KEY,
  id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente),
  id_clase INTEGER NOT NULL REFERENCES clases(id_clase),
  fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  estado VARCHAR(20) DEFAULT 'RESERVADA' CHECK (UPPER(estado) IN ('RESERVADA','CANCELADA','ASISTIO','NO_ASISTIO')),
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

INSERT INTO reservas_clases (id_reserva, id_cliente, id_clase, fecha_reserva, estado, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 1, 1, '2026-09-01 19:03:28', 'RESERVADA', 1, NULL, NULL),
(2, 2, 3, '2026-09-01 19:03:28', 'RESERVADA', 1, NULL, NULL),
(3, 3, 2, '2026-09-01 19:03:29', 'ASISTIO', 1, NULL, NULL);

SELECT setval('reservas_clases_id_reserva_seq', (SELECT MAX(id_reserva) FROM reservas_clases));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `asistencia_clases`
--

CREATE TABLE asistencia_clases (
  id_asistencia SERIAL PRIMARY KEY,
  id_reserva INTEGER NOT NULL REFERENCES reservas_clases(id_reserva),
  fecha_asistencia DATE NOT NULL,
  estado VARCHAR(20) CHECK (UPPER(estado) IN ('ASISTIO','NO_ASISTIO')),
  observaciones TEXT DEFAULT NULL,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

INSERT INTO asistencia_clases (id_asistencia, id_reserva, fecha_asistencia, estado, observaciones, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 3, '2026-09-01', 'ASISTIO', 'Asistencia registrada correctamente', 1, NULL, NULL);

SELECT setval('asistencia_clases_id_asistencia_seq', (SELECT MAX(id_asistencia) FROM asistencia_clases));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cancelaciones_clases`
--

CREATE TABLE cancelaciones_clases (
  id_cancelacion SERIAL PRIMARY KEY,
  id_clase INTEGER NOT NULL REFERENCES clases(id_clase),
  fecha_cancelacion DATE NOT NULL,
  motivo VARCHAR(255) NOT NULL,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario)
);

SELECT setval('cancelaciones_clases_id_cancelacion_seq', (SELECT MAX(id_cancelacion) FROM cancelaciones_clases));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `margen_ganancia`
--

CREATE TABLE margen_ganancia (
  id_margen SERIAL PRIMARY KEY,
  id_producto INTEGER NOT NULL REFERENCES productos(id_producto),
  costo_unitario NUMERIC(10,2) NOT NULL,
  precio_venta NUMERIC(10,2) NOT NULL,
  margen_porcentaje NUMERIC(5,2) NOT NULL,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

INSERT INTO margen_ganancia (id_margen, id_producto, costo_unitario, precio_venta, margen_porcentaje, fecha_creacion, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 1, 10.00, 20.00, 50.00, '2026-09-01 19:03:27', 2, NULL, NULL),
(2, 2, 20.00, 35.00, 42.86, '2026-09-01 19:03:28', 2, NULL, NULL),
(3, 3, 600.00, 850.00, 29.41, '2026-09-01 19:03:28', 2, NULL, NULL),
(4, 4, 150.00, 250.00, 40.00, '2026-09-01 19:03:28', 2, NULL, NULL),
(5, 5, 220.00, 350.00, 37.14, '2026-09-01 19:03:28', 2, NULL, NULL);

SELECT setval('margen_ganancia_id_margen_seq', (SELECT MAX(id_margen) FROM margen_ganancia));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pagos_membresias`
--

CREATE TABLE pagos_membresias (
  id_pago_membresia SERIAL PRIMARY KEY,
  id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente),
  id_membresia INTEGER NOT NULL REFERENCES membresias(id_membresia),
  fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE NOT NULL,
  monto NUMERIC(10,2) NOT NULL,
  metodo_pago VARCHAR(30) CHECK (UPPER(metodo_pago) IN ('EFECTIVO','TARJETA','TRANSFERENCIA')),
  referencia VARCHAR(100) DEFAULT NULL,
  estado VARCHAR(20) DEFAULT 'PAGADO' CHECK (UPPER(estado) IN ('PAGADO','PENDIENTE','CANCELADO')),
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

INSERT INTO pagos_membresias (id_pago_membresia, id_cliente, id_membresia, fecha_pago, fecha_inicio, fecha_fin, monto, metodo_pago, referencia, estado, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 1, 1, '2026-09-01 19:03:28', '2026-09-01', '2026-10-01', 500.00, 'EFECTIVO', 'PAGO-SOC-0001', 'PAGADO', 1, NULL, NULL),
(2, 2, 2, '2026-09-01 19:03:28', '2026-09-01', '2026-11-30', 1350.00, 'EFECTIVO', 'PAGO-SOC-0002', 'PAGADO', 1, NULL, NULL),
(3, 3, 3, '2026-09-01 19:03:28', '2026-09-01', '2027-02-28', 2400.00, 'EFECTIVO', 'PAGO-SOC-0003', 'PAGADO', 1, NULL, NULL),
(4, 4, 5, '2026-09-01 19:03:28', '2026-09-01', '2026-10-01', 750.00, 'EFECTIVO', 'PAGO-SOC-0004', 'PAGADO', 1, NULL, NULL),
(5, 5, 4, '2026-09-01 19:03:28', '2026-09-01', '2027-09-01', 4200.00, 'EFECTIVO', 'PAGO-SOC-0005', 'PAGADO', 1, NULL, NULL);

SELECT setval('pagos_membresias_id_pago_membresia_seq', (SELECT MAX(id_pago_membresia) FROM pagos_membresias));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `permisos`
--

CREATE TABLE permisos (
  id_permiso SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  modulo VARCHAR(100) NOT NULL,
  descripcion TEXT DEFAULT NULL
);

INSERT INTO permisos (id_permiso, nombre, modulo, descripcion) VALUES
(1, 'ver_socios', 'Socios', 'Consultar socios'),
(2, 'crear_socios', 'Socios', 'Registrar socios'),
(3, 'editar_socios', 'Socios', 'Modificar socios'),
(4, 'eliminar_socios', 'Socios', 'Eliminar socios'),
(5, 'ver_membresias', 'Membresias', 'Consultar catálogo de membresías'),
(6, 'crear_membresias', 'Membresias', 'Crear membresías'),
(7, 'editar_membresias', 'Membresias', 'Modificar membresías'),
(8, 'ver_clases', 'Clases', 'Consultar clases'),
(9, 'crear_clases', 'Clases', 'Crear clases'),
(10, 'editar_clases', 'Clases', 'Modificar clases'),
(11, 'cancelar_clases', 'Clases', 'Cancelar clases'),
(12, 'reservar_clases', 'Clases', 'Reservar clases'),
(13, 'ver_inventario', 'Inventario', 'Consultar inventario'),
(14, 'crear_productos', 'Inventario', 'Registrar productos'),
(15, 'editar_productos', 'Inventario', 'Modificar productos'),
(16, 'ver_proveedores', 'Proveedores', 'Consultar proveedores'),
(17, 'crear_proveedores', 'Proveedores', 'Registrar proveedores'),
(18, 'ver_ventas', 'Ventas', 'Consultar ventas'),
(19, 'crear_ventas', 'Ventas', 'Registrar ventas'),
(20, 'crear_promociones', 'Promociones', 'Crear promociones'),
(21, 'editar_promociones', 'Promociones', 'Modificar promociones'),
(22, 'ver_reportes', 'Reportes', 'Consultar reportes');

SELECT setval('permisos_id_permiso_seq', (SELECT MAX(id_permiso) FROM permisos));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `rol_permiso`
--

CREATE TABLE rol_permiso (
  id_rol INTEGER REFERENCES roles(id_rol) ON DELETE CASCADE,
  id_permiso INTEGER REFERENCES permisos(id_permiso) ON DELETE CASCADE,
  PRIMARY KEY (id_rol, id_permiso)
);

INSERT INTO rol_permiso (id_rol, id_permiso) VALUES
(1, 1), (1, 2), (1, 3), (1, 5), (1, 8), (1, 11), (1, 12), (1, 13), (1, 16), (1, 18), (1, 19),
(2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (2, 11), (2, 12), (2, 13), (2, 14), (2, 15), (2, 16), (2, 17), (2, 18), (2, 19), (2, 20), (2, 21), (2, 22),
(3, 1), (3, 5), (3, 8), (3, 18), (3, 22),
(4, 5), (4, 8), (4, 12);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `promociones`
--

CREATE TABLE promociones (
  id_promocion SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT DEFAULT NULL,
  tipo VARCHAR(30) CHECK (UPPER(tipo) IN ('PORCENTAJE','MONTO','')),
  valor NUMERIC(10,2) NOT NULL,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE NOT NULL,
  estado VARCHAR(20) DEFAULT 'ACTIVA' CHECK (UPPER(estado) IN ('ACTIVA','INACTIVA')),
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario),
  fecha_edicion TIMESTAMP DEFAULT NULL,
  usuario_edito INTEGER REFERENCES usuarios(id_usuario)
);

INSERT INTO promociones (id_promocion, nombre, descripcion, tipo, valor, fecha_inicio, fecha_fin, estado, fecha_creacion, usuario_creo, fecha_edicion, usuario_edito) VALUES
(1, 'Promoción de bienvenida', 'Descuento para nuevos socios', 'PORCENTAJE', 10.00, '2026-09-01', '2026-10-01', 'ACTIVA', '2026-09-01 19:03:28', 2, NULL, NULL),
(2, 'Promoción Premium', 'Descuento especial para membresía Premium', 'PORCENTAJE', 15.00, '2026-09-01', '2026-10-31', 'ACTIVA', '2026-09-01 19:03:28', 2, NULL, NULL),
(3, 'Trae un amigo ', 'trae a alguien nuevo y obten el 35% de descuento en tu proxima renovacion', '', 35.00, '2000-01-01', '2000-01-01', 'ACTIVA', '2026-09-08 16:32:29', NULL, NULL, NULL),
(4, 'Al 2x1', '2x1 renueva o compra una membresia y llevate una segunda del mismo tipo gratis', '', 50.00, '2000-01-01', '2000-01-01', 'ACTIVA', '2026-09-09 10:45:39', NULL, NULL, NULL);

SELECT setval('promociones_id_promocion_seq', (SELECT MAX(id_promocion) FROM promociones));

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reportes`
--

CREATE TABLE reportes (
  id_reporte SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  tipo VARCHAR(30) CHECK (UPPER(tipo) IN ('VENTAS','INVENTARIO','MEMBRESIAS','ASISTENCIAS','OTRO')),
  fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ruta_archivo VARCHAR(255) DEFAULT NULL,
  usuario_creo INTEGER REFERENCES usuarios(id_usuario)
);

INSERT INTO reportes (id_reporte, nombre, tipo, fecha_generacion, ruta_archivo, usuario_creo) VALUES
(1, 'Reporte de ventas', 'VENTAS', '2026-09-01 19:03:30', 'reportes/ventas.pdf', 2),
(2, 'Reporte de inventario', 'INVENTARIO', '2026-09-01 19:03:30', 'reportes/inventario.pdf', 2),
(3, 'Reporte de membresías', 'MEMBRESIAS', '2026-09-01 19:03:30', 'reportes/membresias.pdf', 2),
(4, 'Reporte de asistencias', 'ASISTENCIAS', '2026-09-01 19:03:30', 'reportes/asistencias.pdf', 2);

SELECT setval('reportes_id_reporte_seq', (SELECT MAX(id_reporte) FROM reportes));