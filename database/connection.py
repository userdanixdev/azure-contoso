import os
import struct

import pyodbc
from azure.identity import InteractiveBrowserCredential
from dotenv import load_dotenv


# ============================================================
# 1. Carrega variáveis do .env
# ============================================================

load_dotenv()

ID_LOCATARIO = os.getenv("ID_LOCATARIO")

if not ID_LOCATARIO:
    raise ValueError(
        "ID_LOCATARIO não foi encontrado no arquivo .env"
    )


# ============================================================
# 2. Configurações
# ============================================================

SERVER = (
    "mi-contoso-retail.public.b018dfd06a8a.database.windows.net,3342"
)

DATABASE = "ContosoRetailDW"


# ============================================================
# 3. Autenticação Microsoft Entra ID
# ============================================================

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


# ============================================================
# 4. Constante ODBC
# ============================================================

SQL_COPT_SS_ACCESS_TOKEN = 1256


# ============================================================
# 5. String de conexão
# ============================================================

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)


# ============================================================
# 6. Função de conexão
# ============================================================

def get_connection():

    print("Conectando ao ContosoRetailDW...")

    connection = pyodbc.connect(
        connection_string,
        attrs_before={
            SQL_COPT_SS_ACCESS_TOKEN: token_struct
        },
    )

    print("Conexão realizada com sucesso!")

    return connection