-- =============================================================
--  MiSpa Turnos — Script de base de datos
--  Versión final para distribución
--  Universidad Nacional de La Rioja (UNLaR)
--  Tecnicatura Universitaria en Informática — Trabajo Final
-- =============================================================

CREATE DATABASE IF NOT EXISTS mispa_turnos
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE mispa_turnos;

-- -------------------------------------------------------------
-- TABLA: personas
-- -------------------------------------------------------------
CREATE TABLE personas (
    id_persona  INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(50)  NOT NULL,
    apellido    VARCHAR(50)  NOT NULL,
    dni         INT          UNIQUE,
    telefono    VARCHAR(20),
    email       VARCHAR(100)
);

-- -------------------------------------------------------------
-- TABLA: usuarios
-- -------------------------------------------------------------
CREATE TABLE usuarios (
    id_usuario      INT AUTO_INCREMENT PRIMARY KEY,
    id_persona      INT          NOT NULL,
    nombre_usuario  VARCHAR(50)  UNIQUE NOT NULL,
    contrasena      VARCHAR(255) NOT NULL,
    rol             ENUM('administrador', 'estandar') NOT NULL DEFAULT 'estandar',
    foto            VARCHAR(255) DEFAULT NULL,
    activo          TINYINT(1)   DEFAULT 1,
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona)
);

-- -------------------------------------------------------------
-- TABLA: empleados
-- -------------------------------------------------------------
CREATE TABLE empleados (
    id_empleado  INT AUTO_INCREMENT PRIMARY KEY,
    id_persona   INT NOT NULL,
    id_usuario   INT,
    dias_trabajo VARCHAR(100) COMMENT 'ej: lunes,miércoles,viernes',
    activo       TINYINT(1) DEFAULT 1,
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- -------------------------------------------------------------
-- TABLA: clientes
-- -------------------------------------------------------------
CREATE TABLE clientes (
    id_cliente   INT AUTO_INCREMENT PRIMARY KEY,
    id_persona   INT NOT NULL,
    preferencias TEXT,
    notas        TEXT,
    estado       ENUM('activo', 'inactivo') DEFAULT 'activo',
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona)
);

-- -------------------------------------------------------------
-- TABLA: especialidades
-- -------------------------------------------------------------
CREATE TABLE especialidades (
    id_especialidad INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL,
    descripcion     TEXT
);

-- -------------------------------------------------------------
-- TABLA: empleado_especialidad (muchos a muchos)
-- -------------------------------------------------------------
CREATE TABLE empleado_especialidad (
    id_empleado     INT,
    id_especialidad INT,
    PRIMARY KEY (id_empleado, id_especialidad),
    FOREIGN KEY (id_empleado)     REFERENCES empleados(id_empleado),
    FOREIGN KEY (id_especialidad) REFERENCES especialidades(id_especialidad)
);

-- -------------------------------------------------------------
-- TABLA: servicios
-- -------------------------------------------------------------
CREATE TABLE servicios (
    id_servicio     INT AUTO_INCREMENT PRIMARY KEY,
    id_especialidad INT,
    nombre          VARCHAR(100)  NOT NULL,
    descripcion     TEXT,
    precio          DECIMAL(10,2) NOT NULL,
    duracion        FLOAT         NOT NULL COMMENT 'duracion en horas',
    protocolos      TEXT,
    activo          TINYINT(1)    DEFAULT 1,
    FOREIGN KEY (id_especialidad) REFERENCES especialidades(id_especialidad)
);

-- -------------------------------------------------------------
-- TABLA: turnos
-- -------------------------------------------------------------
CREATE TABLE turnos (
    id_turno      INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente    INT           NOT NULL,
    id_empleado   INT           NOT NULL,
    fecha_hora    DATETIME      NOT NULL,
    estado        ENUM('programado', 'completado', 'cancelado') DEFAULT 'programado',
    precio_total  DECIMAL(10,2),
    sena_pagada   DECIMAL(10,2) DEFAULT NULL,
    total_pagado  TINYINT(1)    DEFAULT 0,
    duracion      FLOAT         COMMENT 'duracion total en horas',
    observaciones TEXT,
    FOREIGN KEY (id_cliente)  REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

-- -------------------------------------------------------------
-- TABLA: turno_servicio (muchos a muchos)
-- -------------------------------------------------------------
CREATE TABLE turno_servicio (
    id_turno    INT,
    id_servicio INT,
    PRIMARY KEY (id_turno, id_servicio),
    FOREIGN KEY (id_turno)    REFERENCES turnos(id_turno),
    FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio)
);

