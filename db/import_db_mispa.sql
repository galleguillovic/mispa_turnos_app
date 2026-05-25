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
    duracion        FLOAT         NOT NULL COMMENT 'duración en horas',
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
    sena_pagada   DECIMAL(10,2),
    total_pagado  TINYINT(1)    DEFAULT 0,
    duracion      FLOAT         COMMENT 'duración total en horas',
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
-- TABLA: configuracion general de la empresa
-- -------------------------------------------------------------
CREATE TABLE configuracion (
    id_config INT AUTO_INCREMENT PRIMARY KEY,
    clave     VARCHAR(100) UNIQUE NOT NULL,
    valor     VARCHAR(255)
);

-- =============================================================
--  DATOS INICIALES
-- =============================================================

-- -------------------------------------------------------------
-- Configuración básica de la empresa
-- -------------------------------------------------------------
INSERT INTO configuracion (clave, valor) VALUES
('nombre_empresa', 'Macaspa'),
('direccion',      'Las Acacias 2553, Barrio Vial, La Rioja'),
('telefono',       '+5493804939419'),
('instagram',      '@macaspalr'),
('horario_inicio', '15:00'),
('horario_fin',    '20:00'),
('dias_laborales', 'martes,miércoles,jueves,viernes,sábado'),
('monto_sena',     '2000');

-- -------------------------------------------------------------
-- Especialidades
-- -------------------------------------------------------------
INSERT INTO especialidades (id_especialidad, nombre, descripcion) VALUES
(1, 'Manicura y Pedicura',
 'Servicios relacionados al cuidado integral para manos y pies para lucir unas uñas impecables, sanas y cuidadas.'),
(4, 'Cejas y Pestañas',
 'Tratamientos diseñados para potenciar y enmarcar la mirada de forma natural sin necesidad de maquillaje diario.'),
(5, 'Tratamientos Faciales',
 'Procedimientos personalizados para cuidar, rejuvenecer y proteger la piel del rostro, buscan devolver la luminosidad, firmeza y vitalidad a la dermis.'),
(6, 'Tratamientos Corporales',
 'Terapias enfocadas en el bienestar y la estética de todo el cuerpo. Incluye masajes relajantes, reductores o drenantes con técnicas avanzadas para moldear la silueta, combatir la celulitis, mejorar la circulación y liberar el estrés.'),
(7, 'Depilación Láser',
 'La solución más cómoda, rápida y duradera para eliminar el vello no deseado. Utiliza tecnología de luz pulsada o láser para debilitar el folículo piloso desde la raíz, logrando una piel suave y libre de vello de forma progresiva y segura.');

-- -------------------------------------------------------------
-- Servicios
-- -------------------------------------------------------------
INSERT INTO servicios (id_servicio, id_especialidad, nombre, descripcion, precio, duracion, protocolos) VALUES
-- Manicura y Pedicura
(5,  1, 'Arreglo por uña',
 'Reparación individual de uñas quebradas o dañadas para mantener una apariencia prolija y uniforme.',
 5000.00, 0.5, 'Evaluación de la uña, reconstrucción o reparación, limado y sellado final.'),
(6,  1, 'Esculpidas en gel 1&2 o 3&4',
 'Extensión y modelado de uñas con gel para lograr mayor largo, resistencia y diseño personalizado.',
 20000.00, 2.0, 'Preparación de la uña natural, colocación de molde, aplicación de gel, curado en cabina, limado y terminación.'),
(7,  1, 'Manicure + Esmaltado Semipermanente',
 'Servicio de cuidado de manos con esmaltado duradero y acabado brillante, liso o decorado.',
 14000.00, 1.2, 'Limpieza de cutículas, limado, preparación de la uña, aplicación de base, color/diseño y sellado.'),
(8,  1, 'Manicure + Kapping + Esmaltado Semipermanente',
 'Refuerzo de la uña natural con capa protectora y esmaltado de larga duración.',
 16000.00, 1.6, 'Preparación de uñas, aplicación de kapping, curado en cabina, esmaltado y sellado.'),
