# %%
import pandas as pd
import numpy as np
import glob
import os
import unicodedata
import re

# %%
caminho_avaliacoes = '../data/01_raw/turmalina_avaliacoes.csv'
caminho_itens = '../data/01_raw/turmalina_itens.csv'
caminho_lojas = '../data/01_raw/turmalina_lojas.csv'
caminho_vendas = '../data/01_raw/turmalina_vendas_diarias.csv'


df_avaliacoes = pd.read_csv(caminho_avaliacoes, sep=',')
df_itens = pd.read_csv(caminho_itens, sep=',')
df_lojas = pd.read_csv(caminho_lojas, sep=',')
df_vendas = pd.read_csv(caminho_vendas, sep=',')


# %%
df_lojas.info()
# %%
df_itens.info()
# %%
df_lojas.info()
# %%
df_vendas.info()
# %%
#Funções Padrões

def padronizar_id_loja(df, nome_coluna):
    coluna = df[nome_coluna].astype(str).str.upper().str.strip()
    coluna = coluna.str.replace('-', '', regex=False)
    df[nome_coluna] = coluna
    return df

def padronizar_datas(df, nome_coluna):
    df[nome_coluna] = pd.to_datetime(
            df[nome_coluna],
            format='mixed',
            dayfirst=True,
            errors='coerce'
        ).dt.normalize()
    return df

def padronizar_competencia(df, nome_coluna):
    df[nome_coluna] = pd.to_datetime(
        df[nome_coluna].astype(str).str.strip(),
        format='%Y-%m',
        errors='coerce'
    )

    return df

def padronizar_valores(df, nome_coluna):
    coluna = df[nome_coluna].astype(str)
    coluna = coluna.str.lower().str.replace('(r\$|\$|brl)', '', regex=True)
    coluna = coluna.str.strip()
    
    tem_virgula = coluna.str.contains(',', na=False)
    coluna.loc[tem_virgula] = coluna.loc[tem_virgula].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    coluna = coluna.str.replace(',', '.', regex=False)

    df[nome_coluna] = pd.to_numeric(coluna, errors='coerce')

    return df

def padronizar_texto (df, nome_coluna):
    df[nome_coluna] = df[nome_coluna].astype(str).str.lower().str.strip().str.replace(r'[^\w\s]', '', regex=True)
    df[nome_coluna] = df[nome_coluna].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

    return df

def salvar_atualizado (df_novo, caminho_saida, chave):
    if os.path.exists(caminho_saida):
        antigo = pd.read_csv(caminho_saida)

    
        colunas_data = df_novo.select_dtypes(include=['datetime64', 'datetimetz']).columns

        for col in colunas_data:
            if col in antigo.columns:
                antigo[col] = pd.to_datetime(antigo[col], errors='coerce')

        for col in chave:
            if col in antigo.columns and col not in colunas_data:
                antigo[col] = antigo[col].astype(df_novo[col].dtype)


        df_novo_copy = df_novo.copy()

        df_novo = (
        pd.concat([antigo,df_novo_copy], ignore_index=True).drop_duplicates(subset=chave, keep='last')
        )

    df_novo.to_csv(caminho_saida, index=False, date_format='%Y-%m-%d')
    print(f'Arquivo salvo com sucesso: {caminho_saida}')
# %%
#Função para limpeza do arquivo de lojas
def limpar_lojas(lojas):
    lojas['cidade_uf'] = lojas['cidade_uf'].str.upper().str.replace(r'[^\w\s]', ' ', regex=True).str.replace(r'\s+', ' ', regex=True).str.strip().str.replace(r'\bBH\b', 'BELO HORIZONTE MG', regex=True)

    lojas['formato'] = lojas['formato'].str.lower().str.strip().replace({
        'lojas de rua': 'rua',
        'shopping Center': 'shopping',
        'kiosk': 'quiosque'
    })

    lojas = padronizar_datas(lojas, 'data_abertura')

    #Retira os acentos e tranforma o resultado em letras minúsculas
    lojas['modelo'] = lojas['modelo'].apply(lambda x: unicodedata.normalize('NFKD', str(x)).encode('ASCII', 'ignore').decode('utf-8').lower().strip())

    #Usando regex para extrair apenas os números e ignorar os textos
    lojas['area_m2'] = lojas['area_m2'].astype(str).str.replace(',', '').str.extract(r'(\d+(?:\.\d+)?)')[0].astype(float)
    lojas['num_funcionarios'] = lojas['num_funcionarios'].astype(str).str.extract(r'(\d+)')[0].astype(int)
    lojas = padronizar_valores(lojas,'meta_faturamento_mensal')
    lojas['status'] = lojas['status'].astype(str).str.lower().str.strip().replace('1', 'ativa')
    
    return lojas