-- -------------------------------------------------------------
-- TABLA: configuracion general
-- -------------------------------------------------------------
CREATE TABLE configuracion (
    id_config INT AUTO_INCREMENT PRIMARY KEY,
    clave     VARCHAR(100) UNIQUE NOT NULL,
    valor     VARCHAR(255)
);

-- =============================================================
--  DATOS INICIALES
-- =============================================================

-- Configuracion basica de la empresa
INSERT INTO configuracion (clave, valor) VALUES
('nombre_empresa', 'Macaspa'),
('direccion',      'Las Acacias 2553, Barrio Vial, La Rioja'),
('telefono',       '+5493804939419'),
('instagram',      '@macaspalr'),
('horario_inicio', '15:00'),
('horario_fin',    '20:00'),
('dias_laborales', 'martes,miercoles,jueves,viernes,sabado'),
('monto_sena',     '2000');

-- Especialidades
INSERT INTO especialidades (nombre, descripcion) VALUES
('Manicura y Pedicura',
 'Servicios relacionados al cuidado integral para manos y pies para lucir unas unas impecables, sanas y cuidadas.'),
('Cejas y Pestanas',
 'Tratamientos disenados para potenciar y enmarcar la mirada de forma natural sin necesidad de maquillaje diario.'),
('Tratamientos Faciales',
 'Procedimientos personalizados para cuidar, rejuvenecer y proteger la piel del rostro, buscan devolver la luminosidad, firmeza y vitalidad a la dermis.'),
('Tratamientos Corporales',
 'Terapias enfocadas en el bienestar y la estetica de todo el cuerpo. Incluye masajes relajantes, reductores o drenantes con tecnicas avanzadas para moldear la silueta, combatir la celulitis, mejorar la circulacion y liberar el estres.'),
('Depilacion Laser',
 'La solucion mas comoda, rapida y duradera para eliminar el vello no deseado. Utiliza tecnologia de luz pulsada o laser para debilitar el foliculo piloso desde la raiz, logrando una piel suave y libre de vello de forma progresiva y segura.');

-- Servicios - Manicura y Pedicura (id_especialidad = 1)
INSERT INTO servicios (id_especialidad, nombre, descripcion, precio, duracion, protocolos) VALUES
(1, 'Arreglo por una',
 'Reparacion individual de unas quebradas o danadas para mantener una apariencia prolija y uniforme.',
 5000.00, 0.5, 'Evaluacion de la una, reconstruccion o reparacion, limado y sellado final.'),
(1, 'Esculpidas en gel 1&2 o 3&4',
 'Extension y modelado de unas con gel para lograr mayor largo, resistencia y diseno personalizado.',
 20000.00, 2.0, 'Preparacion de la una natural, colocacion de molde, aplicacion de gel, curado en cabina, limado y terminacion.'),
(1, 'Manicure + Esmaltado Semipermanente',
 'Servicio de cuidado de manos con esmaltado duradero y acabado brillante, liso o decorado.',
 14000.00, 1.2, 'Limpieza de cuticulas, limado, preparacion de la una, aplicacion de base, color/diseno y sellado.'),
(1, 'Manicure + Kapping + Esmaltado Semipermanente',
 'Refuerzo de la una natural con capa protectora y esmaltado de larga duracion.',
 16000.00, 1.6, 'Preparacion de unas, aplicacion de kapping, curado en cabina, esmaltado y sellado.'),
(1, 'Manicure sin esmaltado',
 'Cuidado estetico de manos y unas con acabado natural y prolijo.',
 12000.00, 0.8, 'Higiene, corte y limado, tratamiento de cuticulas e hidratacion.'),
