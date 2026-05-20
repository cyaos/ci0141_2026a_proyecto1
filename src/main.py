from connections.connection_manager import ConnectionManager


def imprimir_registros(registros):
    if not registros:
        print("No hay registros para mostrar.")
        return

    for registro in registros:
        print(registro)


def obtener_motor_activo(administrador):
    motor_activo = administrador.obtener_conexion_activa()

    if not motor_activo:
        return None

    return motor_activo


def menu_crud_jugadores(administrador):
    while True:
        print("\n=== CRUD de Jugadores ===")
        print("1. Listar jugadores")
        print("2. Insertar jugador")
        print("3. Actualizar jugador")
        print("4. Eliminar jugador")
        print("5. Volver")

        opcion = input("Elige una opcion (1-5): ")

        motor_activo = obtener_motor_activo(administrador)

        if not motor_activo:
            return

        try:
            if opcion == "1":
                jugadores = motor_activo.listar_jugadores()
                imprimir_registros(jugadores)

            elif opcion == "2":
                nombre_usuario = input("Nombre de usuario: ")
                pais = input("Pais: ")
                fecha_registro = input("Fecha de registro (YYYY-MM-DD): ")

                jugador = motor_activo.insertar_jugador(
                    nombre_usuario,
                    pais,
                    fecha_registro
                )

                print("Jugador insertado:")
                print(jugador)

            elif opcion == "3":
                id_jugador = int(input("ID del jugador: "))
                nombre_usuario = input("Nuevo nombre de usuario: ")
                pais = input("Nuevo pais: ")

                jugador = motor_activo.actualizar_jugador(
                    id_jugador,
                    nombre_usuario,
                    pais
                )

                if jugador:
                    print("Jugador actualizado:")
                    print(jugador)
                else:
                    print("No se encontro el jugador.")

            elif opcion == "4":
                id_jugador = int(input("ID del jugador a eliminar: "))

                jugador = motor_activo.eliminar_jugador(id_jugador)

                if jugador:
                    print("Jugador eliminado:")
                    print(jugador)
                else:
                    print("No se encontro el jugador.")

            elif opcion == "5":
                break

            else:
                print("Opcion invalida.")

        except Exception as error:
            print("Error ejecutando operacion CRUD de jugadores.")
            print("Detalle:", error)


def menu_crud_rankings(administrador):
    while True:
        print("\n=== CRUD de Rankings ===")
        print("1. Listar rankings")
        print("2. Insertar ranking")
        print("3. Actualizar ranking")
        print("4. Eliminar ranking")
        print("5. Volver")

        opcion = input("Elige una opcion (1-5): ")

        motor_activo = obtener_motor_activo(administrador)

        if not motor_activo:
            return

        try:
            if opcion == "1":
                rankings = motor_activo.listar_rankings()
                imprimir_registros(rankings)

            elif opcion == "2":
                id_jugador = int(input("ID del jugador: "))
                id_videojuego = int(input("ID del videojuego: "))
                temporada = input("Temporada: ")
                posicion = int(input("Posicion: "))
                puntaje = int(input("Puntaje: "))

                ranking = motor_activo.insertar_ranking(
                    id_jugador,
                    id_videojuego,
                    temporada,
                    posicion,
                    puntaje
                )

                print("Ranking insertado:")
                print(ranking)

            elif opcion == "3":
                id_ranking = int(input("ID del ranking: "))
                posicion = int(input("Nueva posicion: "))
                puntaje = int(input("Nuevo puntaje: "))
                partidas_jugadas = int(input("Partidas jugadas: "))
                partidas_ganadas = int(input("Partidas ganadas: "))

                ranking = motor_activo.actualizar_ranking(
                    id_ranking,
                    posicion,
                    puntaje,
                    partidas_jugadas,
                    partidas_ganadas
                )

                if ranking:
                    print("Ranking actualizado:")
                    print(ranking)
                else:
                    print("No se encontro el ranking.")

            elif opcion == "4":
                id_ranking = int(input("ID del ranking a eliminar: "))

                ranking = motor_activo.eliminar_ranking(id_ranking)

                if ranking:
                    print("Ranking eliminado:")
                    print(ranking)
                else:
                    print("No se encontro el ranking.")

            elif opcion == "5":
                break

            else:
                print("Opcion invalida.")

        except Exception as error:
            print("Error ejecutando operacion CRUD de rankings.")
            print("Detalle:", error)


def main():
    administrador = ConnectionManager()
    administrador.conectar_todos()

    while True:
        print("\n=== Cliente de Bases de Datos Distribuidas ===")

        nombre_motor_activo = "Ninguno"
        if administrador.motor_activo:
            nombre_motor_activo = administrador.conexiones[administrador.motor_activo].nombre

        print(f"Motor activo: {nombre_motor_activo}")
        print("1. Mostrar estado de conexiones")
        print("2. Cambiar a PostgreSQL")
        print("3. Cambiar a MongoDB")
        print("4. Mostrar motor activo")
        print("5. CRUD de jugadores")
        print("6. CRUD de rankings")
        print("7. Salir")

        opcion = input("Elige una opcion (1-7): ")

        if opcion == "1":
            administrador.mostrar_conexiones()

        elif opcion == "2":
            administrador.seleccionar_motor_activo("postgres")

        elif opcion == "3":
            administrador.seleccionar_motor_activo("mongo")

        elif opcion == "4":
            administrador.mostrar_motor_activo()

        elif opcion == "5":
            menu_crud_jugadores(administrador)

        elif opcion == "6":
            menu_crud_rankings(administrador)

        elif opcion == "7":
            administrador.desconectar_todos()
            print("Hasta luego. Conexiones cerradas.")
            break

        else:
            print("Opcion invalida, intentalo de nuevo.")


if __name__ == "__main__":
    main()