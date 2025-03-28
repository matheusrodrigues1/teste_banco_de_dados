import mysql.connector
from mysql.connector import Error
import pandas as pd
import os
from dotenv import load_dotenv
import csv

# Carrega variáveis de ambiente
load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database='ans_database'
        )
        return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

def import_operadoras():
    connection = get_db_connection()
    if connection is None:
        return
    
    cursor = connection.cursor()
    
    try:
        # Lê o arquivo CSV com encoding correto
        file_path = os.path.join('data', 'Relatorio_cadop.csv')
        df = pd.read_csv(file_path, sep=';', encoding='latin1')
        
        # Limpa os dados e prepara para inserção
        df = df.where(pd.notnull(df), None)
        
        # Insere os dados na tabela
        for _, row in df.iterrows():
            cursor.execute("""
            INSERT INTO operadoras (
                registro_ans, cnpj, razao_social, nome_fantasia, modalidade,
                logradouro, numero, complemento, bairro, cidade, uf, cep, ddd,
                telefone, fax, endereco_eletronico, representante, cargo_representante,
                regiao_comercializacao, data_registro_ans
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, tuple(row))
        
        connection.commit()
        print(f"Dados de operadoras importados com sucesso! {len(df)} registros inseridos.")
        
    except Error as e:
        print(f"Erro ao importar dados de operadoras: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def import_demonstracoes(arquivo):
    connection = get_db_connection()
    if connection is None:
        return
    
    cursor = connection.cursor()
    
    try:
         # 1. Desativa as verificações de FK temporariamente
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        file_path = os.path.join('data', arquivo)
        print(f"\nImportando {arquivo}...")
        
        # Le o CSV mantendo os nomes originais das colunas
        df = pd.read_csv(
            file_path,
            sep=';',
            encoding='latin1',
            decimal=',',
            thousands='.'
        )
        
        # Renomeia as colunas para o formato esperado
        df = df.rename(columns={
            'REG_ANS': 'registro_ans',
            'CD_CONTA_CONTABIL': 'cd_conta_contabil',
            'DESCRICAO': 'descricao',
            'VL_SALDO_INICIAL': 'vl_saldo_inicial',
            'VL_SALDO_FINAL': 'vl_saldo_final',
            'DATA': 'data'
        })
        
        print("Colunas após renomeação:", df.columns.tolist())
        
        # Converte a data
        try:
            df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y').dt.date
        except ValueError:
            df['data'] = pd.to_datetime(df['data']).dt.date
        
        # Converte valores numéricos
        for col in ['vl_saldo_inicial', 'vl_saldo_final']:
            if df[col].dtype == object:
                df[col] = (
                    df[col].astype(str)
                    .str.replace('.', '', regex=False)
                    .str.replace(',', '.', regex=False)
                )
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove linhas com valores essenciais faltantes
        df = df.dropna(subset=['data', 'registro_ans', 'vl_saldo_final'])
        
        print(f"Registros válidos encontrados: {len(df)}")
        
        # Insere os dados
        for _, row in df.iterrows():
            cursor.execute("""
            INSERT INTO demonstracoes_contabeis 
            (data, registro_ans, cd_conta_contabil, descricao, vl_saldo_inicial, vl_saldo_final)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                row['data'],
                str(row['registro_ans']).strip(),  # Remove espaços e converte para string
                str(row['cd_conta_contabil']).strip() if pd.notnull(row['cd_conta_contabil']) else None,
                row['descricao'],
                row['vl_saldo_inicial'],
                row['vl_saldo_final']
            ))
        
        connection.commit()
        print(f"✅ {len(df)} registros importados com sucesso de {arquivo}")

        # 2. Remove registros sem operadora correspondente
        cursor.execute("""
        DELETE FROM demonstracoes_contabeis 
        WHERE registro_ans NOT IN (SELECT registro_ans FROM operadoras)
        """)
        print(f"Registros removidos por falta de operadora: {cursor.rowcount}")
        
        # 3. Adiciona a constraint apenas se não existir
        cursor.execute("""
        SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS 
        WHERE CONSTRAINT_SCHEMA = DATABASE() 
        AND TABLE_NAME = 'demonstracoes_contabeis'
        AND CONSTRAINT_NAME = 'fk_operadora'
        """)
        
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
            ALTER TABLE demonstracoes_contabeis
            ADD CONSTRAINT fk_operadora
            FOREIGN KEY (registro_ans) REFERENCES operadoras(registro_ans)
            """)
            print("✅ Restrição de chave estrangeira adicionada com sucesso")
        else:
            print("ℹ️ Restrição de chave estrangeira já existe")
        
        connection.commit()
        
    except Exception as e:
        connection.rollback()
        print(f"❌ Erro durante importação: {str(e)}")
    finally:
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        if connection.is_connected():
            cursor.close()
            connection.close()

def verificar_operadoras_faltantes():
    connection = get_db_connection()
    if connection is None:
        return
    
    try:
        cursor = connection.cursor()
        
        # Encontra operadoras faltantes
        cursor.execute("""
        SELECT DISTINCT d.registro_ans 
        FROM demonstracoes_contabeis d
        LEFT JOIN operadoras o ON d.registro_ans = o.registro_ans
        WHERE o.registro_ans IS NULL
        LIMIT 10
        """)
        
        faltantes = cursor.fetchall()
        if faltantes:
            print("\nOperadoras referenciadas mas não cadastradas:")
            for reg in faltantes:
                print(reg[0])
        else:
            print("✅ Todas as operadoras referenciadas existem no cadastro")
            
    except Error as e:
        print(f"Erro ao verificar operadoras: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def verificar_arquivo_csv(arquivo):
    file_path = os.path.join('data', arquivo)
    try:
        df = pd.read_csv(file_path, sep=';', encoding='latin1', nrows=5)
        print(f"\nVerificação do arquivo {arquivo}:")
        print("Colunas encontradas:", df.columns.tolist())
        print("Amostra de dados:")
        print(df)
        print("\nTipos de dados:")
        print(df.dtypes)
        return True
    except Exception as e:
        print(f"Erro ao verificar arquivo {arquivo}: {str(e)}")
        return False

# Função principal:
if __name__ == "__main__":
    # Verifica os arquivos primeiro
    verificar_arquivo_csv('3T2023.csv')
    verificar_arquivo_csv('3T2024.csv')
    
    # Depois importa os dados
    import_operadoras()
    import_demonstracoes('3T2023.csv')
    import_demonstracoes('3T2024.csv')