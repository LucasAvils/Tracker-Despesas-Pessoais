import streamlit as st
import dbconnect as db
import pandas as pd

mes = "Novembro"
ano = 2024

query_meta = "SELECT categoria as 'Categoria', meta as 'Meta' FROM meta"

config_meta = {"Meta": st.column_config.NumberColumn("Meta", format="R$%.2f")}

dicMesDia = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
             "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12}

cursor = db.get_cursor(db.connect_db()) 

df_meta = db.pandas_query(query_meta)

st.dataframe(df_meta,hide_index=True,column_config=config_meta)

query_gastos = "SELECT data AS 'Data', valor AS 'Valor', modo_pagamento AS 'Modo de Pagamento', descricao_pagamento AS 'Descrição do Pagamento', categoria AS 'Categoria' FROM despesas"

df_gastos = db.pandas_query(query_gastos)

config_gastos = {"Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
          "Valor": st.column_config.NumberColumn("Valor", format="R$%.2f")}

df_gastos['Data'] = pd.to_datetime(df_gastos['Data'])
df_gastos['Valor'] = pd.to_numeric(df_gastos['Valor'])

dfAno = df_gastos[df_gastos['Data'].dt.year == ano]
dfMês = dfAno[dfAno['Data'].dt.month == dicMesDia[mes]]

df_gastos['Data'] = pd.to_datetime(df_gastos['Data'])
df_gastos['Valor'] = pd.to_numeric(df_gastos['Valor'])

dfAno = df_gastos[df_gastos['Data'].dt.year == ano]
dfMês = dfAno[dfAno['Data'].dt.month == dicMesDia[mes]]

sumCategoria = dfMês.groupby('Categoria')['Valor'].sum().reset_index()

st.dataframe(sumCategoria,column_config=config_gastos,hide_index=True)

df_meta['Categoria'] = df_meta["Categoria"].str.lower()
sumCategoria['Categoria'] = sumCategoria["Categoria"].str.lower()

df_merge = pd.merge(df_meta, sumCategoria, on="Categoria",how="outer",suffixes=('_meta','_gasto'))

df_merge['Diferença'] = df_merge['Meta'] - df_merge['Valor']

df_merge




