import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# Carrega variáveis de ambiente
load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database='ans_database',
            charset='utf8mb4'
        )
        return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

def criar_pasta_resultados():
    """Cria a pasta resultados se não existir"""
    if not os.path.exists('resultados'):
        os.makedirs('resultados')
        print("Pasta 'resultados' criada com sucesso")

def exportar_resultado(df, nome_relatorio, formato='ambos'):
    """
    Exporta resultados para CSV e/ou Excel
    Formatos possíveis: 'csv', 'excel', 'ambos'
    """
    if df.empty:
        print(f"Nada para exportar em {nome_relatorio}")
        return
    
    criar_pasta_resultados()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_base = f"{nome_relatorio}_{timestamp}"
    
    if formato in ('csv', 'ambos'):
        csv_path = os.path.join('resultados', f"{nome_base}.csv")
        df.to_csv(csv_path, index=False, sep=';', decimal=',', encoding='utf-8-sig')
        print(f"Arquivo CSV salvo: {csv_path}")
    
    if formato in ('excel', 'ambos'):
        excel_path = os.path.join('resultados', f"{nome_base}.xlsx")
        df.to_excel(excel_path, index=False)
        print(f"Arquivo Excel salvo: {excel_path}")

def get_anos_disponiveis():
    """Retorna lista de anos com dados disponíveis ordenados do mais recente"""
    connection = get_db_connection()
    if connection is None:
        return []
    
    try:
        query = """
        SELECT DISTINCT YEAR(data) as ano 
        FROM demonstracoes_contabeis 
        ORDER BY ano DESC
        """
        cursor = connection.cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]
    except Error as e:
        print(f"Erro ao obter anos disponíveis: {e}")
        return []
    finally:
        if connection.is_connected():
            connection.close()

def identificar_descricoes_saude():
    """Identifica as descrições relacionadas a saúde existentes no banco"""
    connection = get_db_connection()
    if connection is None:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT DISTINCT descricao, cd_conta_contabil
        FROM demonstracoes_contabeis
        WHERE descricao LIKE '%SAÚDE%' 
           OR descricao LIKE '%SINISTRO%'
           OR descricao LIKE '%ASSISTÊNCIA%'
           OR cd_conta_contabil IN ('31111', '31112')
        LIMIT 20;
        """
        
        df = pd.read_sql(query, connection)
        if not df.empty:
            print("\nDescrições relacionadas a saúde encontradas:")
            print(df.to_string(index=False))
            exportar_resultado(df, "descricoes_saude")
        return df
    except Error as e:
        print(f"Erro ao identificar descrições: {e}")
        return pd.DataFrame()
    finally:
        if connection.is_connected():
            connection.close()

def consulta_saude_generica(periodo, intervalo):
    """Consulta genérica para despesas em saúde"""
    connection = get_db_connection()
    if connection is None:
        return pd.DataFrame()
    
    try:
        # Filtro abrangente
        query = f"""
        SELECT 
            o.razao_social,
            o.nome_fantasia,
            ABS(SUM(d.vl_saldo_final)) as total_despesas,
            COUNT(*) as qtd_registros,
            MAX(d.descricao) as descricao_exemplo,
            '{periodo}' as periodo
        FROM 
            demonstracoes_contabeis d
        JOIN 
            operadoras o ON d.registro_ans = o.registro_ans
        WHERE 
            (d.descricao LIKE '%SAÚDE%'
            OR d.descricao LIKE '%SINISTRO%'
            OR d.descricao LIKE '%ASSISTÊNCIA%'
            OR d.cd_conta_contabil IN ('31111', '31112'))
            AND d.data >= DATE_SUB((SELECT MAX(data) FROM demonstracoes_contabeis), INTERVAL {intervalo})
        GROUP BY 
            o.razao_social, o.nome_fantasia
        ORDER BY 
            total_despesas DESC
        LIMIT 10;
        """
        
        df = pd.read_sql(query, connection)
        if df.empty:
            print(f"\nNenhum resultado encontrado para o último {periodo}.")
        else:
            print(f"\nTop 10 Operadoras - Maiores Despesas em Saúde ({periodo}):")
            print(df.to_string(index=False))
            exportar_resultado(df, f"top10_{periodo}")
        
        return df
    except Error as e:
        print(f"Erro na consulta: {e}")
        return pd.DataFrame()
    finally:
        if connection.is_connected():
            connection.close()

def top_10_operadoras_ultimo_trimestre():
    """Consulta para o último trimestre"""
    return consulta_saude_generica("trimestre", "3 MONTH")

def top_10_operadoras_ultimo_ano():
    """Consulta para o último ano"""
    return consulta_saude_generica("ano", "12 MONTH")

def relatorio_anual_completo():
    """Gera relatório completo por ano"""
    anos = get_anos_disponiveis()
    if not anos:
        print("Nenhum dado anual encontrado no banco de dados")
        return
    
    print("\nRELATÓRIO ANUAL DE DESPESAS EM SAÚDE")
    print("===================================")
    
    resultados_anuais = pd.DataFrame()
    
    for ano in sorted(anos, reverse=True):
        connection = get_db_connection()
        if connection is None:
            continue
            
        try:
            query = f"""
            SELECT 
                o.razao_social,
                o.nome_fantasia,
                ABS(SUM(d.vl_saldo_final)) as total_despesas,
                COUNT(*) as qtd_registros,
                MAX(d.descricao) as descricao_exemplo,
                {ano} as ano
            FROM 
                demonstracoes_contabeis d
            JOIN 
                operadoras o ON d.registro_ans = o.registro_ans
            WHERE 
                (d.descricao LIKE '%SAÚDE%'
                OR d.descricao LIKE '%SINISTRO%'
                OR d.descricao LIKE '%ASSISTÊNCIA%'
                OR d.cd_conta_contabil IN ('31111', '31112'))
                AND YEAR(d.data) = {ano}
            GROUP BY 
                o.razao_social, o.nome_fantasia
            ORDER BY 
                total_despesas DESC
            LIMIT 10;
            """
            
            df = pd.read_sql(query, connection)
            if df.empty:
                print(f"\nNenhum resultado encontrado para {ano}.")
            else:
                print(f"\nTop 10 Operadoras em {ano}:")
                print(df.to_string(index=False))
                resultados_anuais = pd.concat([resultados_anuais, df])
                
        except Error as e:
            print(f"Erro para {ano}: {e}")
        finally:
            if connection.is_connected():
                connection.close()
    
    if not resultados_anuais.empty:
        exportar_resultado(resultados_anuais, "relatorio_anual_completo")

if __name__ == "__main__":
    # Exibe informações diagnósticas primeiro
    print("=== DIAGNÓSTICO INICIAL ===")
    descricoes = identificar_descricoes_saude()
    
    # Gera relatórios
    print("\n=== RELATÓRIOS ===")
    relatorio_anual_completo()
    
    print("\n=== ÚLTIMO TRIMESTRE ===")
    top_10_operadoras_ultimo_trimestre()
    
    print("\n=== ÚLTIMO ANO ===")
    top_10_operadoras_ultimo_ano()