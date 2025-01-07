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
  `nombreUnidad` varchar(45) DEFAULT NULL,
  `contactoUnidad` varchar(45) DEFAULT NULL,
  `direccionUnidad` varchar(45) CHARACTER SET armscii8 COLLATE armscii8_general_ci DEFAULT NULL,
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
  `rutFuncionario` varchar(20) NOT NULL,
  `nombreFuncionario` varchar(45) NOT NULL,
  `cargoFuncionario` varchar(45) DEFAULT NULL,
  `idUnidad` int(11) DEFAULT NULL,
  `correoFuncionario` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`rutFuncionario`),
  CONSTRAINT `funcionario_ibfk_1` FOREIGN KEY (`idUnidad`) REFERENCES `unidad` (`idUnidad`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;



--
-- Estructura de tabla para la tabla `asignacion`
--

CREATE TABLE `asignacion` (
  `idAsignacion` int(11) NOT NULL,
  `fecha_inicioAsignacion` date DEFAULT NULL,
  `ObservacionAsignacion` varchar(250) DEFAULT NULL,
  `rutaactaAsignacion` varchar(45) DEFAULT NULL,
  `ActivoAsignacion` tinyint(4) DEFAULT NULL,
  `rutFuncionario` varchar(20) DEFAULT NULL,
  `idDevolucion` int(11) DEFAULT NULL,
  `fechaDevolucion` date DEFAULT NULL,
  PRIMARY KEY (`idAsignacion`),
  CONSTRAINT `fk_asignacion_funcionario` FOREIGN KEY (`rutFuncionario`) REFERENCES `funcionario` (`rutFuncionario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Estructura de tabla para la tabla `marca_equipo`
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
  `observacionTipoEquipo` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`idTipo_equipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Estructura de tabla para la tabla `marca_tipo_equipo`
--

CREATE TABLE `marca_tipo_equipo` (
  `idMarca_Equipo` int(11) NOT NULL,
  `idTipo_equipo` int(11) NOT NULL,
  PRIMARY KEY (`idMarca_Equipo`, `idTipo_equipo`),
  CONSTRAINT `marca_tipo_equipo_ibfk_1` FOREIGN KEY (`idMarca_Equipo`) REFERENCES `marca_equipo` (`idMarca_Equipo`),
  CONSTRAINT `marca_tipo_equipo_ibfk_2` FOREIGN KEY (`idTipo_equipo`) REFERENCES `tipo_equipo` (`idTipo_equipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Estructura de tabla para la tabla `modelo_equipo`
--

CREATE TABLE `modelo_equipo` (
  `idModelo_Equipo` int(11) NOT NULL AUTO_INCREMENT,
  `nombreModeloequipo` varchar(45) UNIQUE,
  `idTipo_Equipo` int(11) DEFAULT NULL,
  `idMarca_Equipo` int(11) DEFAULT NULL,
  PRIMARY KEY (`idModelo_Equipo`),
  CONSTRAINT `modelo_equipo_ibfk_1` FOREIGN KEY (`idTipo_Equipo`) REFERENCES `tipo_equipo` (`idTipo_equipo`),
  CONSTRAINT `modelo_equipo_ibfk_2` FOREIGN KEY (`idMarca_Equipo`) REFERENCES `marca_equipo` (`idMarca_Equipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Estructura de tabla para la tabla `tipo_adquisicion`
--

CREATE TABLE `tipo_adquisicion` (
  `idTipo_adquisicion` int(11) NOT NULL AUTO_INCREMENT,
  `nombreTipo_adquisicion` varchar(45) NOT NULL,
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
  `idEstado_equipo` int(11) NOT NULL,
  `idUnidad` int(11) NOT NULL,
  `idOrden_compra` varchar(45) NOT NULL,
  `idModelo_equipo` int(11) NOT NULL,
  PRIMARY KEY (`idEquipo`),
  CONSTRAINT `equipo_ibfk_2` FOREIGN KEY (`idEstado_equipo`) REFERENCES `estado_equipo` (`idEstado_equipo`),
  CONSTRAINT `equipo_ibfk_3` FOREIGN KEY (`idUnidad`) REFERENCES `unidad` (`idUnidad`),
  CONSTRAINT `equipo_ibfk_4` FOREIGN KEY (`idOrden_compra`) REFERENCES `orden_compra` (`idOrden_compra`),
  CONSTRAINT `equipo_ibfk_5` FOREIGN KEY (`idModelo_equipo`) REFERENCES `modelo_equipo` (`idModelo_Equipo`)
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
  PRIMARY KEY (`idIncidencia`),
  CONSTRAINT `incidencia_ibfk_1` FOREIGN KEY (`idEquipo`) REFERENCES `equipo` (`idEquipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Estructura de tabla para la tabla `equipo_asignacion`
--

CREATE TABLE `equipo_asignacion` (
  `idAsignacion` int(11) NOT NULL,
  `idEquipo` int(11) NOT NULL,
  PRIMARY KEY (`idAsignacion`,`idEquipo`),
  CONSTRAINT `equipo_asignacion_ibfk_1` FOREIGN KEY (`idAsignacion`) REFERENCES `asignacion` (`idAsignacion`),
  CONSTRAINT `equipo_asignacion_ibfk_2` FOREIGN KEY (`idEquipo`) REFERENCES `equipo` (`idEquipo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Estructura de tabla para la tabla `devolucion`
--

CREATE TABLE `devolucion` (
  `idDevolucion` int(11) NOT NULL,
  `fechaDevolucion` date DEFAULT NULL,
  `observacionDevolucion` varchar(250) DEFAULT NULL,
  `rutaactaDevolucion` varchar(45) DEFAULT NULL,
  `ActivoDevolucion` tinyint(4) DEFAULT NULL,
  `rutFuncionario` varchar(10) NOT NULL,
  PRIMARY KEY (`idDevolucion`)
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

--
-- Volcado de datos para la tabla `modalidad`
--

INSERT INTO `modalidad` (`idModalidad`, `nombreModalidad`) VALUES
(1, 'CLASICO'),
(2, 'ALTERNATIVO'),
(3, 'OFICINA');

--
-- Volcado de datos para la tabla `unidad`
--

INSERT INTO `unidad` (`idUnidad`, `nombreUnidad`, `contactoUnidad`, `direccionUnidad`, `idComuna`, `idModalidad`) VALUES
(1, 'u_de_excel', 'test', '123_calle_falsa', 1, 1),
(2, 'u_de_excel2', 'test', '123_calle_falsa', 2, 1),
(3, 'u_de_excel2', 'test', '123_calle_falsa', 3, 1);

--
-- Volcado de datos para la tabla `funcionario`
--

INSERT INTO `funcionario` (`rutFuncionario`, `nombreFuncionario`, `cargoFuncionario`, `idUnidad`, `correoFuncionario`) VALUES
('1-1', 'ElFuncionario', 'funcionario', 1, 'fun@dominio.cl'),
('10222333k', 'Leticia Letelier', 'Encargada', 2, NULL),
('15222111k', 'Valentina Salgado', 'Encargada', 1, NULL),
('180003339', 'Natalie Ramirez', 'Encargada', 1, NULL),
('190001110', 'Cristina Dominguez', 'Encargada', 3, NULL),
('20941502-', 'martin', '123', 3, NULL),
('20941502-k', 'martin2', 'cargo', 2, NULL),
('21000222k', 'Romina Gonzales', 'Encargada', 2, NULL);

--
-- Volcado de datos para la tabla `asignacion`
--

INSERT INTO `asignacion` (`idAsignacion`, `fecha_inicioAsignacion`, `ObservacionAsignacion`, `rutaactaAsignacion`, `ActivoAsignacion`, `rutFuncionario`, `idDevolucion`, `fechaDevolucion`) VALUES
(146, '2024-06-25', 'set', 'ruta', 0, '1-1', NULL, '2024-06-25'),
(147, '0000-00-00', 'set', 'ruta', 0, '1-1', NULL, '2024-06-25');

--
-- Volcado de datos para la tabla `marca_equipo`
--

INSERT INTO `marca_equipo` (`idMarca_Equipo`, `nombreMarcaEquipo`) VALUES
(101, 'Acer'),
(102, 'Samsung'),
(103, 'Epson'),
(104, 'HP'),
(105, 'Lenovo');

--
-- Volcado de datos para la tabla `tipo_equipo`
--

INSERT INTO `tipo_equipo` (`idTipo_equipo`, `nombreTipo_equipo`, `observacionTipoEquipo`) VALUES
(101, 'AIO', 'test'),
(102, 'Notebook', 'test'),
(103, 'Impresora', 'test'),
(104, 'Telefono', 'Smartphone'),
(105, 'HUB', '');

--
-- Volcado de datos para la tabla `marca_tipo_equipo`
--

INSERT INTO `marca_tipo_equipo` (`idMarca_Equipo`, `idTipo_equipo`) VALUES
(105, 101),
(101, 102),
(103, 103),
(102, 104),
(104, 105);

--
-- Volcado de datos para la tabla `tipo_adquisicion`
--

INSERT INTO `tipo_adquisicion` (`idTipo_adquisicion`, `nombreTipo_adquisicion`) VALUES
(1, 'contrato de arriendo'),
(2, 'compra'),
(3, 'forzado'),
(4, 'sin adquisicion');

--
-- Volcado de datos para la tabla `modelo_equipo`
--

INSERT INTO `modelo_equipo` (`idModelo_Equipo`, `nombreModeloequipo`, `idTipo_Equipo`, `idMarca_Equipo`) VALUES
(301, 'Tuf Gamming', 101, 102),
(302, 'todo en uno', 105, 101),
(303, 'Galaxy S24', 102, 104);

--
-- Volcado de datos para la tabla `proveedor`
--

INSERT INTO `proveedor` (`idProveedor`, `nombreProveedor`) VALUES
(1, 'Sonda'),
(2, 'TechnoSystem'),
(3, 'forzado'),
(4, 'sin proveedor');

--
-- Volcado de datos para la tabla `orden_compra`
--

INSERT INTO `orden_compra` (`idOrden_compra`, `nombreOrden_compra`, `fechacompraOrden_compra`, `fechafin_ORDEN_COMPRA`, `rutadocumentoOrden_compra`, `idTipo_adquisicion`, `idProveedor`) VALUES
('1', 'forzado', '0000-00-00', '2024-06-21', NULL, 1, 1),
('2342342', '3412412', '0000-00-00', '0000-00-00', NULL, 2, 1),
('599-193-CC22', 'contrato 1592', '2021-11-11', '2022-11-11', NULL, 1, 1),
('599-405-CC22', 'contrato 2645', '2023-11-11', '2025-10-10', NULL, 2, 1);


COMMIT;
