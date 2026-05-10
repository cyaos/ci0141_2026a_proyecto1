from connections.connection_manager import ConnectionManager


def main():
    # Punto de entrada: crea el gestor y trata de conectar a los motores disponibles.
    manager = ConnectionManager()
    manager.connect_all()

    while True:
        # Menú sencillo para interactuar con las conexiones.
        print("\n=== Cliente de Bases de Datos Distribuidas ===")
        print("1. Mostrar estado de conexiones")
        print("2. Cambiar a PostgreSQL")
        print("3. Cambiar a MongoDB")
        print("4. Mostrar motor activo")
        print("5. Salir")

        option = input("Elige una opción (1-5): ")

        if option == "1":
            # Muestra si cada motor está activo o no.
            manager.show_connections()

        elif option == "2":
            # Intenta establecer PostgreSQL como motor activo.
            manager.set_active_engine("postgres")

        elif option == "3":
            # Intenta establecer MongoDB como motor activo.
            manager.set_active_engine("mongo")

        elif option == "4":
            # Muestra información del motor activo si hay uno.
            active = manager.get_active_connection()
            if active:
                print(f"Motor activo: {active.name}")

        elif option == "5":
            # Cierra las conexiones y sale del programa.
            manager.disconnect_all()
            print("Hasta luego — conexiones cerradas.")
            break

        else:
            print("Opción inválida, inténtalo de nuevo.")


if __name__ == "__main__":
    main()