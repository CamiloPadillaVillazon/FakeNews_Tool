"""
Prueba rapida de conexion a PostgreSQL.
Lee la cadena de conexion desde .env (via settings) y NO imprime la contrasena.
Ejecutar desde la raiz del proyecto:
    .venv\\Scripts\\python backend\\test_db_connection.py
"""
from sqlalchemy import create_engine, inspect, text
from app.config.settings import settings


def main():
    # Ocultar la contrasena al mostrar la URL
    url = settings.database_url
    safe_url = url
    if "@" in url and ":" in url.split("@")[0]:
        prefix, rest = url.split("@", 1)
        user = prefix.rsplit(":", 1)[0]
        safe_url = f"{user}:****@{rest}"

    print(f"Conectando a: {safe_url}")
    engine = create_engine(url)

    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
            db = conn.execute(text("SELECT current_database();")).scalar()
        print("Conexion EXITOSA")
        print(f"  Base de datos: {db}")
        print(f"  Version      : {version.split(',')[0]}")

        tables = inspect(engine).get_table_names()
        print(f"  Tablas       : {tables if tables else '(ninguna todavia — arranca el server para crear claims)'}")
    except Exception as exc:
        print("Conexion FALLIDA")
        print(f"  {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
