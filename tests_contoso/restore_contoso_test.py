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
)

print("Conexão realizada com sucesso!")
print()


# ============================================================
# 8. Cria/verifica a Credential para o Blob Storage
# ============================================================

print("Configurando acesso ao Blob Storage...")
print()

cursor = connection.cursor()

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
# 9. Verifica a Credential registrada
# ============================================================

print("Verificando credencial registrada no SQL Server...")
print()

cursor.execute("""
SELECT
    name,
    credential_identity
FROM sys.credentials
WHERE name =
'https://stcontosoretaildw01.blob.core.windows.net/backups';
""")

row = cursor.fetchone()

if row:
    print("Credential:", row.name)
    print("Identity:", row.credential_identity)
else:
    raise RuntimeError(
        "Credential não encontrada."
    )


# ============================================================
# 10. Testa acesso ao arquivo .bak
# ============================================================

print()
print("Testando acesso ao arquivo .bak...")
print(BACKUP_URL)
print()

print("Executando RESTORE HEADERONLY...")
print()

cursor.execute(f"""
RESTORE HEADERONLY
FROM URL = '{BACKUP_URL}';
""")

rows = cursor.fetchall()


# ============================================================
# 11. Exibe informações do backup
# ============================================================

print()
print("Backup acessado com sucesso!")
print(f"Quantidade de conjuntos de backup: {len(rows)}")
print()

for row in rows:
    print("DatabaseName:", row.DatabaseName)
    print("BackupType:", row.BackupType)
    print("BackupStartDate:", row.BackupStartDate)
    print("BackupFinishDate:", row.BackupFinishDate)
    print()


# ============================================================
# 12. Fecha conexão
# ============================================================

cursor.close()
connection.close()

print("Conexão encerrada.")