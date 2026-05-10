from connections.postgres_connection import PostgresConnection
from connections.mongo_connection import MongoConnection


class ConnectionManager:
    # Gestiona instancias de conexión para cada motor y mantiene el motor activo.
    def __init__(self):
        # Mapa de claves a objetos de conexión.
        self.connections = {
            "postgres": PostgresConnection(),
            "mongo": MongoConnection()
        }
        # Clave del motor actualmente seleccionado (ej. 'postgres' o 'mongo').
        self.active_engine = None

    def connect_all(self):
        # Intenta conectar a todos los motores registrados.
        print("\nConectando con las bases de datos disponibles...\n")

        for connection in self.connections.values():
            connection.connect()

    def show_connections(self):
        # Muestra estado de cada conexión y marca cuál está en uso.
        print("\n=== Estado de Conexiones ===")

        for key, connection in self.connections.items():
            status = "activo" if connection.test_connection() else "inactivo"
            active_marker = " (en uso)" if self.active_engine == key else ""
            print(f"{key}: {connection.name} - {status}{active_marker}")

    def set_active_engine(self, engine_key):
        if engine_key not in self.connections:
            # La clave proporcionada no corresponde a ningún motor conocido.
            print("Error: el motor de base de datos no está registrado.")
            return False

        connection = self.connections[engine_key]

        if not connection.test_connection():
            # Si no pasa la prueba de conexión no se puede activar.
            print(f"Error: {connection.name} no está disponible.")
            return False

        # Guardamos la clave del motor activo.
        self.active_engine = engine_key
        print(f"Listo: ahora se usará {connection.name} como motor activo.")
        return True

    def get_active_connection(self):
        if not self.active_engine:
            # No hay motor activo seleccionado.
            print("Error: no se ha seleccionado ningún motor activo.")
            return None

        return self.connections[self.active_engine]

    def disconnect_all(self):
        # Cierra todas las conexiones (si están abiertas).
        for connection in self.connections.values():
            connection.disconnect()