from pymongo import MongoClient
from datetime import datetime


class MongoConnection:
    def __init__(self):
        self.nombre = "MongoDB"
        self.cliente = None
        self.base_datos = None
        self.esta_activa = False

    def conectar(self):
        try:
            self.cliente = MongoClient(
                "mongodb://localhost:27018/",
                serverSelectionTimeoutMS=3000
            )

            self.cliente.admin.command("ping")
            self.base_datos = self.cliente["distributed_client_db"]
            self.esta_activa = True

            print("Listo: conectado a MongoDB.")
            return True

        except Exception as error:
            self.esta_activa = False
            print("No se pudo conectar a MongoDB.")
            print("Detalle:", error)
            return False

    def desconectar(self):
        if self.cliente:
            self.cliente.close()
            self.cliente = None
            self.base_datos = None
            self.esta_activa = False
            print("Conexion a MongoDB cerrada.")

    def probar_conexion(self):
        if not self.cliente:
            return False

        try:
            self.cliente.admin.command("ping")
            return True

        except Exception:
            self.esta_activa = False
            return False

    def listar_jugadores(self):
        return list(
            self.base_datos.jugadores.find({}, {"_id": 0}).sort("id_jugador", 1)
        )

    def insertar_jugador(self, nombre_usuario, pais, fecha_registro):
        ultimo = self.base_datos.jugadores.find_one(sort=[("id_jugador", -1)])
        nuevo_id = 1 if not ultimo else ultimo["id_jugador"] + 1

        jugador = {
            "id_jugador": nuevo_id,
            "nombre_usuario": nombre_usuario,
            "pais": pais,
            "fecha_registro": fecha_registro
        }

        self.base_datos.jugadores.insert_one(jugador)
        jugador.pop("_id", None)
        return jugador

    def actualizar_jugador(self, id_jugador, nombre_usuario, pais):
        self.base_datos.jugadores.update_one(
            {"id_jugador": id_jugador},
            {
                "$set": {
                    "nombre_usuario": nombre_usuario,
                    "pais": pais
                }
            }
        )

        return self.base_datos.jugadores.find_one(
            {"id_jugador": id_jugador},
            {"_id": 0}
        )

    def eliminar_jugador(self, id_jugador):
        jugador = self.base_datos.jugadores.find_one(
            {"id_jugador": id_jugador},
            {"_id": 0}
        )

        self.base_datos.partidas.delete_many({"id_jugador": id_jugador})
        self.base_datos.rankings.delete_many({"id_jugador": id_jugador})
        self.base_datos.jugadores.delete_one({"id_jugador": id_jugador})

        return jugador

    def listar_rankings(self):
        return list(
            self.base_datos.rankings.find({}, {"_id": 0}).sort("posicion", 1)
        )

    def insertar_ranking(self, id_jugador, id_videojuego, temporada, posicion, puntaje):
        ultimo = self.base_datos.rankings.find_one(sort=[("id_ranking", -1)])
        nuevo_id = 1 if not ultimo else ultimo["id_ranking"] + 1

        ranking = {
            "id_ranking": nuevo_id,
            "id_jugador": id_jugador,
            "id_videojuego": id_videojuego,
            "temporada": temporada,
            "posicion": posicion,
            "puntaje": puntaje,
            "partidas_jugadas": 0,
            "partidas_ganadas": 0,
            "fecha_actualizacion": datetime.now()
        }

        self.base_datos.rankings.insert_one(ranking)
        ranking.pop("_id", None)
        return ranking

    def actualizar_ranking(self, id_ranking, posicion, puntaje, partidas_jugadas, partidas_ganadas):
        self.base_datos.rankings.update_one(
            {"id_ranking": id_ranking},
            {
                "$set": {
                    "posicion": posicion,
                    "puntaje": puntaje,
                    "partidas_jugadas": partidas_jugadas,
                    "partidas_ganadas": partidas_ganadas,
                    "fecha_actualizacion": datetime.now()
                }
            }
        )

        return self.base_datos.rankings.find_one(
            {"id_ranking": id_ranking},
            {"_id": 0}
        )

    def eliminar_ranking(self, id_ranking):
        ranking = self.base_datos.rankings.find_one(
            {"id_ranking": id_ranking},
            {"_id": 0}
        )

        self.base_datos.rankings.delete_one({"id_ranking": id_ranking})
        return ranking