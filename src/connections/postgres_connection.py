import psycopg
from psycopg.rows import dict_row


class PostgresConnection:
    # Gestor simple para la conexión a PostgreSQL.
    def __init__(self):
        self.name = "PostgreSQL"
        self.connection = None
        self.is_active = False

    def connect(self):
        # Intenta abrir la conexión usando psycopg y valida con row_factory.
        try:
            self.connection = psycopg.connect(
                host="localhost",
                port=5432,
                dbname="distributed_client_db",
                user="admin",
                password="admin123",
                row_factory=dict_row
            )

            self.is_active = True
            print("Listo: conectado a PostgreSQL.")
            return True

        except Exception as error:
            # Si falla, dejamos is_active en False y mostramos el detalle.
            self.is_active = False
            print("No se pudo conectar a PostgreSQL.")
            print("Detalle:", error)
            return False

    def disconnect(self):
        # Cierra la conexión si existe y limpia el estado.
        if self.connection:
            self.connection.close()
            self.connection = None
            self.is_active = False
            print("Conexión a PostgreSQL cerrada.")

    def test_connection(self):
        # Ejecuta una consulta mínima para verificar la salud de la conexión.
        if not self.connection:
            return False

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1 AS status;")
                cursor.fetchone()
            return True

        except Exception:
            self.is_active = False
            return False