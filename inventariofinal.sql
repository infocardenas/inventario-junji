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
  `cargoFuncionario` ENUM('ADMINISTRATIVO', 'AUXILIAR', 'PROFESIONAL', 'TÉCNICO', 'DIRECTOR REGIONAL','JARDIN') NOT NULL,
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
  `nombre_tipo_adquisicion` ENUM('COMPRA', 'ARRIENDO', 'PRÉSTAMO') NOT NULL,
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
SET GLOBAL local_infile = 1;

SET FOREIGN_KEY_CHECKS = 0;

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
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/UNUDADES_add.csv'
INTO TABLE unidad
FIELDS TERMINATED BY ';'  
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(idUnidad, nombreUnidad, contactoUnidad, direccionUnidad, idComuna, idModalidad);

-- Cargar datos desde el archivo CSV a la tabla funcionario
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/FUNCIONARIOS_add.csv'
INTO TABLE funcionario
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(rutFuncionario, nombreFuncionario, cargoFuncionario, correoFuncionario, idUnidad);


SET FOREIGN_KEY_CHECKS = 1;


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
(3, 'PRÉSTAMO');


--
-- para cargar los CSV es necesario seguir los siguientes pasosç
--
-- entrar en C:/ProgramData/MySQL/MySQL Server 8.0/Uploads y agregar los domumentos UNUDADES_add.csv y FUNCIONARIOS_add.csv 
-- es nesesario dar los permisos temporales para la lectura de rutas es nesesario que se ejecute el sigiente comando 
-- SHOW VARIABLES LIKE 'local_infile'; tiene que estar en on si esta en off ejecutar SET GLOBAL local_infile = 1;
--

COMMIT;

