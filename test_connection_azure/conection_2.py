import os
import struct
# O struct permite converter dados para uma estrutura binária específica.
import pyodbc
from azure.identity import InteractiveBrowserCredential
# Essa biblioteca permite que o Python abra uma janela do navegador 
# para realizar a autenticação no Microsoft Entra ID. ( Via Token )
from dotenv import load_dotenv
# Biblioteca para carregar as variáveis do ambiente

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


# Autenticação Microsoft Entra ID
credential = InteractiveBrowserCredential(
     tenant_id=ID_LOCATARIO
)
#  Aqui o navegador será utilizado para autenticar sua conta no Microsoft Entra ID.
# É necessário informar o id_locatário para adquirir o token. Se não, não obtém.

# Essa linha solicita ao Microsoft Entra ID um Access Token para acessar o SQL Server/Azure SQL.
token = credential.get_token(
    "https://database.windows.net/.default"
)

token_bytes = token.token.encode("utf-16-le")
# O token originalmente é uma string. Aqui ele é convertido para bytes usando o UTF.

# Integração entre a autenticação e os drivers:
token_struct = struct.pack(
    f"<I{len(token_bytes)}s",
    len(token_bytes),
    token_bytes,
)
# O struct.pack() transforma os bytes do token em uma estrutura que o ODBC Driver consegue interpretar.

# Constante do ODBC para autenticação via Access Token
SQL_COPT_SS_ACCESS_TOKEN = 1256
# Ele é um código definido pelo driver ODBC da Microsoft para representar uma opção específica: Access Token.


# String de conexão
connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Encrypt=yes;"
# Exige que a comunicação entre Python e SQL Server seja criptografada.
# Isso é especialmente importante em uma conexão com Azure.    
    "TrustServerCertificate=no;"
# Isso evita aceitar qualquer certificado.    
)


# Testa a conexão
connection = pyodbc.connect(
    connection_string,
    attrs_before={
        SQL_COPT_SS_ACCESS_TOKEN: token_struct
    },
)


print("Conexão realizada com sucesso!")

