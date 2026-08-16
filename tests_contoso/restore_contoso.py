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
# 2. Configurações da Managed Instance
# ============================================================

SERVER = (
    "mi-contoso-retail.public.b018dfd06a8a.database.windows.net,3342"
)

DATABASE = "master"


# ============================================================
# 3. URL do backup no Blob Storage
# ============================================================

BACKUP_URL = (
    "https://stcontosoretaildw01.blob.core.windows.net/"
    "backups/ContosoRetailDW.bak"
)


# ============================================================
# 4. Autenticação Microsoft Entra ID
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
# 5. Constante ODBC para Access Token
# ============================================================

SQL_COPT_SS_ACCESS_TOKEN = 1256


# ============================================================
# 6. String de conexão
# ============================================================

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)


# ============================================================
# 7. Conecta na Managed Instance
# ============================================================

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


# ============================================================
# 8. Configura a Credential para o Blob Storage
# ============================================================

cursor = connection.cursor()

print("Configurando acesso ao Blob Storage...")
print()

credential_sql = """
IF NOT EXISTS (
    SELECT 1
    FROM sys.credentials
    WHERE name = 'https://stcontosoretaildw01.blob.core.windows.net/backups'
)
BEGIN
    CREATE CREDENTIAL [https://stcontosoretaildw01.blob.core.windows.net/backups]
    WITH IDENTITY = 'MANAGED IDENTITY';
END
"""

cursor.execute(credential_sql)

print("Credencial criada/verificada com sucesso!")
print()


# ============================================================
# 9. Verifica a Credential
# ============================================================

cursor.execute("""
SELECT
    name,
    credential_identity
FROM sys.credentials
WHERE name =
    'https://stcontosoretaildw01.blob.core.windows.net/backups';
""")

row = cursor.fetchone()

if not row:
    raise RuntimeError(
        "Credential não encontrada."
    )

print("Credential:", row.name)
print("Identity:", row.credential_identity)
print()


# ============================================================
# 10. Executa o RESTORE
# ============================================================

print("Iniciando restore do ContosoRetailDW...")
print()
print("Executando RESTORE DATABASE...")
print()

restore_sql = f"""
RESTORE DATABASE [ContosoRetailDW]
FROM URL = '{BACKUP_URL}';
"""

cursor.execute(restore_sql)

print()
print("Restore concluído com sucesso!")
print()


# ============================================================
# 11. Verifica o banco restaurado
# ============================================================

print("Verificando o banco restaurado...")
print()

cursor.execute("""
SELECT
    name,
    state_desc
FROM sys.databases
WHERE name = 'ContosoRetailDW';
""")

row = cursor.fetchone()

if row:
    print(f"Banco:  {row.name}")
    print(f"Estado: {row.state_desc}")
else:
    print("Banco ContosoRetailDW não encontrado.")


# ============================================================
# 12. Fecha conexão
# ============================================================

cursor.close()
connection.close()

print()
print("Conexão encerrada.")