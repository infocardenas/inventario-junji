-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 31-07-2024 a las 01:50:53
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `inventariofinal`
--
CREATE TABLE `provincia` (
  `idProvincia` int(11) NOT NULL,
  `nombreProvincia` varchar(45) NOT NULL,
  PRIMARY KEY (`idProvincia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Estructura de tabla para la tabla `comuna`
--

CREATE TABLE `comuna` (
  `idComuna` int(11) NOT NULL,
  `nombreComuna` varchar(45) DEFAULT NULL,
  `idProvincia` int(11) NOT NULL,
  PRIMARY KEY (`idComuna`),
  CONSTRAINT `comuna_ibfk_1` FOREIGN KEY (`idProvincia`) REFERENCES `provincia` (`idProvincia`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Estructura de tabla para la tabla `modalidad`


CREATE TABLE `modalidad` (
  `idModalidad` int(11) NOT NULL,
  `nombreModalidad` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`idModalidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Estructura de tabla para la tabla `unidad`
--

CREATE TABLE `unidad` (
  `idUnidad` int(11) NOT NULL AUTO_INCREMENT,
  `nombreUnidad` varchar(255) DEFAULT NULL,
  `contactoUnidad` varchar(255) DEFAULT NULL,
  `direccionUnidad` varchar(255) CHARACTER SET armscii8 COLLATE armscii8_general_ci DEFAULT NULL,
  `idComuna` int(11) NOT NULL,
  `idModalidad` int(11) DEFAULT NULL,
  PRIMARY KEY (`idUnidad`),
  CONSTRAINT `unidad_ibfk_1` FOREIGN KEY (`idComuna`) REFERENCES `comuna` (`idComuna`),
  CONSTRAINT `unidad_ibfk_2` FOREIGN KEY (`idModalidad`) REFERENCES `modalidad` (`idModalidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Estructura de tabla para la tabla `funcionario`
--

CREATE TABLE `funcionario` (
  `rutFuncionario` VARCHAR(10) PRIMARY KEY NOT NULL,
  `nombreFuncionario` VARCHAR(45) NOT NULL,
  `cargoFuncionario` ENUM('ADMINISTRATIVO', 'AUXILIAR', 'PROFESIONAL', 'TÉCNICO', 'DIRECTOR REGIONAL','ENCARGADA/O') NOT NULL,
  `correoFuncionario` VARCHAR(45) NOT NULL,
  `idUnidad` INT NOT NULL,
  UNIQUE KEY `unique_correoFuncionario` (`correoFuncionario`),
  CONSTRAINT `fk_funcionario_idUnidad` FOREIGN KEY (`idUnidad`) REFERENCES `unidad` (`idUnidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;



--
-- Estructura de tabla para la tabla `asignacion`
--

CREATE TABLE `asignacion` (
  `idAsignacion` INT PRIMARY KEY AUTO_INCREMENT,
  `fecha_inicioAsignacion` DATE NOT NULL,
  `ObservacionAsignacion` VARCHAR(250) DEFAULT NULL,
  `ActivoAsignacion` TINYINT DEFAULT 1,
  `rutFuncionario` VARCHAR(10) NOT NULL,
  CONSTRAINT `fk_asignacion_funcionario` FOREIGN KEY (`rutFuncionario`) 
    REFERENCES `funcionario` (`rutFuncionario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Estructura de tabla para la tabla `marca_equipo`cl
--

CREATE TABLE `marca_equipo` (
  `idMarca_Equipo` int(11) NOT NULL AUTO_INCREMENT,
  `nombreMarcaEquipo` varchar(45) NOT NULL UNIQUE,
  PRIMARY KEY (`idMarca_Equipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Estructura de tabla para la tabla `tipo_equipo`
--

CREATE TABLE `tipo_equipo` (
  `idTipo_equipo` int(11) NOT NULL AUTO_INCREMENT,
  `nombreTipo_equipo` varchar(45) UNIQUE,
  PRIMARY KEY (`idTipo_equipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Estructura de tabla para la tabla `marca_tipo_equipo`
--

CREATE TABLE `marca_tipo_equipo` (
  `idMarcaTipo` int(11) NOT NULL AUTO_INCREMENT,
  `idMarca_Equipo` int(11) NOT NULL,
  `idTipo_equipo` int(11) NOT NULL,
  PRIMARY KEY (`idMarcaTipo`),
  UNIQUE KEY `unique_marca_tipo` (`idMarca_Equipo`, `idTipo_equipo`),
  CONSTRAINT `marca_tipo_equipo_ibfk_1` FOREIGN KEY (`idMarca_Equipo`) REFERENCES `marca_equipo` (`idMarca_Equipo`) ON DELETE RESTRICT,
  CONSTRAINT `marca_tipo_equipo_ibfk_2` FOREIGN KEY (`idTipo_equipo`) REFERENCES `tipo_equipo` (`idTipo_equipo`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Estructura de tabla para la tabla `modelo_equipo`
--

CREATE TABLE `modelo_equipo` (
  `idModelo_Equipo` int(11) NOT NULL AUTO_INCREMENT,
  `nombreModeloequipo` varchar(45) UNIQUE,
  `idMarca_Tipo_Equipo` int(11) NOT NULL, 
  PRIMARY KEY (`idModelo_Equipo`),
  CONSTRAINT `modelo_equipo_FK_1` FOREIGN KEY (`idMarca_Tipo_Equipo`) REFERENCES `marca_tipo_equipo` (`idMarcaTipo`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Estructura de tabla para la tabla `tipo_adquisicion`
--

CREATE TABLE `tipo_adquisicion` (
  `idTipo_adquisicion` INT NOT NULL AUTO_INCREMENT,
  `nombre_tipo_adquisicion` ENUM('COMPRA', 'ARRIENDO', 'PRÉSTAMO', 'COMODATTO') NOT NULL, 
  PRIMARY KEY (`idTipo_adquisicion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Estructura de tabla para la tabla `proveedor`
--

CREATE TABLE `proveedor` (
  `idProveedor` int(11) NOT NULL AUTO_INCREMENT,
  `nombreProveedor` varchar(45) NOT NULL,
  PRIMARY KEY (`idProveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Estructura de tabla para la tabla `orden_compra`
--

CREATE TABLE `orden_compra` (
  `idOrden_compra` varchar(45) NOT NULL,
  `nombreOrden_compra` varchar(45) DEFAULT NULL,
  `fechacompraOrden_compra` date DEFAULT NULL,
  `fechafin_ORDEN_COMPRA` date DEFAULT NULL,
  `rutadocumentoOrden_compra` varchar(45) DEFAULT NULL,
  `idTipo_adquisicion` int(11) NOT NULL,
  `idProveedor` int(11) NOT NULL,
  PRIMARY KEY (`idOrden_compra`),
  CONSTRAINT `orden_compra_ibfk_1` FOREIGN KEY (`idTipo_adquisicion`) REFERENCES `tipo_adquisicion` (`idTipo_adquisicion`),
  CONSTRAINT `orden_compra_ibfk_2` FOREIGN KEY (`idProveedor`) REFERENCES `proveedor` (`idProveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Estructura de tabla para la tabla `estado_equipo`
--

CREATE TABLE `estado_equipo` (
  `idEstado_equipo` int(11) NOT NULL AUTO_INCREMENT,
  `nombreEstado_equipo` varchar(45) DEFAULT NULL,
  `FechaEstado_equipo` date DEFAULT NULL,
  PRIMARY KEY (`idEstado_equipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Estructura de tabla para la tabla `equipo`
--

CREATE TABLE `equipo` (
  `idEquipo` int(11) NOT NULL AUTO_INCREMENT,
  `Cod_inventarioEquipo` varchar(20) DEFAULT NULL,
  `Num_serieEquipo` varchar(20) UNIQUE,
  `ObservacionEquipo` varchar(250) DEFAULT NULL,
  `codigoproveedor_equipo` varchar(45) DEFAULT NULL,
  `macEquipo` varchar(45) DEFAULT NULL,
  `imeiEquipo` varchar(45) DEFAULT NULL,
  `numerotelefonicoEquipo` varchar(12) DEFAULT NULL,
  `idEstado_equipo` int(11) NOT NULL DEFAULT 1,
  `idUnidad` int(11) NOT NULL,
  `idOrden_compra` varchar(45) NOT NULL,
  `idModelo_equipo` int(11) NOT NULL,
  PRIMARY KEY (`idEquipo`),
  CONSTRAINT `equipo_ibfk_2` FOREIGN KEY (`idEstado_equipo`) REFERENCES `estado_equipo` (`idEstado_equipo`),
  CONSTRAINT `equipo_ibfk_3` FOREIGN KEY (`idUnidad`) REFERENCES `unidad` (`idUnidad`),
  CONSTRAINT `equipo_ibfk_4` FOREIGN KEY (`idOrden_compra`) REFERENCES `orden_compra` (`idOrden_compra`),
  CONSTRAINT `equipo_ibfk_5` FOREIGN KEY (`idModelo_equipo`) REFERENCES `modelo_equipo` (`idModelo_Equipo`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Estructura de tabla para la tabla `traslado`
--

CREATE TABLE `traslado` (
  `idTraslado` int(11) NOT NULL AUTO_INCREMENT,
  `fechatraslado` date DEFAULT NULL,
  `rutadocumentoTraslado` varchar(50) DEFAULT NULL,
  `idUnidadDestino` int(11) NOT NULL,
  `idUnidadOrigen` int(11) DEFAULT NULL,
  `estaFirmadoTraslado` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`idTraslado`),
  CONSTRAINT `fk_idUnidadOrigen` FOREIGN KEY (`idUnidadOrigen`) REFERENCES `unidad` (`idUnidad`),
  CONSTRAINT `traslado_ibfk_1` FOREIGN KEY (`idUnidadDestino`) REFERENCES `unidad` (`idUnidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Estructura de tabla para la tabla `traslacion`
--

CREATE TABLE `traslacion` (
  `idTraslado` int(11) NOT NULL,
  `idEquipo` int(11) NOT NULL,
  PRIMARY KEY(`idTraslado`,`idEquipo`),
  CONSTRAINT `traslacion_ibfk_1` FOREIGN KEY (`idTraslado`) REFERENCES `traslado` (`idTraslado`),
  CONSTRAINT `traslacion_ibfk_2` FOREIGN KEY (`idEquipo`) REFERENCES `equipo` (`idEquipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Estructura de tabla para la tabla `detalle_traslado`
--

CREATE TABLE `detalle_traslado` (
  `idDetalle_traslado` int(11) NOT NULL AUTO_INCREMENT,
  `observacionDetalletraslado` varchar(45) DEFAULT NULL,
  `idTraslado` int(11) NOT NULL,
  PRIMARY KEY (`idDetalle_traslado`),
  CONSTRAINT `detalle_traslado_ibfk_1` FOREIGN KEY (`idTraslado`) REFERENCES `traslado` (`idTraslado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Estructura de tabla para la tabla `incidencia`
--

CREATE TABLE `incidencia` (
  `idIncidencia` int(11) NOT NULL AUTO_INCREMENT,
  `nombreIncidencia` varchar(45) DEFAULT NULL,
  `observacionIncidencia` varchar(45) DEFAULT NULL,
  `rutaactaIncidencia` varchar(45) DEFAULT NULL,
  `fechaIncidencia` date DEFAULT NULL,
  `idEquipo` int(11) NOT NULL,
  `numDocumentos` int(11) DEFAULT NULL,
  `estadoIncidencia` ENUM('pendiente', 'cerrado', 'abierta', 'servicio tecnico', 'equipo reparado', 'equipo cambiado') DEFAULT 'pendiente',
  PRIMARY KEY (`idIncidencia`),
  CONSTRAINT `incidencia_ibfk_1` FOREIGN KEY (`idEquipo`) REFERENCES `equipo` (`idEquipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Estructura de tabla para la tabla `equipo_asignacion`
--

CREATE TABLE `equipo_asignacion` (
  `idEquipoAsignacion` INT PRIMARY KEY AUTO_INCREMENT,
  `idAsignacion` INT NOT NULL,
  `idEquipo` INT NOT NULL,
  CONSTRAINT `fk_equipo_asignacion_idAsignacion` FOREIGN KEY (`idAsignacion`) REFERENCES `asignacion` (`idAsignacion`),
  CONSTRAINT `fk_equipo_asignacion_idEquipo` FOREIGN KEY (`idEquipo`) REFERENCES `equipo` (`idEquipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Estructura de tabla para la tabla `devolucion`
--

CREATE TABLE `devolucion` (
  `idDevolucion` INT PRIMARY KEY AUTO_INCREMENT,
  `fechaDevolucion` DATE DEFAULT NULL,
  `observacionDevolucion` VARCHAR(250) DEFAULT NULL,
  `idEquipoAsignacion` INT NOT NULL,
  CONSTRAINT `fk_devolucion_idAsignacion` FOREIGN KEY (`idEquipoAsignacion`) REFERENCES `equipo_asignacion` (`idEquipoAsignacion`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `nombreUsuario` varchar(30) NOT NULL,
  `contrasennaUsuario` varchar(80) DEFAULT NULL,
  `privilegiosAdministrador` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`nombreUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Estructura Stand-in para la vista `super_equipo`
-- (Véase abajo para la vista actual)
--

CREATE TABLE IF NOT EXISTS `super_equipo` (
  `idEquipo` INT(11),
  `Cod_inventarioEquipo` VARCHAR(20),
  `Num_serieEquipo` VARCHAR(20),
  `ObservacionEquipo` VARCHAR(250),
  `codigoproveedor_equipo` VARCHAR(45),
  `macEquipo` VARCHAR(45),
  `imeiEquipo` VARCHAR(45),
  `numerotelefonicoEquipo` VARCHAR(12),
  `idTipo_equipo` INT(11),
  `nombreTipo_equipo` VARCHAR(45),
  `idMarca_Equipo` INT(11), 
  `nombreMarcaEquipo` VARCHAR(45),
  `idEstado_equipo` INT(11),
  `nombreEstado_equipo` VARCHAR(45),
  `idUnidad` INT(11),
  `nombreUnidad` VARCHAR(45),
  `idOrden_compra` VARCHAR(45),
  `nombreOrden_compra` VARCHAR(45),
  `idModelo_equipo` INT(11),
  `nombreModeloequipo` VARCHAR(45),
  `nombreFuncionario` VARCHAR(45),
  `rutFuncionario` VARCHAR(20),
  `nombreIncidencia` VARCHAR(45)
);
--
-- Estructura para la vista `super_equipo`
--
DROP TABLE IF EXISTS `super_equipo`;


CREATE ALGORITHM=UNDEFINED 
DEFINER=`root`@`localhost` 
SQL SECURITY DEFINER 
VIEW `super_equipo` AS 
SELECT 
    `e`.`idEquipo` AS `idEquipo`, 
    `e`.`Cod_inventarioEquipo` AS `Cod_inventarioEquipo`,
    `e`.`Num_serieEquipo` AS `Num_serieEquipo`, 
    `e`.`ObservacionEquipo` AS `ObservacionEquipo`, 
    `e`.`codigoproveedor_equipo` AS `codigoproveedor_equipo`, 
    `e`.`macEquipo` AS `macEquipo`, 
    `e`.`imeiEquipo` AS `imeiEquipo`, 
    `e`.`numerotelefonicoEquipo` AS `numerotelefonicoEquipo`, 
    `te`.`idTipo_equipo` AS `idTipo_equipo`, 
    `te`.`nombreTipo_equipo` AS `nombreTipo_equipo`,
    `ma`.`idMarca_Equipo` AS `idMarca_Equipo`,
    `ma`.`nombreMarcaEquipo` AS `nombreMarcaEquipo`,
    `ee`.`idEstado_equipo` AS `idEstado_equipo`, 
    `ee`.`nombreEstado_equipo` AS `nombreEstado_equipo`, 
    `u`.`idUnidad` AS `idUnidad`, 
    `u`.`nombreUnidad` AS `nombreUnidad`, 
    `oc`.`idOrden_compra` AS `idOrden_compra`, 
    `oc`.`nombreOrden_compra` AS `nombreOrden_compra`, 
    `moe`.`idModelo_Equipo` AS `idModelo_equipo`, 
    `moe`.`nombreModeloequipo` AS `nombreModeloequipo`, 
    `f`.`nombreFuncionario` AS `nombreFuncionario`, 
    `f`.`rutFuncionario` AS `rutFuncionario`
FROM 
    `equipo` `e`
    JOIN `modelo_equipo` `moe` 
        ON (`moe`.`idModelo_Equipo` = `e`.`idModelo_equipo`)
    JOIN `marca_tipo_equipo` `mte`
        ON (`moe`.`idMarca_Tipo_Equipo` = `mte`.`idMarcaTipo`)
    JOIN `marca_equipo` `ma`
        ON (`ma`.`idMarca_Equipo` = `mte`.`idMarca_Equipo`)
    JOIN `tipo_equipo` `te`
        ON (`mte`.`idTipo_equipo` = `te`.`idTipo_equipo`)
    JOIN `estado_equipo` `ee` 
        ON (`ee`.`idEstado_equipo` = `e`.`idEstado_equipo`)
    JOIN `unidad` `u` 
        ON (`u`.`idUnidad` = `e`.`idUnidad`)
    JOIN `orden_compra` `oc` 
        ON (`oc`.`idOrden_compra` = `e`.`idOrden_compra`)
    LEFT JOIN `equipo_asignacion` `ea` 
        ON (`ea`.`idEquipo` = `e`.`idEquipo` AND `ea`.`idAsignacion` = (
            SELECT `idAsignacion` 
            FROM `equipo_asignacion` 
            WHERE `idEquipo` = `e`.`idEquipo` 
            ORDER BY `idAsignacion` DESC 
            LIMIT 1
        ))
    LEFT JOIN `asignacion` `a` 
        ON (`a`.`idAsignacion` = `ea`.`idAsignacion` AND `a`.`ActivoAsignacion` = 1)
    LEFT JOIN `funcionario` `f` 
        ON (`f`.`rutFuncionario` = `a`.`rutFuncionario`);




--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`nombreUsuario`, `contrasennaUsuario`, `privilegiosAdministrador`) VALUES
('admin', '$2b$12$QUyjfHNIiGxsqPXjSKs38O7RCN2XfXfpzIxrzMNQw0VmBvF0J3cgG', 1),
('martin', '$2b$12$latvxc1R56a94bkyuJHVHe8fNMpVd247CYM78LtyzhKfqRrqTDYOa', 0),
('usuario_normal', '$2b$12$AIHWrdksjmF7AApn02/vRuC2qGMe8QcButv15WNZSxRkm8BqHLm3S', 0);

--
-- Volcado de datos para la tabla `provincia`
--

INSERT INTO `provincia` (`idProvincia`, `nombreProvincia`) VALUES
(1, 'Concepcion'),
(2, 'Arauco'),
(3, 'Biobío');

--
-- Volcado de datos para la tabla `comuna`
--
-- SET GLOBAL local_infile = 1;

-- SET FOREIGN_KEY_CHECKS = 0;

-- Insertar datos en comuna
INSERT INTO `comuna` (`idComuna`, `nombreComuna`, `idProvincia`) VALUES
(1, 'Concepcion', 1),
(2, 'Coronel', 1),
(3, 'Chiguayante', 1),
(4, 'Florida', 1),
(5, 'Hualqui', 1),
(6, 'Lota', 1),
(7, 'Penco', 1),
(8, 'San Pedro de la Paz', 1),
(9, 'Santa Juana', 1),
(10, 'Talcahuano', 1),
(11, 'Tome', 1),
(12, 'Hualpen', 1),
(13, 'Lebu', 2),
(14, 'Arauco', 2),
(15, 'Cañete', 2),
(16, 'Contulmo', 2),
(17, 'Curanilahue', 2),
(18, 'Los Álamos', 2),
(19, 'Tirúa', 2),
(20, 'Los Angeles', 3),
(21, 'Antuco', 3),
(22, 'Cabrero', 3),
(23, 'Laja', 3),
(24, 'Mulchen', 3),
(25, 'Nacimiento', 3),
(26, 'Negrete', 3),
(27, 'Santa Barbara', 3),
(28, 'Tucapel', 3),
(29, 'Alto Biobío', 3),
(30, 'San Rosendo', 3),
(31, 'Quilleco', 3),
(32, 'Quilaco', 3),
(33, 'Yumbel', 3);

-- Cargar datos desde el archivo CSV a la tabla unidad
-- LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/UNUDADES_add.csv'
-- LOAD DATA INFILE 'var/lib/mysql-files/UNUDADES_add.csv'
-- INTO TABLE unidad
-- FIELDS TERMINATED BY ';'  
-- ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (idUnidad, nombreUnidad, contactoUnidad, direccionUnidad, idComuna, idModalidad);

-- Cargar datos desde el archivo CSV a la tabla funcionario
-- LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/FUNCIONARIOS_add.csv'
-- LOAD DATA INFILE 'var/lib/mysql-files/FUNCIONARIOS_add.csv'
-- INTO TABLE funcionario
-- FIELDS TERMINATED BY ';' 
-- ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (rutFuncionario, nombreFuncionario, cargoFuncionario, correoFuncionario, idUnidad);


--  SET FOREIGN_KEY_CHECKS = 1;


-- Insersion de datos para la tabla `modalidad`
INSERT INTO `modalidad` (`idModalidad`, `nombreModalidad`) VALUES
(1, 'CLASICO'),
(2, 'ALTERNATIVO'),
(3, 'OFICINA'),
(4, 'PMI'),
(5, 'CECI');

-- Insersion de datos para la tabla `estado_equipo`
INSERT INTO `estado_equipo` (`idEstado_equipo`, `nombreEstado_equipo`) VALUES 
(1, 'SIN ASIGNAR'),
(2, 'En Uso'),
(3, 'Siniestro'),
(4, 'Baja'),
(5, 'Mantencion');

--
-- Volcado de datos para la tabla `tipo_adquisicion`
--
INSERT INTO `tipo_adquisicion` (`idTipo_adquisicion`, `nombre_tipo_adquisicion`) VALUES
(1, 'COMPRA'),
(2, 'ARRIENDO'),
(3, 'PRÉSTAMO'),
(4, 'COMODATTO');

INSERT INTO `marca_equipo` (`idMarca_Equipo`, `nombreMarcaEquipo`) VALUES
(1, 'LG'),
(2, 'Samsung'),
(3, 'VIEWSONIC'),
(4, 'EPSON'),
(5, 'CANON'),
(6, 'HP'),
(7, 'TOSHIBA'),
(8, 'LENOVO'),
(9, 'PHILCO');

INSERT INTO `tipo_equipo` (`idTipo_equipo`, `nombreTipo_equipo`) VALUES
(1, 'COMPUTADORES DE ESCRITORIO Y AIO'),
(2, 'NOTEBOOK'),
(3, 'IMPRESORA'),
(4, 'ESCANER'),
(5, 'PLOTTER'),
(6, 'PROYECTOR'),
(7, 'MONITOR');

INSERT INTO `marca_tipo_equipo` (`idMarca_Equipo`, `idTipo_equipo`) VALUES
(8, 1),
(8, 2),
(6, 2),
(7, 2),
(4, 3),
(6, 3),
(5, 3),
(6, 4),
(6, 5),
(5, 5),
(4, 6),
(1, 6),
(3, 6),
(9, 6),
(2, 7),
(1, 7);

INSERT INTO `modelo_equipo` (`nombreModeloequipo`, `idMarca_Tipo_Equipo`) VALUES
('Thinkcentre M700z', 1),
('Thinkcentre E73z', 1),
('V510z', 1),
('Thinkcentre E71z', 1),
('V530', 1),
('V330', 2),
('Thinkpad P51', 2),
('Thinkpad X250', 2),
('V110', 2),
('Thinkpad E431', 2),
('Lenovo L470', 2),
('V310', 2),
('B40-80', 2),
('Thinkpad E440', 2),
('Thinkpad X260', 2),
('Thinkpad X270', 2),
('Thinkpad P50', 2),
('Thinkpad L460', 2),
('K14', 2),
('440 G1', 3),
('240 G5', 3),
('340 G1', 3),
('340 G2', 3),
('C55 C5213K', 4),
('DFX 9000', 5),
('L375', 5),
('L380', 5),
('L395', 5),
('L3110', 5),
('L3250', 5),
('L6191', 5),
('L5190', 5),
('L365', 5),
('P1100w', 6),
('Smart Tank 515', 6),
('PIXMA G2160', 7),
('700 S2 Flow', 8),
('T520', 9),
('Ipf785', 10),
('H552A', 11),
('H436A', 11),
('EMP S5', 11),
('H430', 11),
('H553A', 11),
('719A', 11),
('723A', 11),
('H839A', 11),
('PH550G', 12),
('PJD5123', 13),
('PJD7383', 13),
('VS13868', 13),
('VS17337', 13),
('PJD5134', 13),
('3113N', 14),
('29UB55', 12),
('S22A33ANHL', 15),
('20M35A', 16);

INSERT INTO `proveedor` (`nombreProveedor`) VALUES
('JUNJI'),
('SONDA'),
('Technosystems'); 



INSERT INTO `unidad` (`idUnidad`, `nombreUnidad`, `contactoUnidad`, `direccionUnidad`, `idComuna`, `idModalidad`) VALUES
(8101098, 'Direccion Regional', '412125510', 'ohiggins poniente 77', 1, 3),
(8101001, 'PEQUENA PEWEN', '44921213', 'PJE C 74 POBL TENIENTE MERINO I BARRIO NORTE', 1, 1),
(8101002, 'CARACOLITO','443671761' , 'PASAJE 11 N 289 POBLACION TENIENTE MERINO II CONCEPCION', 1, 1),
(8101003, 'NINOS EN ACCION', '443671764', 'AV LAGUNA REDONDA 2320', 1, 1),
(8101005, 'PETER PAN', 'sin contacto', 'CAMILO HENRIQUEZ 2505 CONCEPCION', 1, 1),
(8101006, 'COSTANERA SUR', '443670124', 'RANCAGUA 219 PEDRO DE VALDIVIA BAJO CONCEPCION', 1, 1),
(8101031, 'VILLA CAP', '443671776', 'AVENIDA PRINCIPAL 364 VILLA CAP CONCEPCION', 1, 1),
(8101032, 'UBB COLLAO ENTRE VALLES', '443670117', 'CAMINO A NONGUEN 430 CONCEPCION', 1, 1),
(8101033, 'MAGALLANES', '443671778', 'MAGALLANES 1470 TERRAZAS LAS LOMAS CONCEPCION', 1, 1),
(8101041, 'LOS CISNES', '443671781', 'LOS PIBES 40 POBL LAS LAGUNAS BARRIO NORTE', 1, 1),
(8101042, 'LO GALINDO', '443670115', 'AV ANDALIEN 1359 BARRIO MODELO SECTOR SANTA SABINA', 1, 1),
(8101044, 'HIJOS DE LA TIERRA', '443671783', 'GALVARINO 1080 CONCEPCION', 1, 1),
(8102001, 'BERTA', '443671503', 'Millabu 543 Poblacion Berta', 2, 1),
(8102046, 'PEUMAYEN', '443671505', 'ANDALIEN 3475 VILLA ESCUADRON CORONEL', 2, 1),
(8102050, 'LIHUEN', '443671506', 'Juan Leal Silva 1213 La Pena', 2, 1),
(8102051, 'SUENOS DE ESPERANZA DE GABRIELA MISTRAL', '443671507', 'Avenida Las Torres Ex El Maite N 3357', 2, 1),
(8103001, 'CHIGUAY', '443670127', 'La Marina 519', 3, 1),
(8103002, 'LA LEONERA', '443671787', 'Los Andes Esquina Escocia s n La Leonera', 3, 1),
(8103003, 'HEROES DEL SOL', '443671790', 'La Marina s n', 3, 1),
(8103009, 'FUTURA ESPERANZA', '443671791', 'Italia 600 Villa La Leonera', 3, 1),
(8106001, 'CALERO SUR', '443671508', 'Arturo Perez Canto s n Pob Calero Sur', 6, 1),
(8106002, 'BALDOMERO LILLO', '443671509', 'Evaristo Azocar 62 Fundicion Lota', 6, 1),
(8106003, 'MATIAS COUSINO', '443671510', 'Juan Manuel del Valle 498 Lota Alto', 6, 1),
(8106004, 'LAS ABEJITAS', '443671511', 'Poblacion libertad calle miramar s n Lota', 6, 1),
(8107001, 'LORD COCHRANE', '443671473', 'Yerrbas Buenas 30 Penco', 7, 1),
(8107002, 'MI MUNDO DE DULZURA', '443671474', 'Las Heras 75', 7, 1),
(8107021, 'PEQUENOS CONQUISTADORES', '443671480', 'Esteban de Soza 440 lomas del Conquistador Penco', 7, 1),
(8107022, 'TESOROS DEL MAR', '443671481', 'Camino viejo n 141 Pob Mejoreros', 7, 1),
(8108001, 'NUESTRA SENORA DE LAS NIEVES', '443671513', 'Avda 05 de octubre 375 boca sur', 8, 1),
(8108015, 'ESPUMA DE MAR', '443671517', 'Calle Diguillin n 956 Pob Cardenal Raul Silva Henriquez', 8, 1),
(8108025, 'NINOS DEL MAR', '443671520', 'Calle Piedra de Francia n 300 Sector Valle La Piedra Boca Sur', 8, 1),
(8110005, 'LA GLORIA', '443671482 - 443671483 - 443671484', 'AURELIO COVENA 495 HIGUERAS THNO', 10, 1),
(8110006, 'PATRICIO LYNCH', '443671485 - 443671486 - 443671487', 'SAN MIGUEL 526 POBLACION PATRICIO LYNCH TALCAHUANO', 10, 1),
(8110032, 'CRUZ DEL SUR', '443671492', 'VOLCAN HUDSON 315 POBLACION CRUZ DEL SUR TALCAHUANO', 10, 1),
(8111001, 'BRISAS DEL MAR', '443671497', 'Esperanza 640 Poblacion 18 de septiembre Tome', 11, 1),
(8111028, 'RAFAEL', '443671502', 'Ohiggins 460 Rafael', 11, 1),
(8111029, 'LOS BLOQUES', 'sin contacto', 'Calle Bio Bio 2730 Loma Larga Tome', 11, 1),
(8112001, 'ALONDRA', '443671462', 'QUINCHAO S N POB PRESIDENTE BULNES', 12, 1),
(8112002, 'CABO AROCA', '443671463', 'SUIZA 2310 POBLACION CABO AROCA HUALPEN', 12, 1),
(8112003, 'MIYALI', '443671464', 'GRAN BRETANA ESQ YUGOESLAVIA S N POBLACION 18 DE SEPTIEMBRE HUALPEN', 12, 1),
(8112004, 'WALT DISNEY', '443671465', 'BELGICA ESQUINA SUIZA ARMANDO ALARCON DEL CANTO HUALPEN', 12, 1),
(8112005, 'BARQUITO DE ILUSIONES', '443671467', 'QUEMCHI 8375 POBLACION LAN C HUALPEN', 12, 1),
(8112006, 'PASO A PASITO', '443671468', 'RUMANIA 2455', 12, 1),
(8112007, 'RENE SCHNEIDER', '443671799', 'MULCHEN 171 POB RENE SCHNEIDER', 12, 1),
(8112008, 'BOTECITO DE LENGA', '443671471', 'EL FARO 348 CALETA LENGA HUALPEN', 12, 1),
(8112016, 'SONRISAS DE COLORES RECONQUISTA', '443671472', 'LA RECONQUISTA 4185 POBLACION CRISPULO GANDARA HUALPEN', 12, 1),
(8201001, 'BOCA LEBU', '443671802', 'POBLACION DIEGO PORTALES LUIS SAGARDIA S N', 13, 1),
(8201002, 'EL PUENTE', '443671803', 'Diego Duble Urrutia S N Pobl Cornelio Saavedra Lebu', 13, 1),
(8201018, 'PESCADORES DE SUENOS', '443671808', 'Ignacio Carrera Pinto N 1301', 13, 1),
(8201019, 'MAR DE ESPERANZA', '443671809', 'Calle Esperanza N 1133 poblacion 27 de febrero', 13, 1),
(8202012, 'FLORECER DEL BOSQUE', '443671811', 'ConTuLmo Alto S N Carampangue', 14, 1),
(8202021, 'TIERRA DE NINOS FELICES', '443671812', 'Volcan Llaima N 178 Pobl Villa Don Carlos Arauco', 14, 1),
(8202033, 'GIRASOLES DE CARAMPANGUE', '443671815' , 'Manuel Luengo N 40 Carampangue Arauco Calle Caupolican N 340 Local 3 5 Arauco Corr', 14, 1),
(8202044, 'TRAWUN ANTU', '443671817', 'Villa El Mirador Calle Los Alelies N 19 Arauco', 14, 1),
(8203006, 'ENCANTOS DE SAYEN', '443671832' , 'San Martin N 60 Interior Esc Homero Vigueras Canete', 15, 1),
(8203029, 'SOL NACIENTE', '443671838', 'Camino Publico Ruta P 60 N 780 Huillinco Alto Canete', 15, 1),
(8203030, 'ANTU RAYEN', '443671839', 'Bella Hortensia N 426 Villa Tucapel Canete', 15, 1),
(8205001, 'GOTITAS DE AMOR', '443670112', 'Luis Cruz Martinez S N Pobl Eleuterio Ramirez Curanilahue', 17, 1),
(8205002, 'GABRIELA MISTRAL', '443671819', 'Psj 5 S N Pobl Eleuterio Ramirez Curanilahue', 17, 1),
(8205026, 'PINTANDO SONRISAS', 'sin contacto', 'Calle Arturo Prat N 591 Curanilahue', 17, 1),
(8206038, 'LIWEN PU PICHIKECHE AYINCO', 'sin contacto', 'Calle La Virgen N 66 Cerro Alto Los Alamos', 18, 1),
(8206040, 'GOLONDRINAS', 'sin contacto', 'Av Diego Portales S N Cerro Alto Norte Los Alamos', 18, 1),
(8301001, 'KENNEDY', '443671716', 'Los Canelos 161 Pobl Keneddy', 20, 1),
(8301002, 'SALA CUNA RENACER', '443671717', 'Colo Colo 1245', 20, 1),
(8301003, '21 DE MAYO', 'sin contacto', 'Cholguague 1290 Pobl Paillihue', 20, 1),
(8301004, 'PRINCIPITO', '443671719', 'Volcan Calbuco 393 Pobl Dgo Contreras G', 20, 1),
(8301029, 'P HISTORIADORES', '443671727', 'Avda Oriente N 1891 Villa Los Historiadores', 20, 1),
(8301032, 'ISLA DE LOS TESOROS', '443671728', 'Calle Costanera Quilque 1510 Avda Padre Hurtado', 20, 1),
(8301048, 'HUELLAS DE AMOR', 'sin contacto', 'Marina del Rey N 1257', 20, 1),
(8301052, 'KETRAWE', '443671733', 'Avda Oriente N 2200 Parque Lauquen', 20, 1),
(8301053, 'TREN DE MIS SUENOS', 'sin contacto', 'Rio Huaqui N 275 Pobl 21 de Mayo', 20, 1),
(8301059, 'BROTES DE CHACAY', '443671740', 'Km 18 camino Antuco sector Chacayal Norte', 20, 1),
(8304010, 'MI PEQUENO MUNDO', '443671751', 'Violeta Parra N 2402 Altos del Laja', 23, 1),
(8304011, 'RENACER DE CAPPONI', '443671752', 'Roma N 16 Villa Capponi', 23, 1),
(8305022, 'LELIANTU', '443671743', 'Unzueta N 0250', 24, 1),
(8306011, 'ELUNEY', '443671753', 'Juan Paredes Pasmino N 1904 pobl Nahuelbuta', 25, 1),
(8307001, 'TRENCITO DE COIGUE', '443671754', 'Joaquin Diaz Garces S N Coigue', 26, 1),
(8311001, 'ABEJITAS', '443671744', 'Carrera S N', 27, 1),
(8312008, 'HERENCIA DE HUEPIL', 'sin contacto', 'Arturo Prat 375 Huepil', 28, 1),
(8101010, 'LOS DUENDECITOS TRAVIESOS', '443671771', 'MANUEL GUTIERREZ 1745 BARRIO NORTE CONCEPCION', 1, 2),
(8101016, 'RAYITO DE SOL KM 10', '443671775', 'LOS ALAMOS 327 VILLA JUAN RIQUELME LARAY KM10', 1, 2),
(8106011, 'PELUSITA', '443671512', 'Pob 9 de Agosto Calle Chacabuco s n', 6, 2),
(8107003, 'LAS CUNCUNITAS', '443671475', 'Uno Sur s n La Greda', 7, 2),
(8107004, 'MANITOS PINTADAS', '443671476', 'Independencia s n Pob Jaime Lea Plaza', 7, 2),
(8107005, 'CAMINITO DE COLORES', '443671478', 'Pasaje San Francisco C Calle Victoria N 35 Sector la Ermita Penco', 7, 2),
(8107006, 'FLORCITA SILVESTRE', '443671479', 'Venecia n 130 Villa Italia Lirquen Penco', 7, 2),
(8108003, 'LAS MANITOS', 'sin contacto', 'Pasaje las Torres s n Candelaria', 8, 2),
(8108004, 'PEDACITO DE CIELO', 'sin contacto', 'Pasaje 1 n 431 Sector Los Bloques de Michaihue', 8, 2),
(8108005, 'LOS CARINOSITOS', '443671516', 'Avda Daniel Belmar n 680 Boca Sur', 8, 2),
(8110014, 'LUCERITO', '443671488', 'TARAPACA 830 POB DIEGO PORTALES THNO', 10, 2),
(8110017, 'SANSANITO', '443671489', 'PUNTA LILEMO 660', 10, 2),
(8110023, 'ARCOIRIS DE AMOR', '443671491', 'PLAYA EL GALGO 1283 VILLA BADARAN THNO', 10, 2),
(8111007, 'MI PEQUENO MUNDO', '443671498', 'Avda Bellavista Central 0890 Bellavista Interior Escuela E 420', 11, 2),
(8111010, 'HOJITAS DE PARRA', '443671499', 'Av Cardenal Samorey s n Punta de Parra', 11, 2),
(8111013, 'GOTITAS DE AMOR', '443671500', 'Los Almendros 683', 11, 2),
(8202003, 'ESTRELLITA DE MAR', 'sin contacto', 'ALONSO DE ERCILLA S N LARAQUETE', 14, 2),
(8204001, 'LOS CARINOSITOS', '443671840', 'Esmeralda S N sector Villa Rivas', 16, 2),
(8205007, 'LAS ARDILLITAS', '443671822', 'Mina Peumo S N Poblacion Pioneros del Carbon', 17, 2),
(8205025, 'LA FAMILIA', '443671825', 'Santa Elena S N', 17, 2),
(8207001, 'CAU CURA', '443671841', 'Ohiggins S N Quidico', 19, 2),
(8301007, 'CARINOSITOS', 'sin contacto', 'Otawa 880 Pobl Montreal', 20, 2),
(8301010, 'CASITA DE MIS SUENOS', '443671725', 'Lago Todos los Santos 1484 Villa Departamental', 20, 2),
(8301012, 'EL HORIZONTE', '443671726', 'Av Estanislao Anguita con Bombero Rioseco', 20, 2),
(8303001, 'NUBELUZ', '443671741', 'Escuela E 1104 Charrua', 22, 2),
(8311008, 'LAS CAMPANITAS RINCONADA', '443671745', 'Rinconada Estacion Medico Rural', 27, 2),
(8314003, 'RALCO LEPOY', '443671747', 'Villa Ralco S N', 29, 2),
(8102043, 'GOTITA DE FE', '443671504', 'Avenida Escuadron N 3300 Lagunillas 3', 2, 4),
(8104012, 'GRANERILLOS RAYITO DE LUZ', '443671794', 'GRANERILLOS S N EX ESCUELA BASICA G 455 GRANERILLOS', 4, 4),
(8104017, 'SEMBRADORES DE LUZ', '443671797', 'ESCUELA CANCHA LOS MONTEROS FLORIDA', 4, 4),
(8105007, 'CONSTRUYENDO FUTURO', 'sin contacto', 'CALLE RIO BIOBIO 298 POBLACION ENTRE RIOS', 5, 4),
(8108018, 'MIS PRIMEROS PASOS', '443671518', 'Avda Las Torres 3468 Primera Etapa San Pedro de La Costa', 8, 4),
(8110040, 'ESTRELLITAS DE MAR', '443671493', 'PRINCIPAL 80 CALETA TUMBES', 10, 4),
(8110043, 'SONRISAS DE NINOS I', '443671494', 'BENAVENTE 1125 COLEGIO SIMONS TALCAHUANO', 10, 4),
(8110045, 'LUZ DE ESPERANZA', '443671495', 'CATEMU 7132 DIEGO PORTALES II TALCAHUANO', 10, 4),
(8110049, 'SONRISAS DE NINOS II', '443671496', 'BENAVENTE 1525 COLEGIO SIMONS TALCAHUANO', 10, 4),
(8301047, 'PASITO SEGURO', '443671731', 'Bombero Francisco Rioseco 2212', 20, 4),
(8301050, 'PATA DE GALLINA', '443671732', 'Sector Pata de Gallina Km 2 4', 20, 4),
(8301057, 'LA PERLITA', '443671739', 'Escuela G 923 Teniente Merino La Perla S N', 20, 4),
(8314029, 'KUPULWE', '443671749', 'Comunidad Trapa Trapa S N', 29, 4),
(8314040, 'EL BARCO', 'sin contacto', 'Sector El Barco', 29, 4),
(8203007, 'JUGANDO CANTANDO', '443671833' , 'Escuela Garcia Hurtado de Mendoza sector rural Ponotro s n comuna Canete', 15, 4),
(8203020, 'RELMU RAYEN', '443671836', 'Escuela Paicavi Sector paicavi grande Canete', 15, 4),
(8203022, 'SEMILLITAS TRANGUILBORO', 'sin contacto', 'Tranguilboro sin numero Canete', 15, 4),
(8205014, 'LOS NINOS SON FELICES', '443671823', 'Ismael Jara n s Cerro la Perdiz', 17, 4),
(8206032, 'LOS PITUFOS LOS RIOS', '443671827', 'sala de escuela los Gualles', 18, 4),
(8206033, 'LOS CARINOSITOS', '443671828', 'Tres Pinos Canete', 18, 4),
(8207024, 'PEHUMAHUE TIRUA', '443671842', 'pasaje el bosque sin numero Tirua', 19, 4),
(8207028, 'PEWMA PICHIKECHE', '443671843', 'Tranaquepe sin numero sector escuela comuna de Tirua', 19, 4),
(8207029, 'WEFACHANTU PICHICHE', '443671845', 'ponotro s n Al frente de la copec', 19, 4),
(8105014, 'TALCAMAVIDA RAYENCURA', '443671798', 'LOS CARRERAS 323 TALCAMAVIDA HUALQUI', 5, 5),
(8111025, 'LOS PECESITOS', '443671501', 'Camino Principal Coliumo Aldea Esperanza s n', 11, 5),
(8301045, 'FUERTECITO', '443671729', 'ANDRES MATERNE S N SAN CARLOS PUREN', 20, 5),
(8301046, 'PEQUENOS SONADORES', '443671730', 'San Gabriel 1804 pobl Basilio Munoz', 20, 5),
(8307007, 'SEMILLITA DE RIHUE', '443671759', 'Sector Rihue S N frente a Escuela', 26, 5),
(8202031, 'FELIPE CUBILLOS SIGALL', '443671813', 'Arauco Lebu Ruta P 40 km50', 14, 5),
(8202032, 'MELIRUPO', '443671814', 'sector Merilupo camino las puentes S N', 14, 5),
(8203012, 'LELBUN ALIWEN', '443671834', 'Sector Pocuno Canete', 15, 5),
(8203013, 'LELUNEY', '443671835', 'Tres sauces camino cayucupil S N Canete', 15, 5),
(8205019, 'RAYITO DE SOL', '443671824', 'Camilo Henriquez s n cerro verde', 17, 5);



SET FOREIGN_KEY_CHECKS=0;


INSERT INTO `funcionario` (`rutFuncionario`, `nombreFuncionario`, `cargoFuncionario`, `correoFuncionario`, `idUnidad`) VALUES
('8101098', 'Direccion Regional', 'ENCARGADA/O', 'junji8101098@junji.cl', 8101098),
('8101001', 'PEQUENA PEWEN', 'ENCARGADA/O', 'junji8101001@junji.cl', 8101001),
('8101002', 'CARACOLITO', 'ENCARGADA/O', 'junji8101002@junji.cl', 8101002),
('8101003', 'NINOS EN ACCION', 'ENCARGADA/O', 'junji8101003@junji.cl', 8101003),
('8101005', 'PETER PAN', 'ENCARGADA/O', 'junji8101005@junji.cl', 8101005),
('8101006', 'COSTANERA SUR', 'ENCARGADA/O', 'junji8101006@junji.cl', 8101006),
('8101031', 'VILLA CAP', 'ENCARGADA/O', 'junji8101031@junji.cl', 8101031),
('8101032', 'UBB COLLAO ENTRE VALLES', 'ENCARGADA/O', 'junji8101032@junji.cl', 8101032),
('8101033', 'MAGALLANES', 'ENCARGADA/O', 'junji8101033@junji.cl', 8101033),
('8101041', 'LOS CISNES', 'ENCARGADA/O', 'junji8101041@junji.cl', 8101041),
('8101042', 'LO GALINDO', 'ENCARGADA/O', 'junji8101042@junji.cl', 8101042),
('8101044', 'HIJOS DE LA TIERRA', 'ENCARGADA/O', 'junji8101044@junji.cl', 8101044),
('8102001', 'BERTA', 'ENCARGADA/O', 'junji8102001@junji.cl', 8102001),
('8102046', 'PEUMAYEN', 'ENCARGADA/O', 'junji8102046@junji.cl', 8102046),
('8102050', 'LIHUEN', 'ENCARGADA/O', 'junji8102050@junji.cl', 8102050),
('8102051', 'SUENOS DE ESPERANZA DE GABRIELA MISTRAL', 'ENCARGADA/O', 'junji8102051@junji.cl', 8102051),
('8103001', 'CHIGUAY', 'ENCARGADA/O', 'junji8103001@junji.cl', 8103001),
('8103002', 'LA LEONERA', 'ENCARGADA/O', 'junji8103002@junji.cl', 8103002),
('8103003', 'HEROES DEL SOL', 'ENCARGADA/O', 'junji8103003@junji.cl', 8103003),
('8103009', 'FUTURA ESPERANZA', 'ENCARGADA/O', 'junji8103009@junji.cl', 8103009),
('8106001', 'CALERO SUR', 'ENCARGADA/O', 'junji8106001@junji.cl', 8106001),
('8106002', 'BALDOMERO LILLO', 'ENCARGADA/O', 'junji8106002@junji.cl', 8106002),
('8106003', 'MATIAS COUSINO', 'ENCARGADA/O', 'junji8106003@junji.cl', 8106003),
('8106004', 'LAS ABEJITAS', 'ENCARGADA/O', 'junji8106004@junji.cl', 8106004),
('8107001', 'LORD COCHRANE', 'ENCARGADA/O', 'junji8107001@junji.cl', 8107001),
('8107002', 'MI MUNDO DE DULZURA', 'ENCARGADA/O', 'junji8107002@junji.cl', 8107002),
('8107021', 'PEQUENOS CONQUISTADORES', 'ENCARGADA/O', 'junji8107021@junji.cl', 8107021),
('8107022', 'TESOROS DEL MAR', 'ENCARGADA/O', 'junji8107022@junji.cl', 8107022),
('8108001', 'NUESTRA SENORA DE LAS NIEVES', 'ENCARGADA/O', 'junji8108001@junji.cl', 8108001),
('8108015', 'ESPUMA DE MAR', 'ENCARGADA/O', 'junji8108015@junji.cl', 8108015),
('8108025', 'NINOS DEL MAR', 'ENCARGADA/O', 'junji8108025@junji.cl', 88108025),
('8110005', 'LA GLORIA', 'ENCARGADA/O', 'junji8110005@junji.cl', 8110005),
('8110006', 'PATRICIO LYNCH', 'ENCARGADA/O', 'junji8110006@junji.cl', 8110006),
('8110032', 'CRUZ DEL SUR', 'ENCARGADA/O', 'junji8110032@junji.cl', 8110032),
('8111001', 'BRISAS DEL MAR', 'ENCARGADA/O', 'junji8111001@junji.cl', 8111001),
('8111028', 'RAFAEL', 'ENCARGADA/O', 'junji8111028@junji.cl', 8111028),
('8111029', 'LOS BLOQUES', 'ENCARGADA/O', 'junji8111029@junji.cl', 8111029),
('8112001', 'ALONDRA', 'ENCARGADA/O', 'junji8112001@junji.cl', 8112001),
('8112002', 'CABO AROCA', 'ENCARGADA/O', 'junji8112002@junji.cl', 8112002),
('8112003', 'MIYALI', 'ENCARGADA/O', 'junji8112003@junji.cl', 8112003),
('8112004', 'WALT DISNEY', 'ENCARGADA/O', 'junji8112004@junji.cl', 8112004),
('8112005', 'BARQUITO DE ILUSIONES', 'ENCARGADA/O', 'junji8112005@junji.cl', 8112005),
('8112006', 'PASO A PASITO', 'ENCARGADA/O', 'junji8112006@junji.cl', 8112006),
('8112007', 'RENE SCHNEIDER', 'ENCARGADA/O', 'junji8112007@junji.cl', 8112007),
('8112008', 'BOTECITO DE LENGA', 'ENCARGADA/O', 'junji8112008@junji.cl', 8112008),
('8112016', 'SONRISAS DE COLORES RECONQUISTA', 'ENCARGADA/O', 'junji8112016@junji.cl', 8112016),
('8201001', 'BOCA LEBU', 'ENCARGADA/O', 'junji8201001@junji.cl', 8201001),
('8201002', 'EL PUENTE', 'ENCARGADA/O', 'junji8201002@junji.cl', 8201002),
('8201018', 'PESCADORES DE SUENOS', 'ENCARGADA/O', 'junji8201018@junji.cl', 8201018),
('8201019', 'MAR DE ESPERANZA', 'ENCARGADA/O', 'junji8201019@junji.cl', 8201019),
('8202012', 'FLORECER DEL BOSQUE', 'ENCARGADA/O', 'junji8202012@junji.cl', 8202012),
('8202021', 'TIERRA DE NINOS FELICES', 'ENCARGADA/O', 'junji8202021@junji.cl', 8202021),
('8202033', 'GIRASOLES DE CARAMPANGUE', 'ENCARGADA/O', 'junji8202033@junji.cl', 8202033),
('8202044', 'TRAWUN ANTU', 'ENCARGADA/O', 'junji8202044@junji.cl', 8202044),
('8203006', 'ENCANTOS DE SAYEN', 'ENCARGADA/O', 'junji8203006@junji.cl', 8203006),
('8203029', 'SOL NACIENTE', 'ENCARGADA/O', 'junji8203029@junji.cl', 8203029),
('8203030', 'ANTU RAYEN', 'ENCARGADA/O', 'junji8203030@junji.cl', 8203030),
('8205001', 'GOTITAS DE AMOR', 'ENCARGADA/O', 'junji8205001@junji.cl', 8205001),
('8205002', 'GABRIELA MISTRAL', 'ENCARGADA/O', 'junji8205002@junji.cl', 8205002),
('8205026', 'PINTANDO SONRISAS', 'ENCARGADA/O', 'junji8205026@junji.cl', 8205026),
('8206038', 'LIWEN PU PICHIKECHE AYINCO', 'ENCARGADA/O', 'junji8206038@junji.cl', 8206038),
('8206040', 'GOLONDRINAS', 'ENCARGADA/O', 'junji8206040@junji.cl', 8206040),
('8301001', 'KENNEDY', 'ENCARGADA/O', 'junji8301001@junji.cl', 8301001),
('8301002', 'SALA CUNA RENACER', 'ENCARGADA/O', 'junji8301002@junji.cl', 8301002),
('8301003', '21 DE MAYO', 'ENCARGADA/O', 'junji8301003@junji.cl', 8301003),
('8301004', 'PRINCIPITO', 'ENCARGADA/O', 'junji8301004@junji.cl', 8301004),
('8301029', 'P HISTORIADORES', 'ENCARGADA/O', 'junji8301029@junji.cl', 8301029),
('8301032', 'ISLA DE LOS TESOROS', 'ENCARGADA/O', 'junji8301032@junji.cl', 8301032),
('8301048', 'HUELLAS DE AMOR', 'ENCARGADA/O', 'junji8301048@junji.cl', 8301048),
('8301052', 'KETRAWE', 'ENCARGADA/O', 'junji8301052@junji.cl', 8301052),
('8301053', 'TREN DE MIS SUENOS', 'ENCARGADA/O', 'junji8301053@junji.cl', 8301053),
('8301059', 'BROTES DE CHACAY', 'ENCARGADA/O', 'junji8301059@junji.cl', 8301059),
('8304001', 'MI PEQUENO MUNDO', 'ENCARGADA/O', 'junji8304001@junji.cl', 8304001),
('8304002', 'RENACER DE CAPPONI', 'ENCARGADA/O', 'junji8304002@junji.cl', 8304002),
('8305022', 'LELIANTU', 'ENCARGADA/O', 'junji8305022@junji.cl', 8305022),
('8306011', 'ELUNEY', 'ENCARGADA/O', 'junji8306011@junji.cl', 8306011),
('8307001', 'TRENCITO DE COIGUE', 'ENCARGADA/O', 'junji8307001@junji.cl', 8307001),
('8311001', 'ABEJITAS', 'ENCARGADA/O', 'junji8311001@junji.cl', 8311001),
('8312008', 'HERENCIA DE HUEPIL', 'ENCARGADA/O', 'junji8312008@junji.cl', 8312008),
('8101010', 'LOS DUENDECITOS TRAVIESOS', 'ENCARGADA/O', 'junji8101010@junji.cl', 8101010),
('8101016', 'RAYITO DE SOL KM 10', 'ENCARGADA/O', 'junji8101016@junji.cl', 8101016),
('8106011', 'PELUSITA', 'ENCARGADA/O', 'junji8106011@junji.cl', 8106011),
('8107003', 'LAS CUNCUNITAS', 'ENCARGADA/O', 'junji8107003@junji.cl', 8107003),
('8107004', 'MANITOS PINTADAS', 'ENCARGADA/O', 'junji8107004@junji.cl', 8107004),
('8107005', 'CAMINITO DE COLORES', 'ENCARGADA/O', 'junji8107005@junji.cl', 8107005),
('8107006', 'FLORCITA SILVESTRE', 'ENCARGADA/O', 'junji8107006@junji.cl', 8107006),
('8108003', 'LAS MANITOS', 'ENCARGADA/O', 'junji8108003@junji.cl', 8108003),
('8108004', 'PEDACITO DE CIELO', 'ENCARGADA/O', 'junji8108004@junji.cl', 8108004),
('8108005', 'LOS CARINOSITOS', 'ENCARGADA/O', 'junji8108005@junji.cl', 8108005),
('8110014', 'LUCERITO', 'ENCARGADA/O', 'junji8110014@junji.cl', 8110014),
('8110017', 'SANSANITO', 'ENCARGADA/O', 'junji8110017@junji.cl', 8110017),
('8110023', 'ARCOIRIS DE AMOR', 'ENCARGADA/O', 'junji8110023@junji.cl', 8110023),
('8111007', 'MI PEQUENO MUNDO', 'ENCARGADA/O', 'junji8111007@junji.cl', 8111007),
('8111010', 'HOJITAS DE PARRA', 'ENCARGADA/O', 'junji8111010@junji.cl', 8111010),
('8111013', 'GOTITAS DE AMOR', 'ENCARGADA/O', 'junji8111013@junji.cl', 8111013),
('8202003', 'ESTRELLITA DE MAR', 'ENCARGADA/O', 'junji8202003@junji.cl', 8202003),
('8204001', 'LOS CARINOSITOS', 'ENCARGADA/O', 'junji8204001@junji.cl', 8204001),
('8205007', 'LAS ARDILLITAS', 'ENCARGADA/O', 'junji8205007@junji.cl', 8205007),
('8205025', 'LA FAMILIA', 'ENCARGADA/O', 'junji8205025@junji.cl', 8205025),
('8207001', 'CAU CURA', 'ENCARGADA/O', 'junji8207001@junji.cl', 8207001),
('8301007', 'CARINOSITOS', 'ENCARGADA/O', 'junji8301007@junji.cl', 8301007),
('8301010', 'CASITA DE MIS SUENOS', 'ENCARGADA/O', 'junji8301010@junji.cl', 8301010),
('8301012', 'EL HORIZONTE', 'ENCARGADA/O', 'junji8301012@junji.cl', 8301012),
('8303001', 'NUBELUZ', 'ENCARGADA/O', 'junji8303001@junji.cl', 8303001),
('8311008', 'LAS CAMPANITAS RINCONADA', 'ENCARGADA/O', 'junji8311008@junji.cl', 8311008),
('8314003', 'RALCO LEPOY', 'ENCARGADA/O', 'junji8314003@junji.cl', 8314003),
('8102043', 'GOTITA DE FE', 'ENCARGADA/O', 'junji8102043@junji.cl', 8102043),
('8104012', 'GRANERILLOS RAYITO DE LUZ', 'ENCARGADA/O', 'junji8104012@junji.cl', 8104012),
('8104017', 'SEMBRADORES DE LUZ', 'ENCARGADA/O', 'junji8104017@junji.cl', 8104017),
('8105007', 'CONSTRUYENDO FUTURO', 'ENCARGADA/O', 'junji8105007@junji.cl', 8105007),
('8108018', 'MIS PRIMEROS PASOS', 'ENCARGADA/O', 'junji8108018@junji.cl', 8108018),
('8110040', 'ESTRELLITAS DE MAR', 'ENCARGADA/O', 'junji8110040@junji.cl', 8110040),
('8110043', 'SONRISAS DE NINOS I', 'ENCARGADA/O', 'junji8110043@junji.cl', 8110043),
('8110045', 'LUZ DE ESPERANZA', 'ENCARGADA/O', 'junji8110045@junji.cl', 8110045),
('8110049', 'SONRISAS DE NINOS II', 'ENCARGADA/O', 'junji8110049@junji.cl', 8110049),
('8301047', 'PASITO SEGURO', 'ENCARGADA/O', 'junji8301047@junji.cl', 8301047),
('8301050', 'PATA DE GALLINA', 'ENCARGADA/O', 'junji8301050@junji.cl', 8301050),
('8301057', 'LA PERLITA', 'ENCARGADA/O', 'junji8301057@junji.cl', 8301057),
('8314029', 'KUPULWE', 'ENCARGADA/O', 'junji8314029@junji.cl', 8314029),
('8314040', 'EL BARCO', 'ENCARGADA/O', 'junji8314040@junji.cl', 8314040),
('8203007', 'JUGANDO CANTANDO', 'ENCARGADA/O', 'junji8203007@junji.cl', 8203007),
('8203020', 'RELMU RAYEN', 'ENCARGADA/O', 'junji8203020@junji.cl', 8203020),
('8203022', 'SEMILLITAS TRANGUILBORO', 'ENCARGADA/O', 'junji8203022@junji.cl', 8203022),
('8205014', 'LOS NINOS SON FELICES', 'ENCARGADA/O', 'junji8205014@junji.cl', 8205014),
('8206032', 'LOS PITUFOS LOS RIOS', 'ENCARGADA/O', 'junji8206032@junji.cl', 8206032),
('8206033', 'LOS CARINOSITOS', 'ENCARGADA/O', 'junji8206033@junji.cl', 8206033),
('8207024', 'PEHUMAHUE TIRUA', 'ENCARGADA/O', 'junji8207024@junji.cl', 8207024),
('8207028', 'PEWMA PICHIKECHE', 'ENCARGADA/O', 'junji8207028@junji.cl', 8207028),
('8207029', 'WEFACHANTU PICHICHE', 'ENCARGADA/O', 'junji8207029@junji.cl', 8207029),
('8105014', 'TALCAMAVIDA RAYENCURA', 'ENCARGADA/O', 'junji8105014@junji.cl', 8105014),
('8111025', 'LOS PECESITOS', 'ENCARGADA/O', 'junji8111025@junji.cl', 8111025),
('8301045', 'FUERTECITO', 'ENCARGADA/O', 'junji8301045@junji.cl', 8301045),
('8301046', 'PEQUENOS SONADORES', 'ENCARGADA/O', 'junji8301046@junji.cl', 8301046),
('8307007', 'SEMILLITA DE RIHUE', 'ENCARGADA/O', 'junji8307007@junji.cl', 8307007),
('8202031', 'FELIPE CUBILLOS SIGALL', 'ENCARGADA/O', 'junji8202031@junji.cl', 8202031),
('8202032', 'MELIRUPO', 'ENCARGADA/O', 'junji8202032@junji.cl', 8202032),
('8203012', 'LELBUN ALIWEN', 'ENCARGADA/O', 'junji8203012@junji.cl', 8203012),
('8203013', 'LELUNEY', 'ENCARGADA/O', 'junji8203013@junji.cl', 8203013),
('8205019', 'RAYITO DE SOL', 'ENCARGADA/O', 'junji8205019@junji.cl', 8205019);
	

SET FOREIGN_KEY_CHECKS=1;

COMMIT;

