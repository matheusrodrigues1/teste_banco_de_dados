# Teste de Banco de Dados ANS

![Badge Status](https://img.shields.io/badge/status-conclu%C3%ADdo-brightgreen) 
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange)

Este projeto realiza a extração, transformação e análise de dados das demonstrações contábeis e cadastro de operadoras da Agência Nacional de Saúde Suplementar (ANS). O objetivo é identificar as operadoras com maiores despesas em assistência médico-hospitalar.

## 📋 Pré-requisitos

- MySQL Server 8.0 ou superior
- Python 3.8+
- Bibliotecas listadas em `requirements.txt`
- Arquivos de dados na pasta `/data`

## 🛠️ Instalação

1. Clone o repositório:
```bash
git clone https://github.com/matheusrodrigues1/teste_banco_de_dados
cd teste_banco_de_dados
```

## Configure o ambiente:
````bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
````

## Instale as dependências:

```bash
pip install -r requirements.txt
```

## Crie o arquivo .env com suas credenciais na raiz do projeto:

```bash
DB_HOST=localhost
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
```

## 🗃️ Estrutura do Projeto

teste_banco_de_dados/</br>
├── data/</br>
│   ├── Relatorio_cadop.csv&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;            # Dados cadastrais das operadoras</br>
│   ├── 3T2023.csv    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;                 # Demonstrações contábeis 2023</br>
│   └── 3T2024.csv    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;                 # Demonstrações contábeis 2024</br>
│</br>
├── scripts/</br>
│   ├── database_setup.py &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;             # Criação do banco e tabelas</br>
│   ├── data_import.py  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;             # Importação dos dados</br>
│   └── queries.py    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;                 # Consultas analíticas</br>
│</br>
├── resultados/     &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;                   # Relatórios gerados</br>
│   ├── descricoes_saude_*.{csv,xlsx}</br>
│   ├── top10_*.{csv,xlsx}</br>
│   └── relatorio_anual_*.{csv,xlsx}</br>
│</br>
├── .env        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;                       # Configurações</br>
├── requirements.txt        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;     # Dependências</br>
└── README.md       &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;                   # Documentação

## 🚀 Execução

1. Inicie o serviço do MySQL
2. Execute o pipeline completo:

```bash
# 1. Criação do banco
python scripts/database_setup.py

# 2. Importação dos dados
python scripts/data_import.py

# 3. Geração de relatórios
python scripts/queries.py
```

3. Verifique os resultados na pasta /resultados

## 📊 Exemplo de Saída

```bash
Top 10 Operadoras em 2024:
razao_social                  nome_fantasia      total_despesas  qtd_registros
---------------------------  ----------------  ---------------  -------------
UNIMED RIO BRANCO COOPERATIVA UNIMED RIO BRANCO    125,487,632.45           42
AMIL ASSISTENCIA MEDICA      AMIL                   98,754,231.12           38
...                         ...                    ...             ...
```

## Arquivos Gerados:

- resultados/top10_trimestre_20240515_143022.csv
- resultados/relatorio_anual_20240515_143022.xlsx

### Desde já agradeço a oportunidade!