--
-- Estructura para agregar Orden_compra y cleculares con su equipo de Celulares_Biobio.xlsx
-- 
--

INSERT INTO `tipo_equipo` (`idTipo_equipo`, `nombreTipo_equipo`) VALUES
(8, 'CELULAR');

INSERT INTO `marca_tipo_equipo` (`idMarcaTipo`,`idMarca_Equipo`, `idTipo_equipo`) VALUES 
(18, 2, 8);

INSERT INTO `modelo_equipo` (`nombreModeloequipo`, `idMarca_Tipo_Equipo`) VALUES
('Galaxy A05', 18);

INSERT INTO `orden_compra` (`idOrden_compra`,`nombreOrden_compra`,`fechacompraOrden_compra`,`fechafin_ORDEN_COMPRA`,`rutadocumentoOrden_compra`,`idTipo_adquisicion`,`idProveedor`
) VALUES
('599-527-SE24', 'falta definir nombre  ', 'falta definir fechacompra', 'falta definir fechafin', null, 2, 3);
