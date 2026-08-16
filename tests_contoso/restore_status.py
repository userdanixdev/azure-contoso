import os
import pyodbc
from azure.identity import InteractiveBrowserCredential
from dotenv import load_dotenv

load_dotenv()

SERVER = os.getenv("AZURE_SQL_MI_SERVER")
ID_LOCATARIO = os.getenv("ID_LOCATARIO")
DATABASE = os.getenv("AZURE_SQL_MI_DATABASE")
# Valida configurações

if not SERVER:
    raise ValueError(
        "AZURE_SQL_MI_SERVER não foi encontrado no arquivo .env"
    )

if not DATABASE:
    raise ValueError(
        "AZURE_SQL_MI_DATABASE não foi encontrado no arquivo .env"
    )

if not ID_LOCATARIO:
    raise ValueError(
        "ID_LOCATARIO não foi encontrado no arquivo .env"
    )

# Autenticação Microsoft Entra ID:

# Variávels dinâmincas, não irão para o .env:

credential = InteractiveBrowserCredential(
    tenant_id=ID_LOCATARIO
)

print(" Autenticando no Microsoft Entra ID...")

token = credential.get_token(
    "https://database.windows.net/.default"
)

print(" Autenticação concluída.")

# Converte o Access Token para o formato esperado pelo ODBC:

# Token para o driver ODBC
token_bytes = token.token.encode("utf-16-le")
token_struct = (
    len(token_bytes).to_bytes(4, byteorder="little")
    + token_bytes
)

# String de conexão:
connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

SQL_COPT_SS_ACCESS_TOKEN = 1256

# Conexão à Managed Instance:
print("Conectando à Azure SQL Managed Instance...")
conn = pyodbc.connect(
    connection_string,
    attrs_before={
        SQL_COPT_SS_ACCESS_TOKEN: token_struct
    }
)
print("Conexão realizada com sucesso!")
print()
cursor = conn.cursor()
# Consulta o status dos RESTOREs em execução

query = """
SELECT
    r.session_id,
    r.command,
    r.status,
    r.percent_complete,
    r.start_time,
    r.total_elapsed_time / 1000.0 / 60.0 AS minutos_decorridos,
    r.estimated_completion_time / 1000.0 / 60.0 AS minutos_restantes,
    r.wait_type,
    r.wait_time / 1000.0 AS segundos_esperando
FROM sys.dm_exec_requests AS r
WHERE r.command LIKE 'RESTORE%';
"""

cursor.execute(query)

rows = cursor.fetchall()

# Exibir os resultados:

if not rows:
    print("\n Nenhum RESTORE está sendo executado neste momento.")
else:
    print("\n RESTORE em execução:\n")

    for row in rows:
        print(f"Session ID:              {row.session_id}")
        print(f"Comando:                 {row.command}")
        print(f"Status:                  {row.status}")
        print(f"Progresso:               {row.percent_complete:.2f}%")
        print(f"Início:                  {row.start_time}")
        print(f"Tempo decorrido:         {row.minutos_decorridos:.2f} min")
        print(f"Tempo restante estimado: {row.minutos_restantes:.2f} min")
        print(f"Wait type:               {row.wait_type}")
        print(f"Wait time:               {row.segundos_esperando:.2f} s")
        print("-" * 50)

# Fechar a sessão:
cursor.close()
conn.close()
print()
print("Conexão encerrada.")