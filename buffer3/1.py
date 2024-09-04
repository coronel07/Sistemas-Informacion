import random

class Nodo:
    def __init__(self, nombre):
        self.nombre = nombre
        self.buffer = []

    def enviar_mensaje(self, mensaje, destino):
       
        if random.random() < 0.3: 
            print(f"Mensaje perdido en el nodo {self.nombre}!")
        else:
            destino.recibir_mensaje(mensaje)

    def recibir_mensaje(self, mensaje):
        self.buffer.append(mensaje)

    def procesar_buffer(self):
        if self.buffer:
            mensaje = self.buffer.pop(0)
            print(f"Nodo {self.nombre} procesando mensaje: {mensaje}")

nodo1 = Nodo("Nodo A")
nodo2 = Nodo("Nodo B")

nodo1.enviar_mensaje("Hola Nodo B", nodo2)
nodo1.enviar_mensaje("¿Como estas?", nodo2)

nodo2.procesar_buffer()
nodo2.procesar_buffer()