(1, 'Pedicure + esmaltado semipermanente',
 'Tratamiento completo para pies con esmaltado resistente y duradero.',
 11000.00, 1.2, 'Limpieza, exfoliacion suave, cuidado de cuticulas, esmaltado y sellado.'),
(1, 'Pedicure + exfoliacion + pulido sin esmaltar',
 'Renovacion y suavizado de pies con acabado natural.',
 10000.00, 0.8, 'Higiene, exfoliacion, eliminacion de durezas, pulido e hidratacion.'),
(1, 'Retirado de esmaltado semipermanente',
 'Remocion segura del esmalte sin danar la una natural.',
 6000.00, 0.4, 'Ablandado del producto, retiro cuidadoso, limado suave e hidratacion.'),
(1, 'Retirado de unas esculpidas',
 'Eliminacion profesional de unas artificiales preservando la salud de la una natural.',
 7000.00, 0.8, 'Limado tecnico, remocion del material y tratamiento hidratante.'),
(1, 'Service',
 'Mantenimiento de unas esculpidas o kapping para conservar su estetica y duracion.',
 12000.00, 1.5, 'Relleno de crecimiento, reparacion si es necesario, limado y esmaltado final.'),
(1, 'Softgel',
 'Sistema de extensiones con tips de gel que brinda un acabado natural y liviano.',
 18000.00, 1.8, 'Preparacion de unas, colocacion de tips softgel, curado en cabina y terminacion.');

-- Servicios - Cejas y Pestanas (id_especialidad = 2)
INSERT INTO servicios (id_especialidad, nombre, descripcion, precio, duracion, protocolos) VALUES
(2, 'Extension de pestanas clasicas',
 'Aplicacion pelo por pelo para lograr un efecto natural y definido.',
 10000.00, 1.5, 'Limpieza de pestanas, aislamiento y colocacion individual de extensiones.'),
(2, 'Extension de pestanas con volumen',
 'Tecnica de abanicos de pestanas para mayor volumen e intensidad.',
 12000.00, 2.4, 'Preparacion del area, colocacion de abanicos y sellado final.'),
(2, 'Extension de pestanas tipo wet',
 'Efecto humedo y moderno con acabado definido y voluminoso.',
 14000.00, 1.7, 'Higiene, diseno personalizado y aplicacion estrategica de extensiones.'),
(2, 'Lifting de pestanas',
 'Curvado y elevacion de pestanas naturales para una mirada mas abierta.',
 9000.00, 0.8, 'Limpieza, moldeado, aplicacion de productos fijadores y nutricion final.'),
(2, 'Perfilado + laminado + tinte + brown laminations',
 'Diseno integral de cejas para lograr forma, definicion y efecto peinado duradero.',
 8000.00, 1.2, 'Perfilado, laminado, aplicacion de tinte y fijacion.'),
(2, 'Perfilado de cejas',
 'Diseno y definicion de cejas segun la armonia del rostro.',
 6000.00, 0.4, 'Analisis de forma, depilacion y definicion.'),
(2, 'Perfilado de cejas con tinta',
 'Perfilado con efecto maquillado semipermanente.',
 8000.00, 0.8, 'Diseno de cejas, aplicacion de tinta y acabado final.'),
(2, 'Permanente de pestanas',
 'Tratamiento para mantener las pestanas curvadas por mas tiempo.',
 9000.00, 0.9, 'Limpieza, aplicacion de molde y productos permanentes, hidratacion final.');

-- Servicios - Tratamientos Faciales (id_especialidad = 3)
INSERT INTO servicios (id_especialidad, nombre, descripcion, precio, duracion, protocolos) VALUES
(3, 'Dermapen',
 'Tratamiento de microneedling que estimula colageno y mejora textura de la piel.',
 9000.00, 1.0, 'Limpieza facial, aplicacion de activos, uso de dermapen y mascara calmante.'),
(3, 'Dermaplaning',
 'Exfoliacion superficial que elimina celulas muertas y vello fino del rostro.',
 11000.00, 0.84, 'Limpieza, exfoliacion con bisturi dermatologico e hidratacion.'),
(3, 'Facial para embarazadas',
 'Tratamiento suave y seguro adaptado a pieles sensibles durante el embarazo.',
 10000.00, 0.67, 'Limpieza, hidratacion y masaje facial con productos aptos.'),
