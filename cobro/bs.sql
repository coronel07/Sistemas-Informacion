CREATE DATABASE pagoCobro;

USE pagoCobro;

CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_apellido VARCHAR(250) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    codigo_postal INT,
    contraseña_usuario VARCHAR(60) NOT NULL,
    telefono INT
);

CREATE TABLE roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    tipo_rol VARCHAR(50) NOT NULL,
    id_usuario INT,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

CREATE TABLE carrito (
    id_carrito INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    status_carrito VARCHAR(50),
    metodo_pago VARCHAR(50),
    fecha_pago DATE,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

CREATE TABLE producto (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    precio DECIMAL(10, 2) NOT NULL,
    descripcion TEXT,
    cantidad_producto INT NOT NULL,
    id_carrito INT,
    FOREIGN KEY (id_carrito) REFERENCES carrito(id_carrito)
);

--no usar esto nunca 
DROP DATABASE pagoCobro;