df_lojas_limpo = limpar_lojas(df_lojas)

#Caso os dados sejam atualizados o script empilha os dados novos com os antigos e deleta os duplicados(mantém os novos)
salvar_atualizado(df_lojas_limpo, '../data/02_processed/turmalina_lojas_tratada.csv', chave=['id_loja'])
# %%
def limpar_itens(itens):
    itens = padronizar_id_loja(itens,'id_loja')
    itens = padronizar_competencia(itens,'competencia')
    itens = padronizar_texto(itens, 'categoria')
    itens = padronizar_texto(itens, 'produto')
    itens['quantidade_vendida'] = pd.to_numeric(itens['quantidade_vendida'], errors='coerce').fillna(0)
    itens = padronizar_valores(itens, 'preco_medio')

    itens['custo_unitario'] = pd.to_numeric(itens['custo_unitario'], errors='coerce')
    itens = itens.sort_values(by=['produto', 'competencia'])
    itens['custo_unitario'] = itens.groupby('produto')['custo_unitario'].ffill()
    # Se o fill indicado pela IA não funcionar por ser o primeiro mês do produto iremos usar a média
    itens['custo_unitario'] = itens['custo_unitario'].fillna(
        itens.groupby('produto')['custo_unitario'].transform('mean')
    )

    #Retorna ordenação
    itens = itens.sort_values(by=['id_loja', 'competencia']).reset_index(drop=True)

    return itens

df_itens_limpo = limpar_itens(df_itens)

salvar_atualizado(df_itens_limpo, '../data/02_processed/turmalina_itens_tratado.csv', chave=['id_loja', 'competencia', 'produto'])
# %%
df_vendas.columns
#%%

def limpar_vendas(vendas):
    vendas = padronizar_id_loja(vendas,'id_loja')
    vendas = padronizar_datas(vendas, 'data')
    vendas = padronizar_valores(vendas,'faturamento_bruto')
    vendas = padronizar_valores(vendas,'descontos')
    vendas = padronizar_valores(vendas,'custo_insumos')
    vendas = padronizar_valores(vendas,'valor_desperdicio')
    vendas['num_tickets'] = vendas['num_tickets'].astype(str).str.extract(r'(\d+)')[0].astype(int)
    vendas['horas_trabalhadas_equipe'] = vendas['horas_trabalhadas_equipe'].astype(str).str.extract(r'(\d+)')[0].astype(float)

    return vendas

df_vendas_limpo = limpar_vendas(df_vendas)

#Caso os dados sejam atualizados o script empilha os dados novos com os antigos e deleta os duplicados(mantém os novos)
salvar_atualizado(df_vendas_limpo, '../data/02_processed/turmalina_vendas_tratada.csv', chave=['id_loja', 'data'])
#%%

def padronizar_nota(valor):
    if pd.isna(valor):
        return None
    
    val_str = str(valor).lower().strip()

    mapa_palavras = {
        'um': '1', 'dois': '2', 'três': '3', 'tres': '3', 
        'quatro': '4', 'cinco': '5'
    }

    if val_str in mapa_palavras:
        val_str = mapa_palavras[val_str]

    match = re.search(r'\d+(?:[.,]\d+)?', val_str)
    if match:
        num_str = match.group().replace(',', '.')
        return float(num_str)

    return None
    
def limpar_avaliacoes(avaliacoes):
 avaliacoes = padronizar_id_loja(avaliacoes,'id_loja',)
 avaliacoes = padronizar_datas(avaliacoes, 'data')
 avaliacoes['nota'] = avaliacoes['nota'].apply(padronizar_nota)
 avaliacoes = padronizar_texto(avaliacoes, 'canal')

 #Tratando os outlier e nulos da coluna de tempo de espera
 avaliacoes['tempo_espera_min'] = pd.to_numeric(avaliacoes['tempo_espera_min'], errors='coerce')
 avaliacoes.loc[avaliacoes['tempo_espera_min'] == 999, 'tempo_espera_min'] = np.nan
 #Mediana será utilizada devido filas ter rempo de espera puxados para cima se usar média
 mediana_espera = avaliacoes['tempo_espera_min'].median()
 avaliacoes['tempo_espera_min'] = avaliacoes["tempo_espera_min"].fillna(mediana_espera)

 avaliacoes['comentario'] = avaliacoes['comentario'].fillna('')

 return avaliacoes

df_avaliacoes_limpo = limpar_avaliacoes(df_avaliacoes)

salvar_atualizado(df_avaliacoes_limpo, '../data/02_processed/turmalina_avaliacoes_tratado.csv', chave=['id_avaliacao'])

#%%
