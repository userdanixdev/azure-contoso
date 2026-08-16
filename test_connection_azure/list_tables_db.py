import os
import struct

import pyodbc
from azure.identity import InteractiveBrowserCredential
from dotenv import load_dotenv


# Carrega as variáveis do arquivo .env
load_dotenv()


# Configurações do Azure SQL
SERVER = os.getenv("AZURE_SQL_SERVER")
DATABASE = os.getenv("AZURE_SQL_DATABASE")
ID_LOCATARIO = os.getenv("ID_LOCATARIO")


if not SERVER:
    raise ValueError(
        "AZURE_SQL_SERVER não foi encontrado no arquivo .env"
    )

if not DATABASE:
    raise ValueError(
        "AZURE_SQL_DATABASE não foi encontrado no arquivo .env"
    )

if not ID_LOCATARIO:
    raise ValueError(
        "ID_LOCATARIO não foi encontrado no arquivo .env"
    )


# Autenticação Microsoft Entra ID
credential = InteractiveBrowserCredential(
    tenant_id=ID_LOCATARIO
)

token = credential.get_token(
    "https://database.windows.net/.default"
)

token_bytes = token.token.encode("utf-16-le")

token_struct = struct.pack(
    f"<I{len(token_bytes)}s",
    len(token_bytes),
    token_bytes,
)


# Constante do ODBC para autenticação via Access Token
SQL_COPT_SS_ACCESS_TOKEN = 1256


# String de conexão
connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)


# Estabelece a conexão
connection = pyodbc.connect(
    connection_string,
    attrs_before={
        SQL_COPT_SS_ACCESS_TOKEN: token_struct
    },
)


print("Conexão realizada com sucesso!")
print(f"Banco: {DATABASE}")
print()

# Consultas:
# Cria o cursor
cursor = connection.cursor()

# Consulta as tabelas existentes
cursor.execute(
    """
    SELECT
        TABLE_SCHEMA,
        TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_SCHEMA, TABLE_NAME;
    """
)


# Recupera todas as tabelas
tables = cursor.fetchall()


# Exibe as tabelas
print("Tabelas existentes:")
print("-" * 50)

for table in tables:
    print(f"{table.TABLE_SCHEMA}.{table.TABLE_NAME}")


print("-" * 50)
print(f"Total de tabelas: {len(tables)}")


# Fecha cursor e conexão
cursor.close()
connection.close()


print()
print("Conexão encerrada.")