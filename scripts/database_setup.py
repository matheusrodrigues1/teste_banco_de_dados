import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def create_database_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=int(os.getenv('DB_PORT', '3306'))
        )
        return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

def create_database_and_tables():
    connection = create_database_connection()
    if connection is None:
        return
    
    cursor = connection.cursor()
    
    try:
        # Cria o banco de dados se não existir
        cursor.execute("CREATE DATABASE IF NOT EXISTS ans_database")
        cursor.execute("USE ans_database")
        
        # Cria tabela de operadoras
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS operadoras (
            registro_ans VARCHAR(20) PRIMARY KEY,
            cnpj VARCHAR(20),
            razao_social VARCHAR(255),
            nome_fantasia VARCHAR(255),
            modalidade VARCHAR(100),
            logradouro VARCHAR(255),
            numero VARCHAR(20),
            complemento VARCHAR(100),
            bairro VARCHAR(100),
            cidade VARCHAR(100),
            uf VARCHAR(2),
            cep VARCHAR(10),
            ddd VARCHAR(5),
            telefone VARCHAR(20),
            fax VARCHAR(20),
            endereco_eletronico VARCHAR(255),
            representante VARCHAR(255),
            cargo_representante VARCHAR(100),
            regiao_comercializacao VARCHAR(100),
            data_registro_ans DATE
        )
        """)
        
        # Cria tabela de demonstrações contábeis
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS demonstracoes_contabeis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data DATE,
            registro_ans VARCHAR(20),
            cd_conta_contabil VARCHAR(20),
            descricao VARCHAR(255),
            vl_saldo_inicial DECIMAL(15, 2),
            vl_saldo_final DECIMAL(15, 2),
            FOREIGN KEY (registro_ans) REFERENCES operadoras(registro_ans)
        )
        """)
        
        connection.commit()
        print("Banco de dados e tabelas criados com sucesso!")
        
    except Error as e:
        print(f"Erro ao criar banco de dados e tabelas: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_database_and_tables()