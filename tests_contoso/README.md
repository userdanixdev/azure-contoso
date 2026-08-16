# Restore do ContosoRetailDW:

O arquivo `restore_contoso_test.py` tem como objetivo validar o acesso da Azure SQL Managed Instance ao backup `ContosoRetailDW.bak` armazenado no Azure Blob Storage.

Assim o script realiza as seguintes etapas:

- Carrega as configurações do ambiente através do .env;
- Autentica no Microsoft Entra ID;
- Obtém um Access Token;
- Estabelece conexão com a Azure SQL Managed Instance;
- Cria ou verifica a Credential utilizada para acesso ao Blob Storage;
- Executa RESTORE HEADERONLY;
- Verifica se o SQL Server consegue ler o arquivo .bak;
- Exibe informações do backup, como banco de origem, tipo e datas;
- Encerra corretamente a conexão com a Managed Instance.


Então, o script não restaura o banco de dados. Ele apenas solicita ao SQL Server que leia o cabeçalho do backup e retorne seus metadados. Dessa forma, o script permite confirmar que o arquivo `ContosoRetailDW.bak` está acessível e pode ser interpretado pela Azure SQL Managed Instance antes de realizar o restore definitivo.

> Após essa validação, o próximo passo é realizar o restore efetivo do ContosoRetailDW na Managed Instance e, posteriormente, iniciar a etapa de Analytics.

O arquivo `restore_status.py` monitora o status de um restore que já está sendo executado.

O script:

- Autentica no Microsoft Entra ID utilizando Access Token;
- Conecta à Azure SQL Managed Instance através do PyODBC;
- Consulta a view sys.dm_exec_requests;
- Identifica se existe algum comando RESTORE em execução;

Exibe informações como:

- Status;
- Percentual de progresso;
- Tempo decorrido;
- Tempo restante estimado;
- Tipo de espera (wait_type);
- Tempo de espera.

Ele complementa o `restore_contoso_test.py` enquanto o primeiro valida o acesso ao backup, o `restore_status.py` acompanha a execução do restore efetivo.

O arquivo `restore_database.py` exucuta a restauração do banco legado. O `restore_database.py` é responsável por executar efetivamente a restauração do banco `ContosoRetailDW` na Azure SQL Managed Instance.

Ele é executado depois da validação do arquivo `.bak` realizada pelo script de `RESTORE HEADERONLY.`

Principais responsabilidades:

- Carregar as configurações de variáveis de ambiente assim como as validações:
(Isso evita deixar configurações do ambiente diretamente no código.)
- Autenticar no Microsoft Entra ID
- Conectar à Managed Instance
- Configurar o acesso ao Blob Storage: O script cria ou verifica uma SQL Credential associada ao endereço do Blob Storage
- Executar o RESTORE: Depois de validar a Credential, o script executa a restauração.
(Essa é a etapa que efetivamente transforma o backup armazenado no Blob Storage em um banco de dados dentro da Managed Instance.)
- Verificar o banco restaurado

