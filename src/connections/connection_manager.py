from connections.postgres_connection import PostgresConnection
from connections.mongo_connection import MongoConnection


class ConnectionManager:
    def __init__(self):
        self.conexiones = {
            "postgres": PostgresConnection(),
            "mongo": MongoConnection()
        }

        self.motor_activo = None

    def conectar_todos(self):
        print("Iniciando conexiones...")

        for nombre_motor, conexion in self.conexiones.items():
            conectado = conexion.conectar()

            if conectado and self.motor_activo is None:
                self.motor_activo = nombre_motor

        if self.motor_activo:
            print(f"Motor activo inicial: {self.conexiones[self.motor_activo].nombre}")
        else:
            print("No hay motores activos.")

    def desconectar_todos(self):
        for conexion in self.conexiones.values():
            conexion.desconectar()

        self.motor_activo = None

    def seleccionar_motor_activo(self, nombre_motor):
        if nombre_motor not in self.conexiones:
            print("Motor no reconocido.")
            return False

        conexion = self.conexiones[nombre_motor]

        if not conexion.esta_activa:
            print(f"El motor {conexion.nombre} no esta activo.")
            return False

        self.motor_activo = nombre_motor
        print(f"Motor activo cambiado a: {conexion.nombre}")
        return True

    def obtener_conexion_activa(self):
        if not self.motor_activo:
            print("No hay un motor activo seleccionado.")
            return None

        conexion = self.conexiones[self.motor_activo]

        if not conexion.probar_conexion():
            print(f"La conexion con {conexion.nombre} no esta disponible.")
            return None

        return conexion

    def mostrar_motor_activo(self):
        if not self.motor_activo:
            print("No hay motor activo.")
            return

        conexion = self.conexiones[self.motor_activo]
        print(f"Motor activo: {conexion.nombre}")

    def mostrar_conexiones(self):
        print("\n=== Estado de conexiones ===")

        for nombre_motor, conexion in self.conexiones.items():
            estado = "Activa" if conexion.esta_activa else "Inactiva"
            activo = " <- motor activo" if nombre_motor == self.motor_activo else ""
            print(f"{conexion.nombre}: {estado}{activo}")