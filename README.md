![Azure](https://img.shields.io/badge/Microsoft%20Azure-0078D4?logo=microsoftazure&logoColor=white)
![Azure SQL](https://img.shields.io/badge/Azure%20SQL-0078D4?logo=microsoftsqlserver&logoColor=white)
![Blob Storage](https://img.shields.io/badge/Azure%20Blob%20Storage-0089D6?logo=microsoftazure&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL%20Server-CC2927?logo=microsoftsqlserver&logoColor=white)
![Azure SQL Managed Instance](https://img.shields.io/badge/Azure%20SQL%20Managed%20Instance-0078D4?logo=microsoftazure&logoColor=white)
![Microsoft Entra ID](https://img.shields.io/badge/Microsoft%20Entra%20ID-5E5E5E?logo=microsoft&logoColor=white)
![Managed Identity](https://img.shields.io/badge/Azure%20Managed%20Identity-0078D4?logo=microsoftazure&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![PyODBC](https://img.shields.io/badge/PyODBC-3776AB?logo=python&logoColor=white)
![python-dotenv](https://img.shields.io/badge/python--dotenv-3776AB?logo=python&logoColor=white)
![Microsoft ODBC Driver](https://img.shields.io/badge/Microsoft%20ODBC%20Driver%2018-CC2927?logo=microsoftsqlserver&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)

# Documentação de Configuração do Projeto: Ambiente Azure + Analytics

## Estrutura Inicial do Projeto ContosoRetailDW no Azure 


### Visão geral
---
O ponto de partida do projeto é um backup SQL Server no formato:

**ContosoRetailDW.bak**

Esse arquivo representa a base legada que será migrada para o Azure.

O processo resumido pode ser representado por:

```
SQL Server / ambiente legado
            │
            │ Backup
            ▼
   ContosoRetailDW.bak
            │
            │ Migração
            ▼
    Microsoft Azure
```

A base de dados do SQL Server existente será migrada para uma infraestrutura moderna em nuvem. Isso não significa necessariamente que o modelo de dados do ContosoRetailDW seja obsoleto. 

O banco utilizado é o ContosoRetailDW, disponibilizado pela Microsoft como dataset de demonstração. O banco é uma base legada de origem, permitindo reproduzir um cenário realista de migração de dados para uma infraestrutura moderna.

A arquitetura final utiliza:

- Azure Blob Storage para armazenamento do backup;
- Azure SQL Managed Instance como ambiente de banco de dados;
- Microsoft Entra ID para autenticação;
- Managed Identity para acesso da Managed Instance ao Storage;
- Python para conexão e consultas;
- Power BI como camada posterior de análise e visualização.

## Pré-requisitos para conexão com Azure SQL

### Microsoft ODBC Driver 18 for SQL Server

O **Microsoft ODBC Driver 18 for SQL Server** deve ser instalado diretamente no Windows.

O driver é responsável pela comunicação entre aplicações que utilizam ODBC e o SQL Server/Azure.

**Download oficial:**

[Microsoft ODBC Driver 18 for SQL Server](https://learn.microsoft.com/pt-br/sql/connect/odbc/download-odbc-driver-for-sql-server)

Para Windows 64 bits, utilizar o instalador **x64**.

> O driver ODBC é uma dependência do sistema operacional. Ele não deve ser instalado dentro do ambiente Conda nem versionado no Git.

---

## Ambiente Python

O projeto utiliza um ambiente isolado gerenciado pelo **Miniconda**.

Criar o ambiente:

```bash
conda create -n azure-contoso python=3.12
```

Ativar o ambiente:

```bash
conda activate azure-contoso
```

Instalar as dependências necessárias:

```bash
conda install pyodbc azure-identity
```

### Dependências

O `pyodbc` utiliza o driver ODBC instalado no sistema operacional, enquanto o `azure-identity` fornece os mecanismos necessários para obtenção de credenciais/tokens do Microsoft Entra ID.
Além disso o `python-dotenv` é utilizado somente dentro do ambiente, as variáveis contidas no arquivo não são versionáveis.

As dependências do ambiente devem ser registradas no arquivo:

```text
environment.yml
```

---

## Configuração de acesso ao Azure SQL

Além dos componentes locais, o Azure SQL precisa permitir a conexão do ambiente de origem.

Neste projeto, o acesso utiliza **Microsoft Entra ID** como mecanismo de autenticação.

> Credenciais, tokens e informações de autenticação não devem ser armazenados no código-fonte ou versionados no Git.

---

> O fato de o Azure SQL permitir conexões de serviços do Azure não significa necessariamente que o computador local esteja autorizado. O endereço IP utilizado pelo ambiente de desenvolvimento deve estar configurado nas regras de firewall quando houver conexão direta a partir da máquina local.

---

## Variáveis de ambiente

As informações necessárias para localizar o servidor e o banco podem ser armazenadas localmente por meio de variáveis de ambiente.

Exemplo de arquivo `.env`:

```python
ID_LOCATARIO=ed52ad5b-...
AZURE_SQL_SERVER_1=mi-contoso-retail.public...
```

Neste projeto, **não são armazenados `AZURE_SQL_USER` e `AZURE_SQL_PASSWORD`**, pois a autenticação é realizada por meio do Microsoft Entra ID.

O arquivo `.env` deve estar no `.gitignore` e **nunca deve ser enviado ao GitHub**.

> O arquivo `.env` contém configurações locais do ambiente. Não versionar informações sensíveis, tokens, senhas ou strings de conexão.

---

## Validação das dependências Python

As bibliotecas instaladas no ambiente Conda.
O ambiente deve conter, entre outras dependências do projeto:

```text
pyodbc
azure-identity
```

O arquivo `environment.yml` deve ser atualizado após alterações nas dependências:

```bash
conda env export --from-history > environment.yml
```

***O arquivo deve ser versionado no Git.***

---

## Dependências do projeto

A infraestrutura do projeto está dividida em 2 camadas principais: **ambiente local/python**  e **recursos do Azure**.

```text
Projeto Contoso Retail Analytics
│
├── Ambiente local
│   ├── Windows
│   └── Microsoft ODBC Driver 18 for SQL Server
|   └──  Conda
|          └── azure-contoso
|          ├── Python 3.12
|          ├── pyodbc
|          ├── azure-identity
|          └── python-dotenv
│
└── Microsoft Azure
    │
    ├── Microsoft Entra ID
    │   └── Autenticação e autorização
    │
    ├── Azure Blob Storage
    │   └── ContosoRetailDW.bak
    │
    ├── Azure SQL Managed Instance
    │   └── Restauração e hospedagem do banco ContosoRetailDW
    │
    └── Azure SQL Logical Server
        └── Recurso lógico utilizado na configuração do ambiente
```
## Fluxo Arquitetural do Projeto:
```
                AMBIENTE LEGADO
                       │
                       ▼
             ContosoRetailDW.bak
                       │
                       │ (Migração)
                       ▼
              Azure Blob Storage
                       │
                       │ (RESTORE)
                       ▼
          Azure SQL Managed Instance
                       │
                       ▼
                ContosoRetailDW
                       │
                       ▼
                     Python
                       │
                       ▼
                    Power BI
```

### Ambiente local

O desenvolvimento e a administração do projeto são realizados a partir de uma máquina Windows.


### Ambiente Python Isolado:

O projeto utiliza um ambiente isolado criado com **Conda**, denominado `azure-contoso`.

Principais dependências:

| Dependência        | Finalidade                                                   |
| ------------------ | ------------------------------------------------------------ |
| **Python 3.12**    | Linguagem utilizada na automação e administração do ambiente |
| **pyodbc**         | Conexão Python com SQL Server/Azure SQL                      |
| **azure-identity** | Autenticação utilizando Microsoft Entra ID                   |
| **python-dotenv**  | Carregamento de variáveis de ambiente a partir do `.env`     |

### Microsoft Entra ID

O **Microsoft Entra ID** é utilizado como mecanismo de identidade e autenticação.

A aplicação Python utiliza `InteractiveBrowserCredential`, permitindo autenticar o usuário por meio da conta Microsoft e obter um token de acesso para conexão com o SQL.

A autenticação evita a necessidade de armazenar uma senha de usuário SQL diretamente no código.

### Azure Blob Storage

O **Azure Blob Storage** funciona como área de armazenamento do backup utilizado na migração/restauração.

O arquivo:

```text
ContosoRetailDW.bak
```

é armazenado em um container do Blob Storage e utilizado como origem para a operação de `RESTORE` no Azure SQL Managed Instance.

### Azure SQL Managed Instance

O **Azure SQL Managed Instance** é o principal recurso SQL utilizado na infraestrutura atual.

Ele fornece o mecanismo SQL Server necessário para restaurar e executar o banco de dados legado:

```text
ContosoRetailDW
```

O fluxo simplificado da restauração é:

```text
ContosoRetailDW.bak
        │
        ▼
Azure Blob Storage
        │
        │ RESTORE
        ▼
Azure SQL Managed Instance
        │
        ▼
ContosoRetailDW
```

### Azure SQL Logical Server

O **Azure SQL Logical Server** é um recurso de gerenciamento associado ao Azure SQL Database. Ele não representa, por si só, um banco de dados contendo os dados do projeto.

No contexto deste projeto, sua criação fez parte da configuração inicial do ambiente Azure, mas o banco `ContosoRetailDW` utilizado no processo atual está hospedado no **Azure SQL Managed Instance**.

Portanto, a arquitetura atual deve distinguir claramente:

```text
Azure SQL Logical Server
└── Recurso lógico de gerenciamento

Azure SQL Managed Instance
└── ContosoRetailDW
```

Essa distinção é importante para evitar confundir **logical server**, **SQL Database** e **SQL Managed Instance**, que são recursos diferentes dentro do Azure.


---

### Objetivo Principal 

Migrar o banco de dados ContosoRetailDW para o Azure, utilizando uma Azure SQL Managed Instance, Azure Blob Storage e Python para conexão e consultas.

### Arquitetura:
```
Python
   │
   │ Microsoft Entra ID
   ▼
Azure SQL Managed Instance
   │
   │ Managed Identity
   ▼
Azure Blob Storage
   │
   └── ContosoRetailDW.bak
```
Após o restore:
```
Azure
│
├── Storage Account
│   └── stcontosoretaildw01
│       └── backups
│           └── ContosoRetailDW.bak
│
└── SQL Managed Instance
    └── mi-contoso-retail
        └── ContosoRetailDW
            └── ONLINE
```
## Azure SQL Managed Instance

Foi criada a Managed Instance:

`mi-contoso-retail`

**Configurações relevantes:**

```
Resource Group: ***
Estado: Ready
Public Data Endpoint: Enabled
```

**Endpoint utilizado:**

`mi-contoso-retail.public.***.database.windows.net,3342`

## Azure Blob Storage

**Foi criado o Storage Account:**

```stcontosoretaildw01```

**Container:**

`backups`

**O arquivo de backup foi carregado:**

`ContosoRetailDW.bak`

***O arquivo possui aproximadamente 629 MB.***

## Managed Identity

A Managed Instance utiliza uma System Assigned Managed Identity.

Essa identidade recebeu a permissão:

- Storage Blob Data Owner no Storage Account.

> Isso permitiu que a Managed Instance acessasse o arquivo .bak utilizando sua identidade gerenciada.

## SQL Credential

Foi criada uma credential na Managed Instance:

```SQL
CREATE CREDENTIAL
[https://stcontosoretaildw01.blob.core.windows.net/backups]
WITH IDENTITY = 'MANAGED IDENTITY';
```

## Problema encontrado:

Inicialmente, o acesso ao backup retornava:

```
Operating system error 5
Access is denied.
```

> O problema estava na configuração de rede do Storage Account.

O Storage estava configurado com:

```
Public network access: Enabled
Default action: Deny
```

## Solução:

A configuração de rede do Storage Account foi alterada para permitir o acesso necessário pela rede pública. Após a alteração, a Managed Instance conseguiu acessar o arquivo .bak.

## Validação do backup

Foi utilizado:
```SQL
RESTORE HEADERONLY
FROM URL =
'https://stcontosoretaildw01.blob.core.windows.net/backups/ContosoRetailDW.bak';
```

- Resultado:

```
Backup acessado com sucesso!
DatabaseName: ContosoRetailDW
BackupType: 1
```

> O backup estava íntegro e podia ser utilizado para restore.

## Restore do banco

Foi executado através do Python:
```SQL
RESTORE DATABASE [ContosoRetailDW]
FROM URL =
'https://stcontosoretaildw01.blob.core.windows.net/backups/ContosoRetailDW.bak';
```

- Validação:
```SQL
SELECT
    name,
    state_desc
FROM sys.databases
WHERE name = 'ContosoRetailDW';
```

- Resultado:
```
Banco:  ContosoRetailDW
Estado: ONLINE
```

## Conexão Python

A autenticação utiliza `InteractiveBrowserCredential` e `Microsoft Entra ID.`

## Estrutura Python

Foi criada uma estrutura para separar conexão e consultas:

```
azure-contoso-analytics/
│
├── database/
│   ├── connection.py
│   └── queries.py
│
├── tests_contoso/
│   ├── restore_contoso.py
│   └── restore_contoso_test.py
│
├── .env
└── .gitignore
```

## Arquivo de conexão:

O arquivo `database/connection.py` é responsável por:

- carregar as variáveis do .env;
- autenticar no Microsoft Entra ID;
- obter o Access Token;
- configurar o ODBC;
- conectar ao ContosoRetailDW.

## Arquivo de consultas:

O arquivo `database/queries.py` é responsável por executar consultas no banco e apresentar os resultados diretamente no terminal.

Exemplo:
```SQL
SELECT
    TABLE_SCHEMA,
    TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_SCHEMA, TABLE_NAME;
```

## Recuperação do banco

O arquivo `ContosoRetailDW.bak` permanece armazenado no Azure Blob Storage.

Isso fornece uma cópia de recuperação independente do banco que está atualmente na Managed Instance.

Caso seja necessário reconstruir a infraestrutura:

```
ContosoRetailDW.bak
        ↓
Azure Blob Storage
        ↓
Nova Managed Instance
        ↓
RESTORE DATABASE
        ↓
ContosoRetailDW
```

## Próximos passos

- Criar consultas SQL para explorar o ContosoRetailDW.
- Mapear tabelas e relacionamentos.
- Integrar posteriormente os dados com Power BI.


```

┌─────────────────────────────────────────────────────────────────────┐
│                         MICROSOFT AZURE                             │
│                                                                     │
│  ┌──────────────────────────┐       ┌─────────────────────────────┐ │
│  │     Azure Blob Storage   │       │ Azure SQL Managed Instance  │ │
│  │                          │       │                             │ │
│  │    stcontosoretaildw01   │       │     mi-contoso-retail       │ │
│  │                          │       │                             │ │
│  │ ┌──────────────────────┐ │       │  ┌────────────────────────┐ │ │
│  │ │ ContosoRetailDW.bak  │ │       │  │    ContosoRetailDW     │ │ │
│  │ │                      │ │       │  │                        │ │ │
│  │ │      ~629 MB           │─┼──────► │        ONLINE          │ │ │
│  │ │                      │ │RESTORE│  │                        │ │ │
│  │ └──────────────────────┘ │       │  └────────────────────────┘ │ │
│  └──────────────────────────┘       └──────────────┬──────────────┘ │
│                                                    │                │
│                         ┌──────────────────────────┘                │
│                         │                                           │
│                         ▼                                           │
│              ┌──────────────────────┐                               │
│              │   Microsoft Entra ID │                               │
│              │                      │                               │
│              │  Authentication      │                               │
│              │  + Access Token      │                               │
│              └──────────┬───────────┘                               │
└─────────────────────────┼───────────────────────────────────────────┘
                          │
                          │ HTTPS / TDS
                          │
                          ▼
              ┌──────────────────────────┐
              │     Ambiente Local       │
              │                          │
              │         Python           │
              │           │              │
              │     azure-identity       │
              │           │              │
              │         pyodbc           │
              │           │              │
              │  Microsoft ODBC Driver 18│
              └───────────┬──────────────┘
                          │
                          ▼
                     SQL Queries
                          │
                          ▼
                       PowerBi
```


## Stack do projeto:

- ☁️ Microsoft Azure - infraestrutura em nuvem
- 🗄️ Azure SQL Managed Instance - ambiente de banco de dados
- 📦 Azure Blob Storage - armazenamento do backup ContosoRetailDW.bak
- 🛢️ SQL Server - tecnologia do banco de origem/backup
- 🐍 Python - análise, manipulação, conexão e processamento dos dados
- 🔌 PyODBC - conexão Python → SQL Server
- 📊 Power BI - análise e visualização dos dados
- 🌿 Git - versionamento
- 🐙 GitHub - hospedagem do código e documentação        

*Obs: Falta estrutura do projeto tipo tree*

*Também falta o autor*

