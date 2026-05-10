from pymongo import MongoClient


class MongoConnection:
    # Maneja la conexión a MongoDB y proporciona métodos básicos.
    def __init__(self):
        self.name = "MongoDB"
        self.client = None
        self.database = None
        self.is_active = False

    def connect(self):
        # Intenta crear el cliente y hacer un 'ping' al servidor para validar.
        try:
            self.client = MongoClient(
                "mongodb://localhost:27017/",
                serverSelectionTimeoutMS=3000
            )

            # Ping para asegurar que el servidor responde.
            self.client.admin.command("ping")
            self.database = self.client["distributed_client_db"]
            self.is_active = True

            print("Listo: conectado a MongoDB.")
            return True

        except Exception as error:
            # Mantener is_active en False si falla la conexión.
            self.is_active = False
            print("No se pudo conectar a MongoDB.")
            print("Detalle:", error)
            return False

    def disconnect(self):
        # Cierra el cliente si existe y limpia los atributos.
        if self.client:
            self.client.close()
            self.client = None
            self.database = None
            self.is_active = False
            print("Conexión a MongoDB cerrada.")

    def test_connection(self):
        # Devuelve True si el cliente responde al ping.
        if not self.client:
            return False

        try:
            self.client.admin.command("ping")
            return True

        except Exception:
            self.is_active = False
            return False