import pandas as pd

from connection import get_connection


pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 40)


def listar_tabelas(connection):
    """Retorna as tabelas do banco."""

    query = """
        SELECT
            TABLE_SCHEMA,
            TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME;
    """

    return pd.read_sql(query, connection)


def analisar_tabela(connection, schema, tabela):
    """Faz uma análise básica de uma tabela."""

    nome_tabela = f"[{schema}].[{tabela}]"

    print("\n" + "=" * 100)
    print(f"TABELA: {nome_tabela}")
    print("=" * 100)

    # Carrega os dados:    

    query = f"""
        SELECT *
        FROM {nome_tabela};
    """

    df = pd.read_sql(query, connection)

    
    # Informações gerais
    
    print("\n[1] DIMENSÕES")
    print(f"Linhas : {df.shape[0]:,}")
    print(f"Colunas: {df.shape[1]:,}")

    
    # Colunas e tipos:
    print("\n[2] COLUNAS E TIPOS")

    estrutura = pd.DataFrame({
        "Coluna": df.columns,
        "Tipo": df.dtypes.astype(str).values,
        "Nulos": df.isna().sum().values,
        "% Nulos": (
            df.isna().mean().mul(100).round(2).values
        ),
        "Únicos": df.nunique().values
    })

    print(estrutura.to_string(index=False))

    # Duplicados
    print("\n[3] DUPLICADOS")

    duplicados = df.duplicated().sum()

    print(f"Registros duplicados: {duplicados:,}")

    if len(df) > 0:
        percentual = duplicados / len(df) * 100
        print(f"Percentual duplicado: {percentual:.2f}%")

    # Valores nulos
    
    print("\n[4] VALORES NULOS")

    nulos = (
        df.isna()
        .sum()
        .sort_values(ascending=False)
    )

    nulos = nulos[nulos > 0]

    if nulos.empty:
        print("Nenhum valor nulo encontrado.")

    else:
        print(nulos.to_string())

    # Estatísticas numéricas
    
    numericas = df.select_dtypes(include="number")

    if not numericas.empty:

        print("\n[5] ESTATÍSTICAS NUMÉRICAS")

        print(
            numericas.describe()
            .transpose()
            .to_string()
        )

    # Amostra
    
    print("\n[6] AMOSTRA — 5 PRIMEIROS REGISTROS")

    print(
        df.head(5)
        .to_string(index=False)
    )

    return df


def analisar_banco():

    connection = get_connection()

    try:

        print("\n" + "#" * 100)
        print("ANÁLISE DO BANCO ContosoRetailDW")
        print("#" * 100)

        
        # Lista tabelas
        
        tabelas = listar_tabelas(connection)

        print("\nTABELAS ENCONTRADAS:")
        print(tabelas.to_string(index=False))

        # Resumo das tabelas
        
        print("\n" + "=" * 100)
        print("ANÁLISE DAS TABELAS")
        print("=" * 100)

        for _, row in tabelas.iterrows():

            schema = row["TABLE_SCHEMA"]
            tabela = row["TABLE_NAME"]

            analisar_tabela(
                connection,
                schema,
                tabela
            )

    finally:

        connection.close()


if __name__ == "__main__":
    analisar_banco()