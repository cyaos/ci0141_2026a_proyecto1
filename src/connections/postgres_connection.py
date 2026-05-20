import psycopg
from psycopg.rows import dict_row


class PostgresConnection:
    def __init__(self):
        self.nombre = "PostgreSQL"
        self.conexion = None
        self.esta_activa = False

    def conectar(self):
        try:
            self.conexion = psycopg.connect(
                host="localhost",
                port=5432,
                dbname="distributed_client_db",
                user="admin",
                password="admin123",
                row_factory=dict_row
            )

            self.esta_activa = True
            print("Listo: conectado a PostgreSQL.")
            return True

        except Exception as error:
            self.esta_activa = False
            print("No se pudo conectar a PostgreSQL.")
            print("Detalle:", error)
            return False

    def desconectar(self):
        if self.conexion:
            self.conexion.close()
            self.conexion = None
            self.esta_activa = False
            print("Conexion a PostgreSQL cerrada.")

    def probar_conexion(self):
        if not self.conexion:
            return False

        try:
            with self.conexion.cursor() as cursor:
                cursor.execute("SELECT 1 AS estado;")
                cursor.fetchone()
            return True

        except Exception:
            self.esta_activa = False
            return False

    def listar_jugadores(self):
        with self.conexion.cursor() as cursor:
            cursor.execute("""
                SELECT id_jugador, nombre_usuario, pais, fecha_registro
                FROM jugadores
                ORDER BY id_jugador;
            """)
            return cursor.fetchall()

    def insertar_jugador(self, nombre_usuario, pais, fecha_registro):
        with self.conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO jugadores (nombre_usuario, pais, fecha_registro)
                VALUES (%s, %s, %s)
                RETURNING id_jugador, nombre_usuario, pais, fecha_registro;
            """, (nombre_usuario, pais, fecha_registro))

            jugador = cursor.fetchone()

        self.conexion.commit()
        return jugador

    def actualizar_jugador(self, id_jugador, nombre_usuario, pais):
        with self.conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE jugadores
                SET nombre_usuario = %s,
                    pais = %s
                WHERE id_jugador = %s
                RETURNING id_jugador, nombre_usuario, pais, fecha_registro;
            """, (nombre_usuario, pais, id_jugador))

            jugador = cursor.fetchone()

        self.conexion.commit()
        return jugador

    def eliminar_jugador(self, id_jugador):
        with self.conexion.cursor() as cursor:
            cursor.execute("""
                DELETE FROM partidas
                WHERE id_jugador = %s;
            """, (id_jugador,))

            cursor.execute("""
                DELETE FROM rankings
                WHERE id_jugador = %s;
            """, (id_jugador,))

            cursor.execute("""
                DELETE FROM jugadores
                WHERE id_jugador = %s
                RETURNING id_jugador, nombre_usuario, pais;
            """, (id_jugador,))

            jugador = cursor.fetchone()

        self.conexion.commit()
        return jugador

    def listar_rankings(self):
        with self.conexion.cursor() as cursor:
            cursor.execute("""
                SELECT
                    r.id_ranking,
                    j.nombre_usuario,
                    v.titulo AS videojuego,
                    r.temporada,
                    r.posicion,
                    r.puntaje,
                    r.partidas_jugadas,
                    r.partidas_ganadas
                FROM rankings r
                JOIN jugadores j ON r.id_jugador = j.id_jugador
                JOIN videojuegos v ON r.id_videojuego = v.id_videojuego
                ORDER BY r.posicion;
            """)
            return cursor.fetchall()

    def insertar_ranking(self, id_jugador, id_videojuego, temporada, posicion, puntaje):
        with self.conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO rankings (
                    id_jugador,
                    id_videojuego,
                    temporada,
                    posicion,
                    puntaje,
                    partidas_jugadas,
                    partidas_ganadas
                )
                VALUES (%s, %s, %s, %s, %s, 0, 0)
                RETURNING *;
            """, (id_jugador, id_videojuego, temporada, posicion, puntaje))

            ranking = cursor.fetchone()

        self.conexion.commit()
        return ranking

    def actualizar_ranking(self, id_ranking, posicion, puntaje, partidas_jugadas, partidas_ganadas):
        with self.conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE rankings
                SET posicion = %s,
                    puntaje = %s,
                    partidas_jugadas = %s,
                    partidas_ganadas = %s,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id_ranking = %s
                RETURNING *;
            """, (posicion, puntaje, partidas_jugadas, partidas_ganadas, id_ranking))

            ranking = cursor.fetchone()

        self.conexion.commit()
        return ranking

    def eliminar_ranking(self, id_ranking):
        with self.conexion.cursor() as cursor:
            cursor.execute("""
                DELETE FROM rankings
                WHERE id_ranking = %s
                RETURNING *;
            """, (id_ranking,))

            ranking = cursor.fetchone()

        self.conexion.commit()
        return ranking