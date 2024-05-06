import time

class Nodo:
    def __init__(self, nombre):
        self.nombre = nombre
        self.conexiones = []

    def agregar_conexion(self, nodo):
        self.conexiones.append(nodo)

    def eliminar_conexion(self, nodo):
        if nodo in self.conexiones:
            self.conexiones.remove(nodo)

    def enviar_mensaje(self, mensaje):
        print(f'{self.nombre} envía: {mensaje}')
        for conexion in self.conexiones:
            conexion.recibir_mensaje(mensaje)
    
    def recibir_mensaje(self, mensaje):
        print(f'{self.nombre} recibe: {mensaje}')


servidor = Nodo('Servidor')
cliente1 = Nodo('Cliente 1')
cliente2 = Nodo('Cliente 2')
cliente3 = Nodo('Cliente 3')

servidor.agregar_conexion(cliente1)
servidor.agregar_conexion(cliente2)
servidor.agregar_conexion(cliente3)
cliente1.agregar_conexion(servidor)
cliente2.agregar_conexion(servidor)
cliente3.agregar_conexion(servidor)

servidor.enviar_mensaje(input("Escribe un mensaje para tus clientes: "))

servidor.eliminar_conexion(cliente3)

print("Reconectando con el servidor...")

time.sleep(5)

print("La conexión ha vuelto")