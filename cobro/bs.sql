CREATE DATABASE pagoCobro;

USE pagoCobro;

CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    contraseña_usuario VARCHAR(60) NOT NULL
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


-- Agregar clave foránea a la tabla Carrito para relacionarla con Usuario
ALTER TABLE carrito
ADD CONSTRAINT fk_carrito_usuario
FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario);

-- Agregar clave foránea a la tabla Producto para relacionarla con Carrito
ALTER TABLE producto
ADD CONSTRAINT fk_producto_carrito
FOREIGN KEY (id_carrito) REFERENCES carrito(id_carrito);

ALTER TABLE producto
ADD COLUMN nombre_producto VARCHAR(100),
ADD COLUMN imagen_producto VARCHAR(255);

INSERT INTO producto (precio, descripcion, cantidad_producto, id_carrito, nombre_producto, imagen_producto) VALUES
(59.99, 'Camiseta oficial de fútbol', 50, NULL, 'Camiseta de Fútbol', 'https://www.futbolfactory.es/blog/wp-content/uploads/2019/06/nuevas-camisetas-futbol-temporada-19-20-01.jpg'), 
(29.99, 'Balón de fútbol profesional', 100, NULL, 'Balón de Fútbol', 'https://images-na.ssl-images-amazon.com/images/I/81r89VZeTSL._AC_SL1500_.jpg'),
(69.99, 'Botines de fútbol', 40, NULL, 'Botines de Fútbol', 'https://media.liverpool.com.mx/media/catalog/product/cache/18/image/600x/040ec09b1e35df139433887a97daa66f/s/i/silueta-84666402_6.jpg'),
(24.99, 'Guantes de arquero', 75, NULL, 'Guantes de Arquero', 'https://www.mundodeportivo.com/r/GODO/MD/p7/ContraPortada/Imagenes/2020/04/17/Recortada/img_psola_20200417-123947_imagenes_md_colaboradores_psola_guantes-web-kRHH-U484813964818Af-980x554@MundoDeportivo-Web.jpg'),
(15.99, 'Canilleras de protección', 120, NULL, 'Canilleras', 'https://m.media-amazon.com/images/I/81Kw-K-BLwL._AC_SL1500_.jpg')