(9,  1, 'Manicure sin esmaltado',
 'Cuidado estético de manos y uñas con acabado natural y prolijo.',
 12000.00, 0.8, 'Higiene, corte y limado, tratamiento de cutículas e hidratación.'),
(10, 1, 'Pedicure + esmaltado semipermanente',
 'Tratamiento completo para pies con esmaltado resistente y duradero.',
 11000.00, 1.2, 'Limpieza, exfoliación suave, cuidado de cutículas, esmaltado y sellado.'),
(11, 1, 'Pedicure + exfoliación + pulido sin esmaltar',
 'Renovación y suavizado de pies con acabado natural.',
 10000.00, 0.8, 'Higiene, exfoliación, eliminación de durezas, pulido e hidratación.'),
(12, 1, 'Retirado de esmaltado semipermanente',
 'Remoción segura del esmalte sin dañar la uña natural.',
 6000.00, 0.4, 'Ablandado del producto, retiro cuidadoso, limado suave e hidratación.'),
(13, 1, 'Retirado de uñas esculpidas',
 'Eliminación profesional de uñas artificiales preservando la salud de la uña natural.',
 7000.00, 0.8, 'Limado técnico, remoción del material y tratamiento hidratante.'),
(14, 1, 'Service',
 'Mantenimiento de uñas esculpidas o kapping para conservar su estética y duración.',
 12000.00, 1.5, 'Relleno de crecimiento, reparación si es necesario, limado y esmaltado final.'),
(15, 1, 'Softgel',
 'Sistema de extensiones con tips de gel que brinda un acabado natural y liviano.',
 18000.00, 1.8, 'Preparación de uñas, colocación de tips softgel, curado en cabina y terminación.'),
-- Cejas y Pestañas
(16, 4, 'Extensión de pestañas clásicas',
 'Aplicación pelo por pelo para lograr un efecto natural y definido.',
 10000.00, 1.5, 'Limpieza de pestañas, aislamiento y colocación individual de extensiones.'),
(17, 4, 'Extensión de pestañas con volumen',
 'Técnica de abanicos de pestañas para mayor volumen e intensidad.',
 12000.00, 2.4, 'Preparación del área, colocación de abanicos y sellado final.'),
(18, 4, 'Extensión de pestañas tipo wet',
 'Efecto húmedo y moderno con acabado definido y voluminoso.',
 14000.00, 1.7, 'Higiene, diseño personalizado y aplicación estratégica de extensiones.'),
(19, 4, 'Lifting de pestañas',
 'Curvado y elevación de pestañas naturales para una mirada más abierta.',
 9000.00, 0.8, 'Limpieza, moldeado, aplicación de productos fijadores y nutrición final.'),
(20, 4, 'Perfilado + laminado + tinte + brown laminations',
 'Diseño integral de cejas para lograr forma, definición y efecto peinado duradero.',
 8000.00, 1.2, 'Perfilado, laminado, aplicación de tinte y fijación.'),
(21, 4, 'Perfilado de cejas',
 'Diseño y definición de cejas según la armonía del rostro.',
 6000.00, 0.4, 'Análisis de forma, depilación y definición.'),
(22, 4, 'Perfilado de cejas con tinta',
 'Perfilado con efecto maquillado semipermanente.',
 8000.00, 0.8, 'Diseño de cejas, aplicación de tinta y acabado final.'),
(23, 4, 'Permanente de pestañas',
 'Tratamiento para mantener las pestañas curvadas por más tiempo.',
 9000.00, 0.9, 'Limpieza, aplicación de molde y productos permanentes, hidratación final.'),
-- Tratamientos Faciales
(24, 5, 'Dermapen',
 'Tratamiento de microneedling que estimula colágeno y mejora textura de la piel.',
 9000.00, 1.0, 'Limpieza facial, aplicación de activos, uso de dermapen y máscara calmante.'),
