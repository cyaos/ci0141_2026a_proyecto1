db = db.getSiblingDB("distributed_client_db");

db.jugadores.drop();
db.videojuegos.drop();
db.rankings.drop();
db.partidas.drop();

db.jugadores.insertMany([
  {
    id_jugador: 1,
    nombre_usuario: "ShadowCR",
    pais: "Costa Rica",
    fecha_registro: "2024-01-15"
  },
  {
    id_jugador: 2,
    nombre_usuario: "PixelWolf",
    pais: "Mexico",
    fecha_registro: "2024-02-10"
  },
  {
    id_jugador: 3,
    nombre_usuario: "NovaKnight",
    pais: "Colombia",
    fecha_registro: "2024-03-05"
  },
  {
    id_jugador: 4,
    nombre_usuario: "LunaByte",
    pais: "Argentina",
    fecha_registro: "2024-04-20"
  },
  {
    id_jugador: 5,
    nombre_usuario: "CyberTico",
    pais: "Costa Rica",
    fecha_registro: "2024-05-12"
  }
]);

db.videojuegos.insertMany([
  {
    id_videojuego: 1,
    titulo: "Valorant",
    genero: "Shooter tactico"
  },
  {
    id_videojuego: 2,
    titulo: "League of Legends",
    genero: "MOBA"
  },
  {
    id_videojuego: 3,
    titulo: "Rocket League",
    genero: "Deportes"
  }
]);

db.rankings.insertMany([
  {
    id_ranking: 1,
    id_jugador: 1,
    id_videojuego: 1,
    temporada: "2026-A",
    posicion: 15,
    puntaje: 2450,
    partidas_jugadas: 80,
    partidas_ganadas: 52
  },
  {
    id_ranking: 2,
    id_jugador: 2,
    id_videojuego: 1,
    temporada: "2026-A",
    posicion: 8,
    puntaje: 2780,
    partidas_jugadas: 95,
    partidas_ganadas: 61
  },
  {
    id_ranking: 3,
    id_jugador: 3,
    id_videojuego: 2,
    temporada: "2026-A",
    posicion: 22,
    puntaje: 2100,
    partidas_jugadas: 70,
    partidas_ganadas: 39
  },
  {
    id_ranking: 4,
    id_jugador: 4,
    id_videojuego: 3,
    temporada: "2026-A",
    posicion: 11,
    puntaje: 2600,
    partidas_jugadas: 88,
    partidas_ganadas: 55
  },
  {
    id_ranking: 5,
    id_jugador: 5,
    id_videojuego: 1,
    temporada: "2026-A",
    posicion: 30,
    puntaje: 1850,
    partidas_jugadas: 60,
    partidas_ganadas: 31
  }
]);

db.partidas.insertMany([
  {
    id_partida: 1,
    id_jugador: 1,
    id_videojuego: 1,
    fecha: "2026-05-01",
    resultado: "Victoria",
    puntos_obtenidos: 25
  },
  {
    id_partida: 2,
    id_jugador: 2,
    id_videojuego: 1,
    fecha: "2026-05-02",
    resultado: "Derrota",
    puntos_obtenidos: -15
  },
  {
    id_partida: 3,
    id_jugador: 3,
    id_videojuego: 2,
    fecha: "2026-05-03",
    resultado: "Victoria",
    puntos_obtenidos: 30
  },
  {
    id_partida: 4,
    id_jugador: 4,
    id_videojuego: 3,
    fecha: "2026-05-04",
    resultado: "Victoria",
    puntos_obtenidos: 20
  },
  {
    id_partida: 5,
    id_jugador: 5,
    id_videojuego: 1,
    fecha: "2026-05-05",
    resultado: "Derrota",
    puntos_obtenidos: -10
  }
]);
