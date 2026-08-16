# Database: ContosoRetailDW

`database/`

A pasta database concentra os componentes responsáveis pelo acesso e consulta ao banco ContosoRetailDW, já restaurado na Azure SQL Managed Instance.

O arquivo `connection.py` é responsável por estabelecer a conexão com o `ContosoRetailDW.`

Principais funções:

- Carrega as configurações do .env;
- Autentica no Microsoft Entra ID;
- Obtém o Access Token temporário;
- Configura a conexão utilizando pyodbc e ODBC Driver 18;
- Conecta à Azure SQL Managed Instance;
- Disponibiliza a função get_connection() para os demais módulos.

O arquivo `queries.py` é responsável pelas consultas SQL realizadas no banco. Seu objetivo é separar a lógica de consulta da lógica de conexão.

O arquivo `init.py` é responsável em transformar o database em um pacote Python.
Ele permite organizar os módulos da pasta e facilita sua utilização por outros componentes do projeto.

```
A pasta database representa, portanto, a camada de acesso ao banco de dados do projeto, enquanto os scripts de restauração (restore_header.py, restore_database.py e restore_status.py) ficam responsáveis pelo processo de migração/restauração do backup.
```