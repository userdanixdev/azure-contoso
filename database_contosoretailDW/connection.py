import os
import struct

import pyodbc
from azure.identity import InteractiveBrowserCredential
from dotenv import load_dotenv


load_dotenv()


ID_LOCATARIO = os.getenv("ID_LOCATARIO")
SERVER = os.getenv("AZURE_SQL_MI_SERVER")
DATABASE = os.getenv("AZURE_SQL_MI_DATABASE")


if not ID_LOCATARIO:
    raise ValueError(
        "ID_LOCATARIO não foi encontrado no arquivo .env"
    )

if not SERVER:
    raise ValueError(
        "AZURE_SQL_MI_SERVER não foi encontrado no arquivo .env"
    )

if not DATABASE:
    raise ValueError(
        "AZURE_SQL_MI_DATABASE não foi encontrado no arquivo .env"
    )


SQL_COPT_SS_ACCESS_TOKEN = 1256


connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)


def get_connection():

    print("Conectando ao ContosoRetailDW...")

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

    connection = pyodbc.connect(
        connection_string,
        attrs_before={
            SQL_COPT_SS_ACCESS_TOKEN: token_struct
        },
    )

    print("Conexão realizada com sucesso!")

    return connection