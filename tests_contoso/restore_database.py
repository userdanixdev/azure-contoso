import os
import struct

import pyodbc
from azure.identity import InteractiveBrowserCredential
from dotenv import load_dotenv


# Carrega variáveis do .env: Configurações do SQL Managed Instance

load_dotenv()

ID_LOCATARIO = os.getenv("ID_LOCATARIO")
SERVER = os.getenv("AZURE_SQL_MI_SERVER")
DATABASE = os.getenv("AZURE_SQL_MI_DATABASE")
BACKUP_URL = os.getenv("AZURE_BLOB_BACKUP_URL")
BLOB_CREDENTIAL = os.getenv("AZURE_BLOB_CREDENTIAL")

if not ID_LOCATARIO:
    raise ValueError(
        "ID_LOCATARIO não foi encontrado no arquivo .env"
    )
if not DATABASE:
    raise ValueError(
        "AZURE_SQL_MI_DATABASE não foi encontrado no arquivo .env"
    )

if not SERVER:
    raise ValueError(
        "AZURE_SQL_MI_SERVER não foi encontrado no arquivo .env"
    )

if not BACKUP_URL:
    raise ValueError(
        "AZURE_BLOB_BACKUP_URL não foi encontrado no arquivo .env"
    )

if not BLOB_CREDENTIAL:
    raise ValueError(
        "AZURE_BLOB_CREDENTIAL não foi encontrado no arquivo .env"
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
# Constante ODBC para Access Token:
SQL_COPT_SS_ACCESS_TOKEN = 1256

# String de conexão:

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

# Conecta na Managed Instance:

print("Conectando à Managed Instance...")
connection = pyodbc.connect(
    connection_string,
    attrs_before={
        SQL_COPT_SS_ACCESS_TOKEN: token_struct
    },
    autocommit=True,
)

print("Conexão realizada com sucesso!")
print()

# Configura a Credential para o Blob Storage:
cursor = connection.cursor()

print("Configurando acesso ao Blob Storage...")
print()

credential_sql = f"""
IF NOT EXISTS (
    SELECT 1
    FROM sys.credentials
    WHERE name = '{BLOB_CREDENTIAL}'
)
BEGIN
    CREATE CREDENTIAL [{BLOB_CREDENTIAL}]
    WITH IDENTITY = 'MANAGED IDENTITY';
END
"""

cursor.execute(credential_sql)

print("Credencial criada/verificada com sucesso!")
print()

# Verifica a Credential:
cursor.execute(f"""
SELECT
    name,
    credential_identity
FROM sys.credentials
WHERE name =
    '{BLOB_CREDENTIAL}';
""")

row = cursor.fetchone()

if not row:
    raise RuntimeError(
        "Credential não encontrada."
    )

print("Credential:", row.name)
print("Identity:", row.credential_identity)
print()

# Executa o RESTORE

print("Iniciando restore do ContosoRetailDW...")
print()
print("Executando RESTORE DATABASE...")
print()

restore_sql = f"""
RESTORE DATABASE [{DATABASE}]
FROM URL = '{BACKUP_URL}';
"""

cursor.execute(restore_sql)

print()
print("Restore concluído com sucesso!")
print()

# Verifica o banco restaurado:

print("Verificando o banco restaurado...")
print()

cursor.execute(f"""
SELECT
    name,
    state_desc
FROM sys.databases
WHERE name = '{DATABASE}';
""")

row = cursor.fetchone()

if row:
    print(f"Banco:  {row.name}")
    print(f"Estado: {row.state_desc}")
else:
    print("Banco ContosoRetailDW não encontrado.")

# Fecha conexão:

cursor.close()
connection.close()

print()
print("Conexão encerrada.")