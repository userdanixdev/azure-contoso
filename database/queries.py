from connection import get_connection


# ============================================================
# Consulta: listar tabelas
# ============================================================

def listar_tabelas():

    connection = get_connection()
    cursor = connection.cursor()

    print()
    print("Tabelas do banco:")
    print()

    cursor.execute("""
        SELECT
            TABLE_SCHEMA,
            TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME;
    """)

    rows = cursor.fetchall()

    for row in rows:
        print(f"{row.TABLE_SCHEMA}.{row.TABLE_NAME}")

    cursor.close()
    connection.close()


# ============================================================
# Execução
# ============================================================

if __name__ == "__main__":
    listar_tabelas()