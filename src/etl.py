# %%
import pandas as pd
import numpy as np
import glob
import os

# %%
caminho_avaliacoes = '../data/01_raw/turmalina_avaliacoes.csv'
caminho_itens = '../data/01_raw/turmalina_itens.csv'
caminho_lojas = '../data/01_raw/turmalina_lojas.csv'
caminhos_vendas = '../data/01_raw/turmalina_vendas_diarias.csv'


df_avaliacoes = pd.read_csv(caminho_avaliacoes, sep=',')
df_itens = pd.read_csv(caminho_itens, sep=',')
df_lojas = pd.read_csv(caminho_lojas, sep=',')
df_vendas = pd.read_csv(caminhos_vendas, sep=',')

