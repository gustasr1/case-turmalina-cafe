# Rede Turmalina Café

Este repositório contém o protótipo funcional desenhado para a priorização de intervenções semanais da Rede Turmalina Café. A solução é composta por um pipeline de higienização de dados em Python e um painel interativo no Power BI.

## Como executar o protótipo a partir dos arquivos originais

Para reproduzir o sistema em sua máquina, siga rigorosamente os 4 passos abaixo:

### 1. Pré-requisitos e Ambiente
* Ter o **Python 3.8+** e o **Power BI Desktop** instalados.
* Abra o terminal na raiz do projeto e instale as bibliotecas necessárias:
```bash
  pip install -r requirements.txt
```

### 2. Processamento e Limpeza (ETL)
Abra o seu terminal, navegue até a pasta do código-fonte e execute o script de tratamento:
```bash
cd src
python etl.py
```

### 4. Abertura e Conexão do Painel (Power BI)
- Navegue até a pasta dashboard/ e abra o arquivo café_turmalina_dashboard.pbix.
- Ajuste de Caminho Local: Como o Power BI mapeia diretórios locais, você precisará apontar o arquivo para a sua pasta de dados tratados.
- No menu superior do Power BI, clique em Página Inicial > Transformar Dados > Configurações da Fonte de Dados.
- Clique em Alterar Fonte e selecione o caminho da pasta data/02_processed/ no seu computador.
- Clique em Atualizar e o painel carregará os visuais para a tomada de decisão.
