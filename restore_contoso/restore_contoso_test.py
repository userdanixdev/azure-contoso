import os
import struct

import pyodbc
from azure.identity import InteractiveBrowserCredential
from dotenv import load_dotenv


# Carrega variáveis do .env: Configurações da Managed Instance
load_dotenv()
ID_LOCATARIO = os.getenv("ID_LOCATARIO")
SERVER = os.getenv("AZURE_SQL_MI_SERVER")
DATABASE = os.getenv("AZURE_SQL_MI_MASTER_DATABASE")
BACKUP_URL = os.getenv("AZURE_BLOB_BACKUP_URL")
BLOB_CREDENTIAL = os.getenv("AZURE_BLOB_CREDENTIAL")

if not ID_LOCATARIO:
    raise ValueError(
        "ID_LOCATARIO não foi encontrado no arquivo .env"
    )
if not DATABASE:
    raise ValueError(
        "AZURE_SQL_DATABASE não foi encontrado no arquivo .env"
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
# O token é uma credencial temporária e dinâmica. Não se deve colocar no .env
token = credential.get_token(
    "https://database.windows.net/.default"
)

token_bytes = token.token.encode("utf-16-le")
# Assim também como o 'token_bytes' o Microsoft Entra ID fornece dinamicamente a
#  credencial necessária para acessar o banco.

token_struct = struct.pack(
    f"<I{len(token_bytes)}s",
    len(token_bytes),
    token_bytes,
)

# Constante ODBC para Access Token
SQL_COPT_SS_ACCESS_TOKEN = 1256

# String de conexão:

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

# Conexão com a Managed Instance:

print("Conectando à Managed Instance...")

connection = pyodbc.connect(
    connection_string,
    attrs_before={
        SQL_COPT_SS_ACCESS_TOKEN: token_struct
    },
)

print("Conexão realizada com sucesso!")
print()

# Cria/verifica a Credential para o Blob Storage

print("Configurando acesso ao Blob Storage...")
print()

cursor = connection.cursor()
# Atenção, para interpolação das variáveis de ambiente agora é necessário coloca a função 'f-string'.
# Nesse caso sem a interpolação o python interpretará como valor literal: Foi utilizado """ e não f""".
# O Python iria enviar literalmente.

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

# Verifica a Credential registrada ( Consulta de verificação )

print("Verificando credencial registrada no SQL Server...")
print()

cursor.execute(f"""
SELECT
    name,
    credential_identity
FROM sys.credentials
WHERE name = '{BLOB_CREDENTIAL}';
""")

row = cursor.fetchone()

if row:
    print("Credential:", row.name)
    print("Identity:", row.credential_identity)
else:
    raise RuntimeError(
        "Credential não encontrada."
    )

# Testa acesso ao arquivo .bak
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

# Exibe informações do backup:

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

# Fecha conexão:

cursor.close()
connection.close()

print("Conexão encerrada.")

# Esse código não transforma o .bak em um arquivo legível.
# Ele valida que a Managed Instance consegue acessar e interpretar o conteúdo do backup.
# Isso precisamos para antes de executar o RESTORE DATABASE.
# Aí sim o ContosoRetailDW.bak será utilizado para criar/restaurar o banco ContosoRetailDW dentro da Managed Instance.