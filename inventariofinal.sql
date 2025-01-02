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

-- --------------------------------------------------------

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
  `fechaDevolucion` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `asignacion`
--

INSERT INTO `asignacion` (`idAsignacion`, `fecha_inicioAsignacion`, `ObservacionAsignacion`, `rutaactaAsignacion`, `ActivoAsignacion`, `rutFuncionario`, `idDevolucion`, `fechaDevolucion`) VALUES
(146, '2024-06-25', 'set', 'ruta', 0, '1-1', NULL, '2024-06-25'),
(147, '0000-00-00', 'set', 'ruta', 0, '1-1', NULL, '2024-06-25');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `comuna`
--

CREATE TABLE `comuna` (
  `idComuna` int(11) NOT NULL,
  `nombreComuna` varchar(45) DEFAULT NULL,
  `idProvincia` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
(33, 'Yumbel', 3),
(34, 'Concepcion', 1),
(35, 'Coronel', 1),
(36, 'Chiguayante', 1),
(37, 'Florida', 1),
(38, 'Hualqui', 1),
(39, 'Lota', 1),
(40, 'Penco', 1),
(41, 'San Pedro de la Paz', 1),
(42, 'Santa Juana', 1),
(43, 'Talcahuano', 1),
(44, 'Tome', 1),
(45, 'Hualpen', 1),
(46, 'Concepcion', 1),
(47, 'Coronel', 1),
(48, 'Chiguayante', 1),
(49, 'Florida', 1),
(50, 'Hualqui', 1),
(51, 'Lota', 1),
(52, 'Penco', 1),
(53, 'San Pedro de la Paz', 1),
(54, 'Santa Juana', 1),
(55, 'Talcahuano', 1),
(56, 'Tome', 1),
(57, 'Hualpen', 1),
(58, 'Concepcion', 1),
(59, 'Coronel', 1),
(60, 'Chiguayante', 1),
(61, 'Florida', 1),
(62, 'Hualqui', 1),
(63, 'Lota', 1),
(64, 'Penco', 1),
(65, 'San Pedro de la Paz', 1),
(66, 'Santa Juana', 1),
(67, 'Talcahuano', 1),
(68, 'Tome', 1),
(69, 'Hualpen', 1),
(70, 'Lebu', 2),
(71, 'Arauco', 2),
(72, 'Cañete', 2),
(73, 'Contulmo', 2),
(74, 'Curanilahue', 2),
(75, 'Los Álamos', 2),
(76, 'Tirúa', 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_traslado`
--

CREATE TABLE `detalle_traslado` (
  `idDetalle_traslado` int(11) NOT NULL,
  `observacionDetalletraslado` varchar(45) DEFAULT NULL,
  `idTraslado` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `devolucion`
--

CREATE TABLE `devolucion` (
  `idDevolucion` int(11) NOT NULL,
  `fechaDevolucion` date DEFAULT NULL,
  `observacionDevolucion` varchar(250) DEFAULT NULL,
  `rutaactaDevolucion` varchar(45) DEFAULT NULL,
  `ActivoDevolucion` tinyint(4) DEFAULT NULL,
  `rutFuncionario` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `equipo`
--

CREATE TABLE `equipo` (
  `idEquipo` int(11) NOT NULL,
  `Cod_inventarioEquipo` varchar(20) DEFAULT NULL,
  `Num_serieEquipo` varchar(20) DEFAULT NULL,
  `ObservacionEquipo` varchar(250) DEFAULT NULL,
  `codigoproveedor_equipo` varchar(45) DEFAULT NULL,
  `macEquipo` varchar(45) DEFAULT NULL,
  `imeiEquipo` varchar(45) DEFAULT NULL,
  `numerotelefonicoEquipo` varchar(12) DEFAULT NULL,
  `idEstado_equipo` int(11) NOT NULL,
  `idUnidad` int(11) NOT NULL,
  `idOrden_compra` varchar(45) NOT NULL,
  `idModelo_equipo` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `equipo`
--

INSERT INTO `equipo` (`idEquipo`, `Cod_inventarioEquipo`, `Num_serieEquipo`, `ObservacionEquipo`, `codigoproveedor_equipo`, `macEquipo`, `imeiEquipo`, `numerotelefonicoEquipo`, `idEstado_equipo`, `idUnidad`, `idOrden_compra`, `idModelo_equipo`) VALUES
(71, 'qqwer', 'qwer', 'qwer', 'qwer', '', '', '', 4, 1, '1', 364),
(72, 'werg', 'wadf', '234', '1234', '123', '', '5432', 3, 13221421, 'desconocido', 365),
(73, '12324', '2345234', NULL, '2345234', NULL, NULL, NULL, 3, 8301033, '2342342', 366),
(74, '3434', 'Serie_123', NULL, '56362', NULL, NULL, NULL, 3, 1, '1', 366);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `equipo_asignacion`
--

CREATE TABLE `equipo_asignacion` (
  `idAsignacion` int(11) NOT NULL,
  `idEquipo` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `equipo_asignacion`
--

INSERT INTO `equipo_asignacion` (`idAsignacion`, `idEquipo`) VALUES
(146, 71),
(146, 72),
(147, 71);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estado_equipo`
--

CREATE TABLE `estado_equipo` (
  `idEstado_equipo` int(11) NOT NULL,
  `nombreEstado_equipo` varchar(45) DEFAULT NULL,
  `FechaEstado_equipo` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `estado_equipo`
--

INSERT INTO `estado_equipo` (`idEstado_equipo`, `nombreEstado_equipo`, `FechaEstado_equipo`) VALUES
(1, 'BAJA', '2024-02-05'),
(2, 'EN USO', '2024-02-05'),
(3, 'SIN ASIGNAR', '2024-02-05'),
(4, 'SINIESTRO', '2024-02-05');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `funcionario`
--

CREATE TABLE `funcionario` (
  `rutFuncionario` varchar(20) NOT NULL,
  `nombreFuncionario` varchar(45) NOT NULL,
  `cargoFuncionario` varchar(45) DEFAULT NULL,
  `idUnidad` int(11) DEFAULT NULL,
  `correoFuncionario` varchar(45) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `funcionario`
--

INSERT INTO `funcionario` (`rutFuncionario`, `nombreFuncionario`, `cargoFuncionario`, `idUnidad`, `correoFuncionario`) VALUES
('1-1', 'ElFuncionario', 'funcionario', 8203001, 'fun@dominio.cl'),
('10222333k', 'Leticia Letelier', 'Encargada', 8015892, NULL),
('15222111k', 'Valentina Salgado', 'Encargada', 8203001, NULL),
('180003339', 'Natalie Ramirez', 'Encargada', 8203001, NULL),
('190001110', 'Cristina Dominguez', 'Encargada', 8301033, NULL),
('20941502-', 'martin', '123', 8301033, NULL),
('20941502-k', 'martin2', 'cargo', 8015892, NULL),
('21000222k', 'Romina Gonzales', 'Encargada', 8015892, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `incidencia`
--

CREATE TABLE `incidencia` (
  `idIncidencia` int(11) NOT NULL,
  `nombreIncidencia` varchar(45) DEFAULT NULL,
  `observacionIncidencia` varchar(45) DEFAULT NULL,
  `rutaactaIncidencia` varchar(45) DEFAULT NULL,
  `fechaIncidencia` date DEFAULT NULL,
  `idEquipo` int(11) NOT NULL,
  `numDocumentos` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `incidencia`
--

INSERT INTO `incidencia` (`idIncidencia`, `nombreIncidencia`, `observacionIncidencia`, `rutaactaIncidencia`, `fechaIncidencia`, `idEquipo`, `numDocumentos`) VALUES
(41, 'asdf', 'asfd', 'ruta', '2024-06-28', 72, 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `marca_equipo`
--

CREATE TABLE `marca_equipo` (
  `idMarca_Equipo` int(11) NOT NULL,
  `nombreMarcaEquipo` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `marca_equipo`
--

INSERT INTO `marca_equipo` (`idMarca_Equipo`, `nombreMarcaEquipo`) VALUES
(129, '123Z'),
(130, '13241234'),
(128, 'Epson'),
(127, 'HP'),
(126, 'Lenovo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `marca_tipo_equipo`
--

CREATE TABLE `marca_tipo_equipo` (
  `idMarca_Equipo` int(11) NOT NULL,
  `idTipo_equipo` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `marca_tipo_equipo`
--

INSERT INTO `marca_tipo_equipo` (`idMarca_Equipo`, `idTipo_equipo`) VALUES
(126, 172),
(126, 176),
(126, 185),
(127, 172),
(127, 184),
(127, 186),
(128, 172),
(128, 177),
(129, 181),
(129, 182);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `modalidad`
--

CREATE TABLE `modalidad` (
  `idModalidad` int(11) NOT NULL,
  `nombreModalidad` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `modalidad`
--

INSERT INTO `modalidad` (`idModalidad`, `nombreModalidad`) VALUES
(1, 'CLASICO'),
(2, 'ALTERNATIVO'),
(3, 'OFICINA');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `modelo_equipo`
--

CREATE TABLE `modelo_equipo` (
  `idModelo_Equipo` int(11) NOT NULL,
  `nombreModeloequipo` varchar(45) DEFAULT NULL,
  `idTipo_Equipo` int(11) DEFAULT NULL,
  `idMarca_Equipo` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `modelo_equipo`
--

INSERT INTO `modelo_equipo` (`idModelo_Equipo`, `nombreModeloequipo`, `idTipo_Equipo`, `idMarca_Equipo`) VALUES
(339, '325_notebook', 181, 129),
(340, 'todo en uno1', 172, 127),
(358, '2345', 176, 126),
(363, '3465', 176, 126),
(364, '123M', 181, 129),
(365, 'p2000', 182, 129),
(366, '12342134', 184, 130);

-- --------------------------------------------------------

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
  `idProveedor` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `orden_compra`
--

INSERT INTO `orden_compra` (`idOrden_compra`, `nombreOrden_compra`, `fechacompraOrden_compra`, `fechafin_ORDEN_COMPRA`, `rutadocumentoOrden_compra`, `idTipo_adquisicion`, `idProveedor`) VALUES
('1', 'forzado', '0000-00-00', '2024-06-21', NULL, 18, 12),
('2342342', '3412412', '0000-00-00', '0000-00-00', NULL, 20, 14),
('599-193-CC22', 'contrato 1592', '2021-11-11', '2022-11-11', NULL, 1, 1),
('599-405-CC22', 'contrato 2645', '2023-11-11', '2025-10-10', NULL, 2, 1),
('desconocido', 'sin nombre', '2024-06-10', '2024-06-10', '', 19, 13);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proveedor`
--

CREATE TABLE `proveedor` (
  `idProveedor` int(11) NOT NULL,
  `nombreProveedor` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `proveedor`
--

INSERT INTO `proveedor` (`idProveedor`, `nombreProveedor`) VALUES
(1, 'Sonda'),
(2, 'TechnoSystem'),
(3, 'Sonda'),
(4, 'TechnoSystem'),
(5, 'Sonda'),
(6, 'TechnoSystem'),
(7, 'Sonda'),
(8, 'TechnoSystem'),
(9, 'Sonda'),
(10, 'TechnoSystem'),
(12, 'forzado'),
(13, 'sin proveedor'),
(14, '2345234');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `provincia`
--

CREATE TABLE `provincia` (
  `idProvincia` int(11) NOT NULL,
  `nombreProvincia` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `provincia`
--

INSERT INTO `provincia` (`idProvincia`, `nombreProvincia`) VALUES
(1, 'Concepcion'),
(2, 'Arauco'),
(3, 'Biobío'),
(4, 'Concepcion'),
(5, 'Arauco'),
(6, 'Biobío'),
(7, 'Concepcion'),
(8, 'Arauco'),
(9, 'Biobío'),
(10, 'Concepcion'),
(11, 'Arauco'),
(12, 'Biobío'),
(13, 'Concepcion'),
(14, 'Arauco'),
(15, 'Biobío'),
(16, 'Concepcion'),
(17, 'Arauco'),
(18, 'Biobío'),
(19, 'Concepcion'),
(20, 'Arauco'),
(21, 'Biobío'),
(22, 'Concepcion'),
(23, 'Arauco'),
(24, 'Biobío');

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `super_equipo`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `super_equipo` (
`idEquipo` int(11)
,`Cod_inventarioEquipo` varchar(20)
,`Num_serieEquipo` varchar(20)
,`ObservacionEquipo` varchar(250)
,`codigoproveedor_equipo` varchar(45)
,`macEquipo` varchar(45)
,`imeiEquipo` varchar(45)
,`numerotelefonicoEquipo` varchar(12)
,`idTipo_equipo` int(11)
,`nombreTipo_equipo` varchar(45)
,`idEstado_equipo` int(11)
,`nombreEstado_equipo` varchar(45)
,`idUnidad` int(11)
,`nombreUnidad` varchar(45)
,`idOrden_compra` varchar(45)
,`nombreOrden_compra` varchar(45)
,`idModelo_equipo` int(11)
,`nombreModeloequipo` varchar(45)
,`nombreFuncionario` varchar(45)
,`rutFuncionario` varchar(20)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_adquisicion`
--

CREATE TABLE `tipo_adquisicion` (
  `idTipo_adquisicion` int(11) NOT NULL,
  `nombreTipo_adquisicion` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tipo_adquisicion`
--

INSERT INTO `tipo_adquisicion` (`idTipo_adquisicion`, `nombreTipo_adquisicion`) VALUES
(1, 'contrato de arriendo'),
(2, 'compra'),
(3, 'contrato de arriendo'),
(4, 'compra'),
(5, 'contrato de arriendo'),
(6, 'compra'),
(7, 'contrato de arriendo'),
(8, 'compra'),
(9, 'contrato de arriendo'),
(10, 'compra'),
(11, 'contrato de arriendo'),
(12, 'compra'),
(13, 'contrato de arriendo'),
(14, 'compra'),
(15, 'contrato de arriendo'),
(16, 'compra'),
(18, 'forzado'),
(19, 'sin adquisicion'),
(20, '453452');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipo_equipo`
--

CREATE TABLE `tipo_equipo` (
  `idTipo_equipo` int(11) NOT NULL,
  `nombreTipo_equipo` varchar(45) DEFAULT NULL,
  `observacionTipoEquipo` varchar(60) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tipo_equipo`
--

INSERT INTO `tipo_equipo` (`idTipo_equipo`, `nombreTipo_equipo`, `observacionTipoEquipo`) VALUES
(172, 'AIO', 'test'),
(176, 'Notebook', 'test'),
(177, 'Impresora', 'test'),
(181, '123X', NULL),
(182, 'Telefono', ''),
(184, '12341234', NULL),
(185, 'HUB', ''),
(186, 'Tecla', '');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `traslacion`
--

CREATE TABLE `traslacion` (
  `idTraslado` int(11) NOT NULL,
  `idEquipo` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `traslacion`
--

INSERT INTO `traslacion` (`idTraslado`, `idEquipo`) VALUES
(300, 72),
(301, 73),
(302, 74),
(303, 73),
(304, 73),
(305, 73),
(311, 72);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `traslado`
--

CREATE TABLE `traslado` (
  `idTraslado` int(11) NOT NULL,
  `fechatraslado` date DEFAULT NULL,
  `rutadocumentoTraslado` varchar(50) DEFAULT NULL,
  `idUnidadDestino` int(11) NOT NULL,
  `idUnidadOrigen` int(11) DEFAULT NULL,
  `estaFirmadoTraslado` tinyint(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `traslado`
--

INSERT INTO `traslado` (`idTraslado`, `fechatraslado`, `rutadocumentoTraslado`, `idUnidadDestino`, `idUnidadOrigen`, `estaFirmadoTraslado`) VALUES
(1, '2024-03-01', NULL, 8203001, NULL, NULL),
(2, '2022-12-28', NULL, 8203001, NULL, NULL),
(3, '2024-01-03', NULL, 8203001, NULL, NULL),
(4, '2020-10-30', NULL, 8203001, NULL, NULL),
(5, '2022-02-14', NULL, 8203001, NULL, NULL),
(6, '2024-01-02', NULL, 8203001, NULL, NULL),
(7, '2023-11-30', NULL, 8301033, NULL, NULL),
(8, '2022-11-11', NULL, 8301033, NULL, NULL),
(9, '2021-04-25', NULL, 8301033, NULL, NULL),
(10, '2021-10-15', NULL, 8301033, NULL, NULL),
(11, '2024-07-05', NULL, 8301033, NULL, NULL),
(12, '2021-07-07', NULL, 8301033, NULL, NULL),
(300, '2024-07-22', 'ruta', 8203001, 1, NULL),
(301, '2024-07-02', 'ruta', 8203001, 1, NULL),
(302, '2024-07-29', 'ruta', 1, 1, NULL),
(303, '2024-07-31', 'ruta', 8205012, 8203001, NULL),
(304, '2024-07-31', 'ruta', 8301033, 8203001, NULL),
(305, '2024-07-31', 'ruta', 8301033, 8203001, NULL),
(306, '2024-07-31', 'ruta', 2, 8301033, NULL),
(307, '2024-07-29', 'ruta', 2, 8301033, NULL),
(308, '2024-07-29', 'ruta', 1, 8301033, NULL),
(309, '2024-07-29', 'ruta', 13221421, 8301033, NULL),
(310, '2024-07-29', 'ruta', 13221421, 8301033, NULL),
(311, '2024-07-30', 'ruta', 13221421, 8203001, NULL),
(312, '2024-07-30', 'ruta', 8205012, 8301033, NULL),
(314, '2024-07-30', 'ruta', 13221421, 8301033, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `unidad`
--

CREATE TABLE `unidad` (
  `idUnidad` int(11) NOT NULL,
  `nombreUnidad` varchar(45) DEFAULT NULL,
  `contactoUnidad` varchar(45) DEFAULT NULL,
  `direccionUnidad` varchar(45) CHARACTER SET armscii8 COLLATE armscii8_general_ci DEFAULT NULL,
  `idComuna` int(11) NOT NULL,
  `idModalidad` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `unidad`
--

INSERT INTO `unidad` (`idUnidad`, `nombreUnidad`, `contactoUnidad`, `direccionUnidad`, `idComuna`, `idModalidad`) VALUES
(1, 'u_de_excel', 'test', '123_calle_falsa', 1, 1),
(2, 'u_de_excel2', 'test', '123_calle_falsa', 8, 1),
(3, 'u_de_excel2', 'test', '123_calle_falsa', 2, 1),
(4, 'u_de_excel2', NULL, '123_calle_falsa', 2, 1),
(8015892, 'BALDOMERO LILLO', 'CECILIA  JEREZ NEIRA', 'Evaristo  Az?car 62, Fundici?n Lota', 2, 3),
(8203001, 'ABKELAY KIMUN', '982286157', 'Km.10 Sector De Primer Agua Tirua', 1, 1),
(8205012, 'ACHNU CAÑETE', '88277769', 'Manuel Rodriguez N? 150', 15, NULL),
(8301033, 'VILLA GENESIS', '91774260', 'Avda. Neltume S/N? Villa Genesis', 20, NULL),
(8301034, 'Nueva-Unidad', 'nuevo-contacto', 'camino amarillo', 9, NULL),
(8301035, 'conModalidad', 'conModalidad', 'comModalidad', 2, 2),
(8301037, 'unidad_test_23', '123', '2123', 1, 1),
(13221421, 'Lokobox', 'Martin', 'Galvarino', 4, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `nombreUsuario` varchar(30) NOT NULL,
  `contrasennaUsuario` varchar(80) DEFAULT NULL,
  `privilegiosAdministrador` tinyint(4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`nombreUsuario`, `contrasennaUsuario`, `privilegiosAdministrador`) VALUES
('admin', '$2b$12$QUyjfHNIiGxsqPXjSKs38O7RCN2XfXfpzIxrzMNQw0VmBvF0J3cgG', 1),
('martin', '$2b$12$latvxc1R56a94bkyuJHVHe8fNMpVd247CYM78LtyzhKfqRrqTDYOa', 0),
('usuario_normal', '$2b$12$AIHWrdksjmF7AApn02/vRuC2qGMe8QcButv15WNZSxRkm8BqHLm3S', 0);

-- --------------------------------------------------------

--
-- Estructura para la vista `super_equipo`
--
DROP TABLE IF EXISTS `super_equipo`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `super_equipo`  AS SELECT `e`.`idEquipo` AS `idEquipo`, `e`.`Cod_inventarioEquipo` AS `Cod_inventarioEquipo`, `e`.`Num_serieEquipo` AS `Num_serieEquipo`, `e`.`ObservacionEquipo` AS `ObservacionEquipo`, `e`.`codigoproveedor_equipo` AS `codigoproveedor_equipo`, `e`.`macEquipo` AS `macEquipo`, `e`.`imeiEquipo` AS `imeiEquipo`, `e`.`numerotelefonicoEquipo` AS `numerotelefonicoEquipo`, `te`.`idTipo_equipo` AS `idTipo_equipo`, `te`.`nombreTipo_equipo` AS `nombreTipo_equipo`, `ee`.`idEstado_equipo` AS `idEstado_equipo`, `ee`.`nombreEstado_equipo` AS `nombreEstado_equipo`, `u`.`idUnidad` AS `idUnidad`, `u`.`nombreUnidad` AS `nombreUnidad`, `oc`.`idOrden_compra` AS `idOrden_compra`, `oc`.`nombreOrden_compra` AS `nombreOrden_compra`, `moe`.`idModelo_Equipo` AS `idModelo_equipo`, `moe`.`nombreModeloequipo` AS `nombreModeloequipo`, '' AS `nombreFuncionario`, '' AS `rutFuncionario` FROM (((((`equipo` `e` join `modelo_equipo` `moe` on(`moe`.`idModelo_Equipo` = `e`.`idModelo_equipo`)) left join `tipo_equipo` `te` on(`te`.`idTipo_equipo` = `moe`.`idTipo_Equipo`)) join `estado_equipo` `ee` on(`ee`.`idEstado_equipo` = `e`.`idEstado_equipo`)) join `unidad` `u` on(`u`.`idUnidad` = `e`.`idUnidad`)) join `orden_compra` `oc` on(`oc`.`idOrden_compra` = `e`.`idOrden_compra`)) WHERE `ee`.`nombreEstado_equipo` not like 'EN USO'union select `e`.`idEquipo` AS `idEquipo`,`e`.`Cod_inventarioEquipo` AS `Cod_inventarioEquipo`,`e`.`Num_serieEquipo` AS `Num_serieEquipo`,`e`.`ObservacionEquipo` AS `ObservacionEquipo`,`e`.`codigoproveedor_equipo` AS `codigoproveedor_equipo`,`e`.`macEquipo` AS `macEquipo`,`e`.`imeiEquipo` AS `imeiEquipo`,`e`.`numerotelefonicoEquipo` AS `numerotelefonicoEquipo`,`te`.`idTipo_equipo` AS `idTipo_equipo`,`te`.`nombreTipo_equipo` AS `nombreTipo_equipo`,`ee`.`idEstado_equipo` AS `idEstado_equipo`,`ee`.`nombreEstado_equipo` AS `nombreEstado_equipo`,`u`.`idUnidad` AS `idUnidad`,`u`.`nombreUnidad` AS `nombreUnidad`,`oc`.`idOrden_compra` AS `idOrden_compra`,`oc`.`nombreOrden_compra` AS `nombreOrden_compra`,`moe`.`idModelo_Equipo` AS `idModelo_equipo`,`moe`.`nombreModeloequipo` AS `nombreModeloequipo`,`f`.`nombreFuncionario` AS `nombreFuncionario`,`f`.`rutFuncionario` AS `rutFuncionario` from ((((((((`equipo` `e` join `modelo_equipo` `moe` on(`moe`.`idModelo_Equipo` = `e`.`idModelo_equipo`)) left join `tipo_equipo` `te` on(`te`.`idTipo_equipo` = `moe`.`idTipo_Equipo`)) join `unidad` `u` on(`u`.`idUnidad` = `e`.`idUnidad`)) join `orden_compra` `oc` on(`oc`.`idOrden_compra` = `e`.`idOrden_compra`)) join `equipo_asignacion` `ea` on(`ea`.`idEquipo` = `e`.`idEquipo`)) join `estado_equipo` `ee` on(`ee`.`idEstado_equipo` = `e`.`idEstado_equipo`)) join `asignacion` `a` on(`a`.`idAsignacion` = `ea`.`idAsignacion`)) join `funcionario` `f` on(`f`.`rutFuncionario` = `a`.`rutFuncionario`)) where `ee`.`nombreEstado_equipo` like 'EN USO' and `a`.`ActivoAsignacion` = 1  ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `asignacion`
--
ALTER TABLE `asignacion`
  ADD PRIMARY KEY (`idAsignacion`),
  ADD KEY `idDevolucion` (`idDevolucion`),
  ADD KEY `rutFuncionario` (`rutFuncionario`);

--
-- Indices de la tabla `comuna`
--
ALTER TABLE `comuna`
  ADD PRIMARY KEY (`idComuna`,`idProvincia`),
  ADD KEY `idProvincia` (`idProvincia`);

--
-- Indices de la tabla `detalle_traslado`
--
ALTER TABLE `detalle_traslado`
  ADD PRIMARY KEY (`idDetalle_traslado`),
  ADD KEY `idTraslado` (`idTraslado`);

--
-- Indices de la tabla `devolucion`
--
ALTER TABLE `devolucion`
  ADD PRIMARY KEY (`idDevolucion`),
  ADD KEY `rutFuncionario` (`rutFuncionario`);

--
-- Indices de la tabla `equipo`
--
ALTER TABLE `equipo`
  ADD PRIMARY KEY (`idEquipo`),
  ADD UNIQUE KEY `Num_serieEquipo` (`Num_serieEquipo`),
  ADD KEY `idEstado_equipo` (`idEstado_equipo`),
  ADD KEY `idUnidad` (`idUnidad`),
  ADD KEY `idOrden_compra` (`idOrden_compra`),
  ADD KEY `idModelo_equipo` (`idModelo_equipo`);

--
-- Indices de la tabla `equipo_asignacion`
--
ALTER TABLE `equipo_asignacion`
  ADD PRIMARY KEY (`idAsignacion`,`idEquipo`),
  ADD KEY `idEquipo` (`idEquipo`);

--
-- Indices de la tabla `estado_equipo`
--
ALTER TABLE `estado_equipo`
  ADD PRIMARY KEY (`idEstado_equipo`);

--
-- Indices de la tabla `funcionario`
--
ALTER TABLE `funcionario`
  ADD PRIMARY KEY (`rutFuncionario`),
  ADD UNIQUE KEY `rutFuncionario` (`rutFuncionario`),
  ADD KEY `idUnidad` (`idUnidad`);

--
-- Indices de la tabla `incidencia`
--
ALTER TABLE `incidencia`
  ADD PRIMARY KEY (`idIncidencia`),
  ADD KEY `idEquipo` (`idEquipo`);

--
-- Indices de la tabla `marca_equipo`
--
ALTER TABLE `marca_equipo`
  ADD PRIMARY KEY (`idMarca_Equipo`),
  ADD UNIQUE KEY `nombreMarcaEquipo` (`nombreMarcaEquipo`);

--
-- Indices de la tabla `marca_tipo_equipo`
--
ALTER TABLE `marca_tipo_equipo`
  ADD PRIMARY KEY (`idMarca_Equipo`,`idTipo_equipo`),
  ADD KEY `idTipo_equipo` (`idTipo_equipo`);

--
-- Indices de la tabla `modalidad`
--
ALTER TABLE `modalidad`
  ADD PRIMARY KEY (`idModalidad`);

--
-- Indices de la tabla `modelo_equipo`
--
ALTER TABLE `modelo_equipo`
  ADD PRIMARY KEY (`idModelo_Equipo`),
  ADD UNIQUE KEY `nombreModeloequipo` (`nombreModeloequipo`),
  ADD KEY `idTipo_Equipo` (`idTipo_Equipo`),
  ADD KEY `idMarca_Equipo` (`idMarca_Equipo`);

--
-- Indices de la tabla `orden_compra`
--
ALTER TABLE `orden_compra`
  ADD PRIMARY KEY (`idOrden_compra`),
  ADD KEY `idTipo_adquisicion` (`idTipo_adquisicion`),
  ADD KEY `idProveedor` (`idProveedor`);

--
-- Indices de la tabla `proveedor`
--
ALTER TABLE `proveedor`
  ADD PRIMARY KEY (`idProveedor`);

--
-- Indices de la tabla `provincia`
--
ALTER TABLE `provincia`
  ADD PRIMARY KEY (`idProvincia`);

--
-- Indices de la tabla `tipo_adquisicion`
--
ALTER TABLE `tipo_adquisicion`
  ADD PRIMARY KEY (`idTipo_adquisicion`);

--
-- Indices de la tabla `tipo_equipo`
--
ALTER TABLE `tipo_equipo`
  ADD PRIMARY KEY (`idTipo_equipo`),
  ADD UNIQUE KEY `nombreTipo_equipo` (`nombreTipo_equipo`);

--
-- Indices de la tabla `traslacion`
--
ALTER TABLE `traslacion`
  ADD PRIMARY KEY (`idTraslado`,`idEquipo`),
  ADD KEY `idEquipo` (`idEquipo`);

--
-- Indices de la tabla `traslado`
--
ALTER TABLE `traslado`
  ADD PRIMARY KEY (`idTraslado`),
  ADD KEY `idUnidad` (`idUnidadDestino`),
  ADD KEY `fk_idUnidadOrigen` (`idUnidadOrigen`);

--
-- Indices de la tabla `unidad`
--
ALTER TABLE `unidad`
  ADD PRIMARY KEY (`idUnidad`),
  ADD KEY `idComuna` (`idComuna`),
  ADD KEY `idModalidad` (`idModalidad`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`nombreUsuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `asignacion`
--
ALTER TABLE `asignacion`
  MODIFY `idAsignacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=148;

--
-- AUTO_INCREMENT de la tabla `comuna`
--
ALTER TABLE `comuna`
  MODIFY `idComuna` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=80;

--
-- AUTO_INCREMENT de la tabla `detalle_traslado`
--
ALTER TABLE `detalle_traslado`
  MODIFY `idDetalle_traslado` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `devolucion`
--
ALTER TABLE `devolucion`
  MODIFY `idDevolucion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `equipo`
--
ALTER TABLE `equipo`
  MODIFY `idEquipo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=76;

--
-- AUTO_INCREMENT de la tabla `estado_equipo`
--
ALTER TABLE `estado_equipo`
  MODIFY `idEstado_equipo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- AUTO_INCREMENT de la tabla `incidencia`
--
ALTER TABLE `incidencia`
  MODIFY `idIncidencia` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=42;

--
-- AUTO_INCREMENT de la tabla `marca_equipo`
--
ALTER TABLE `marca_equipo`
  MODIFY `idMarca_Equipo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=131;

--
-- AUTO_INCREMENT de la tabla `modalidad`
--
ALTER TABLE `modalidad`
  MODIFY `idModalidad` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `modelo_equipo`
--
ALTER TABLE `modelo_equipo`
  MODIFY `idModelo_Equipo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=367;

--
-- AUTO_INCREMENT de la tabla `proveedor`
--
ALTER TABLE `proveedor`
  MODIFY `idProveedor` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT de la tabla `provincia`
--
ALTER TABLE `provincia`
  MODIFY `idProvincia` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT de la tabla `tipo_adquisicion`
--
ALTER TABLE `tipo_adquisicion`
  MODIFY `idTipo_adquisicion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT de la tabla `tipo_equipo`
--
ALTER TABLE `tipo_equipo`
  MODIFY `idTipo_equipo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=187;

--
-- AUTO_INCREMENT de la tabla `traslado`
--
ALTER TABLE `traslado`
  MODIFY `idTraslado` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=315;

--
-- AUTO_INCREMENT de la tabla `unidad`
--
ALTER TABLE `unidad`
  MODIFY `idUnidad` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13221422;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `asignacion`
--
ALTER TABLE `asignacion`
  ADD CONSTRAINT `asignacion_ibfk_3` FOREIGN KEY (`idDevolucion`) REFERENCES `devolucion` (`idDevolucion`),
  ADD CONSTRAINT `rutFuncionario` FOREIGN KEY (`rutFuncionario`) REFERENCES `funcionario` (`rutFuncionario`);

--
-- Filtros para la tabla `comuna`
--
ALTER TABLE `comuna`
  ADD CONSTRAINT `comuna_ibfk_1` FOREIGN KEY (`idProvincia`) REFERENCES `provincia` (`idProvincia`);

--
-- Filtros para la tabla `detalle_traslado`
--
ALTER TABLE `detalle_traslado`
  ADD CONSTRAINT `detalle_traslado_ibfk_1` FOREIGN KEY (`idTraslado`) REFERENCES `traslado` (`idTraslado`);

--
-- Filtros para la tabla `equipo`
--
ALTER TABLE `equipo`
  ADD CONSTRAINT `equipo_ibfk_2` FOREIGN KEY (`idEstado_equipo`) REFERENCES `estado_equipo` (`idEstado_equipo`),
  ADD CONSTRAINT `equipo_ibfk_3` FOREIGN KEY (`idUnidad`) REFERENCES `unidad` (`idUnidad`),
  ADD CONSTRAINT `equipo_ibfk_4` FOREIGN KEY (`idOrden_compra`) REFERENCES `orden_compra` (`idOrden_compra`),
  ADD CONSTRAINT `equipo_ibfk_5` FOREIGN KEY (`idModelo_equipo`) REFERENCES `modelo_equipo` (`idModelo_Equipo`);

--
-- Filtros para la tabla `equipo_asignacion`
--
ALTER TABLE `equipo_asignacion`
  ADD CONSTRAINT `equipo_asignacion_ibfk_1` FOREIGN KEY (`idAsignacion`) REFERENCES `asignacion` (`idAsignacion`),
  ADD CONSTRAINT `equipo_asignacion_ibfk_2` FOREIGN KEY (`idEquipo`) REFERENCES `equipo` (`idEquipo`);

--
-- Filtros para la tabla `funcionario`
--
ALTER TABLE `funcionario`
  ADD CONSTRAINT `funcionario_ibfk_1` FOREIGN KEY (`idUnidad`) REFERENCES `unidad` (`idUnidad`);

--
-- Filtros para la tabla `incidencia`
--
ALTER TABLE `incidencia`
  ADD CONSTRAINT `incidencia_ibfk_1` FOREIGN KEY (`idEquipo`) REFERENCES `equipo` (`idEquipo`);

--
-- Filtros para la tabla `marca_tipo_equipo`
--
ALTER TABLE `marca_tipo_equipo`
  ADD CONSTRAINT `marca_tipo_equipo_ibfk_1` FOREIGN KEY (`idMarca_Equipo`) REFERENCES `marca_equipo` (`idMarca_Equipo`),
  ADD CONSTRAINT `marca_tipo_equipo_ibfk_2` FOREIGN KEY (`idTipo_equipo`) REFERENCES `tipo_equipo` (`idTipo_equipo`);

--
-- Filtros para la tabla `modelo_equipo`
--
ALTER TABLE `modelo_equipo`
  ADD CONSTRAINT `modelo_equipo_ibfk_1` FOREIGN KEY (`idTipo_Equipo`) REFERENCES `tipo_equipo` (`idTipo_equipo`),
  ADD CONSTRAINT `modelo_equipo_ibfk_2` FOREIGN KEY (`idMarca_Equipo`) REFERENCES `marca_equipo` (`idMarca_Equipo`);

--
-- Filtros para la tabla `orden_compra`
--
ALTER TABLE `orden_compra`
  ADD CONSTRAINT `orden_compra_ibfk_1` FOREIGN KEY (`idTipo_adquisicion`) REFERENCES `tipo_adquisicion` (`idTipo_adquisicion`),
  ADD CONSTRAINT `orden_compra_ibfk_2` FOREIGN KEY (`idProveedor`) REFERENCES `proveedor` (`idProveedor`);

--
-- Filtros para la tabla `traslacion`
--
ALTER TABLE `traslacion`
  ADD CONSTRAINT `traslacion_ibfk_1` FOREIGN KEY (`idTraslado`) REFERENCES `traslado` (`idTraslado`),
  ADD CONSTRAINT `traslacion_ibfk_2` FOREIGN KEY (`idEquipo`) REFERENCES `equipo` (`idEquipo`);

--
-- Filtros para la tabla `traslado`
--
ALTER TABLE `traslado`
  ADD CONSTRAINT `fk_idUnidadOrigen` FOREIGN KEY (`idUnidadOrigen`) REFERENCES `unidad` (`idUnidad`),
  ADD CONSTRAINT `traslado_ibfk_1` FOREIGN KEY (`idUnidadDestino`) REFERENCES `unidad` (`idUnidad`);

--
-- Filtros para la tabla `unidad`
--
ALTER TABLE `unidad`
  ADD CONSTRAINT `unidad_ibfk_1` FOREIGN KEY (`idComuna`) REFERENCES `comuna` (`idComuna`),
  ADD CONSTRAINT `unidad_ibfk_2` FOREIGN KEY (`idModalidad`) REFERENCES `modalidad` (`idModalidad`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