(25, 5, 'Dermaplaning',
 'Exfoliación superficial que elimina células muertas y vello fino del rostro.',
 11000.00, 0.84, 'Limpieza, exfoliación con bisturí dermatológico e hidratación.'),
(26, 5, 'Facial para embarazadas',
 'Tratamiento suave y seguro adaptado a pieles sensibles durante el embarazo.',
 10000.00, 0.67, 'Limpieza, hidratación y masaje facial con productos aptos.'),
(27, 5, 'Limpieza profunda + punta de diamante',
 'Renovación facial intensiva para limpiar impurezas y mejorar la textura de la piel.',
 15000.00, 1.5, 'Higiene, exfoliación, extracción, punta de diamante y máscara final.'),
(28, 5, 'Radiofrecuencia en rostro, cuello y escote',
 'Tratamiento reafirmante que estimula colágeno y mejora la firmeza.',
 20000.00, 0.75, 'Limpieza, aplicación de gel conductor y radiofrecuencia localizada.'),
(29, 5, 'Renovación facial',
 'Tratamiento revitalizante para devolver luminosidad y frescura a la piel.',
 22000.00, 1.5, 'Limpieza, exfoliación, activos nutritivos y máscara hidratante.'),
(30, 5, 'Tratamiento control de acné',
 'Tratamiento específico para disminuir brotes, oleosidad e inflamación.',
 18500.00, 1.0, 'Limpieza profunda, extracción controlada, activos descongestivos y máscara calmante.'),
-- Tratamientos Corporales
(31, 6, 'Descontracturante completo',
 'Masaje terapéutico para aliviar tensiones musculares y contracturas.',
 7500.00, 0.75, 'Evaluación muscular, masaje profundo y relajación final.'),
(32, 6, 'Drenaje linfático completo',
 'Técnica suave que estimula la circulación linfática y reduce retención de líquidos.',
 10500.00, 1.5, 'Maniobras lentas y rítmicas sobre zonas específicas del cuerpo.'),
(33, 6, 'Masaje deportivo',
 'Tratamiento orientado a preparar o recuperar músculos luego de la actividad física.',
 7000.00, 0.75, 'Trabajo muscular localizado, elongación y descarga muscular.'),
(34, 6, 'Masaje facial',
 'Masaje relajante y revitalizante para rostro y cuello.',
 6500.00, 0.5, 'Limpieza ligera, maniobras faciales y aplicación de hidratantes.'),
(35, 6, 'Masaje pre natal o para embarazadas',
 'Masaje adaptado para aliviar molestias y favorecer la relajación durante el embarazo.',
 9500.00, 1.0, 'Posiciones seguras, maniobras suaves y relajación integral.'),
(36, 6, 'Radiofrecuencia por zona',
 'Tratamiento corporal reafirmante y modelador localizado.',
 6500.00, 0.5, 'Aplicación de gel conductor y radiofrecuencia en la zona elegida.'),
(37, 6, 'Reductor en zona',
 'Tratamiento estético enfocado en modelar y reducir adiposidad localizada.',
 6500.00, 0.75, 'Evaluación corporal, técnicas reductoras y aplicación de activos específicos.'),
-- Depilación Láser
(38, 7, 'Depilación definitiva cuerpo completo o por zonas',
 'Tratamiento que reduce progresivamente el crecimiento del vello mediante tecnología láser.',
 5000.00, 0.5, 'Evaluación de piel y vello, rasurado previo, aplicación de láser y cuidados post tratamiento.');

-- -------------------------------------------------------------
-- Usuario administrador por defecto
-- Credenciales: usuario = admin | contraseña = admin1234
-- ¡IMPORTANTE: cambiar la contraseña al iniciar el sistema
--  por primera vez desde Configurar Perfil!
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
ENDSQL
echo "OK"