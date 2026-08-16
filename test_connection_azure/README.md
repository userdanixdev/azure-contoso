# Test Connection Azure:

O arquivo `test_connection_azure.py` tem uma função importante dentro da etapa de infraestrutura: ele comprova que uma aplicação Python consegue chegar até o banco no Azure usando Microsoft Entra ID, sem utilizar usuário e senha do SQL Server.

Os Scripts Python criados são para validar a conexão com o Azure SQL Managed Instance utilizando Microsoft Entra ID e Access Token.

O arquivo `list_tables_db.py` e o `query_sql_test.py` inicia as primeiras consultas de validação do banco.


