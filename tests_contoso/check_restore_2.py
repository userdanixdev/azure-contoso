import os
import pyodbc
from azure.identity import InteractiveBrowserCredential
from dotenv import load_dotenv

load_dotenv()

SERVER = os.getenv("AZURE_SQL_SERVER_1")
ID_LOCATARIO = os.getenv("ID_LOCATARIO")
DATABASE = "master"

credential = InteractiveBrowserCredential(
    tenant_id=ID_LOCATARIO
)

print(" Autenticando no Microsoft Entra ID...")

token = credential.get_token(
    "https://database.windows.net/.default"
)

print(" Autenticação concluída.")

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

# Token para o driver ODBC
token_bytes = token.token.encode("utf-16-le")
token_struct = (
    len(token_bytes).to_bytes(4, byteorder="little")
    + token_bytes
)

SQL_COPT_SS_ACCESS_TOKEN = 1256

conn = pyodbc.connect(
    connection_string,
    attrs_before={
        SQL_COPT_SS_ACCESS_TOKEN: token_struct
    }
)

cursor = conn.cursor()

query = """
SELECT
    r.session_id,
    r.command,
    r.status,
    r.percent_complete,
    r.wait_type,
    r.wait_time,
    r.last_wait_type,
    r.wait_resource,
    r.blocking_session_id,
    t.text AS sql_text
FROM sys.dm_exec_requests r
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
WHERE r.session_id = 70;
"""

cursor.execute(query)

rows = cursor.fetchall()

if not rows:
    print("\n Nenhum RESTORE está sendo executado neste momento.")
else:
    print("\n RESTORE em execução:\n")

    for row in rows:
        print(f"Session ID:              {row.session_id}")
        print(f"Comando:                 {row.command}")
        print(f"Status:                  {row.status}")
        print(f"Progresso:               {row.percent_complete:.2f}%")                  
        print(f"Wait type:               {row.wait_type}")
        print(f"Wait time:               {row.wait_time}")
        print(f"Last wait type:          {row.last_wait_type}")
        print(f"Wait resource:           {row.wait_resource}")
        print(f"Blocking session:        {row.blocking_session_id}")
        print(f"SQL executado:           {row.sql_text}")
        
        print("-" * 50)

cursor.close()
conn.close()