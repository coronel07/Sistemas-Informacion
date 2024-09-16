-- Active: 1725405326528@@127.0.0.1@3306
-- Crear la base de datos
CREATE DATABASE sistema_usuarios;

-- Seleccionar la base de datos
USE sistema_usuarios;

-- Crear la tabla de usuarios
CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,   -- ID único para cada usuario
    nombre_usuario VARCHAR(50) NOT NULL, -- Nombre de usuario único
    correo VARCHAR(100) NOT NULL UNIQUE, -- Correo electrónico único
    contraseña VARCHAR(255) NOT NULL,    -- Contraseña encriptada
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Fecha de registro
    ultimo_acceso TIMESTAMP NULL         -- Fecha del último acceso
);

-- Crear la tabla de roles (opcional si manejas roles como admin, user, etc.)
CREATE TABLE rol (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL
);

-- Crear una tabla para enlazar usuarios con roles
CREATE TABLE usuario_rol (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    rol_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id),
    FOREIGN KEY (rol_id) REFERENCES rol(id)
);

-- Insertar roles por defecto (opcional)
INSERT INTO rol (nombre_rol) VALUES ('usuario'), ('admin');