(3, 'Limpieza profunda + punta de diamante',
 'Renovacion facial intensiva para limpiar impurezas y mejorar la textura de la piel.',
 15000.00, 1.5, 'Higiene, exfoliacion, extraccion, punta de diamante y mascara final.'),
(3, 'Radiofrecuencia en rostro, cuello y escote',
 'Tratamiento reafirmante que estimula colageno y mejora la firmeza.',
 20000.00, 0.75, 'Limpieza, aplicacion de gel conductor y radiofrecuencia localizada.'),
(3, 'Renovacion facial',
 'Tratamiento revitalizante para devolver luminosidad y frescura a la piel.',
 22000.00, 1.5, 'Limpieza, exfoliacion, activos nutritivos y mascara hidratante.'),
(3, 'Tratamiento control de acne',
 'Tratamiento especifico para disminuir brotes, oleosidad e inflamacion.',
 18500.00, 1.0, 'Limpieza profunda, extraccion controlada, activos descongestivos y mascara calmante.');

-- Servicios - Tratamientos Corporales (id_especialidad = 4)
INSERT INTO servicios (id_especialidad, nombre, descripcion, precio, duracion, protocolos) VALUES
(4, 'Descontracturante completo',
 'Masaje terapeutico para aliviar tensiones musculares y contracturas.',
 7500.00, 0.75, 'Evaluacion muscular, masaje profundo y relajacion final.'),
(4, 'Drenaje linfatico completo',
 'Tecnica suave que estimula la circulacion linfatica y reduce retencion de liquidos.',
 10500.00, 1.5, 'Maniobras lentas y ritmicas sobre zonas especificas del cuerpo.'),
(4, 'Masaje deportivo',
 'Tratamiento orientado a preparar o recuperar musculos luego de la actividad fisica.',
 7000.00, 0.75, 'Trabajo muscular localizado, elongacion y descarga muscular.'),
(4, 'Masaje facial',
 'Masaje relajante y revitalizante para rostro y cuello.',
 6500.00, 0.5, 'Limpieza ligera, maniobras faciales y aplicacion de hidratantes.'),
(4, 'Masaje pre natal o para embarazadas',
 'Masaje adaptado para aliviar molestias y favorecer la relajacion durante el embarazo.',
 9500.00, 1.0, 'Posiciones seguras, maniobras suaves y relajacion integral.'),
(4, 'Radiofrecuencia por zona',
 'Tratamiento corporal reafirmante y modelador localizado.',
 6500.00, 0.5, 'Aplicacion de gel conductor y radiofrecuencia en la zona elegida.'),
(4, 'Reductor en zona',
 'Tratamiento estetico enfocado en modelar y reducir adiposidad localizada.',
 6500.00, 0.75, 'Evaluacion corporal, tecnicas reductoras y aplicacion de activos especificos.');

-- Servicios - Depilacion Laser (id_especialidad = 5)
INSERT INTO servicios (id_especialidad, nombre, descripcion, precio, duracion, protocolos) VALUES
(5, 'Depilacion definitiva cuerpo completo o por zonas',
 'Tratamiento que reduce progresivamente el crecimiento del vello mediante tecnologia laser.',
 5000.00, 0.5, 'Evaluacion de piel y vello, rasurado previo, aplicacion de laser y cuidados post tratamiento.');

-- -------------------------------------------------------------
-- Usuario administrador por defecto
-- Credenciales: usuario = admin | contrasena = admin1234
-- IMPORTANTE: cambiar la contrasena al iniciar el sistema
-- por primera vez desde Configurar Perfil
-- -------------------------------------------------------------
INSERT INTO personas (nombre, apellido, email)
VALUES ('Administrador', 'Sistema', 'admin@mispa.com');

INSERT INTO usuarios (id_persona, nombre_usuario, contrasena, rol, activo)
VALUES (
    LAST_INSERT_ID(),
    'admin',
    '$2b$12$9ovdM0bpkIl3M4Ce9twCqu5fFOKySPAa7j1qebtME6HfcD3PVqEx.',
    'administrador',
    1
);
