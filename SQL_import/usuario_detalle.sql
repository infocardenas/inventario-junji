CREATE TABLE `detalle_usuario` (
  `nombreUsuario` varchar(250) NOT NULL,
  `rut` varchar(20) DEFAULT NULL,
  `cargo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`nombreUsuario`),
  CONSTRAINT `fk_detalle_usuario_usuario` FOREIGN KEY (`nombreUsuario`) REFERENCES `usuario` (`nombreUsuario`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;