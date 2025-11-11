import streamlit as st
import dbconnect as db
import pandas as pd
import altair as alt
import datetime as dt

current_time =  dt.datetime.now()

current_year = current_time.year
current_month = current_time.month

st.header("Selecione o mês e o ano para visualizar a meta de gastos:")

mes = st.selectbox("Selecione o mês", options=["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"], index=(current_month-1), key="Mes")
ano = st.number_input("Insira o ano", min_value=2000, max_value=2100, value=current_year, step=1, key="Ano")

query_meta = "SELECT categoria as 'Categoria', meta as 'Meta' FROM meta"

config_meta = {"Meta": st.column_config.NumberColumn("Meta", format="R$%.2f")}

dicMesDia = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
             "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12}

cursor = db.get_cursor(db.connect_db()) 

df_meta = db.pandas_query(query_meta)

st.subheader(f'Metas de gastos cadastradas:')

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

#st.dataframe(sumCategoria,column_config=config_gastos,hide_index=True)

df_meta['Categoria'] = df_meta["Categoria"].str.lower()
sumCategoria['Categoria'] = sumCategoria["Categoria"].str.lower()

df_merge = pd.merge(df_meta, sumCategoria, on="Categoria",how="outer",suffixes=('_meta','_gasto'))

df_merge['Diferença'] = df_merge['Meta'] - df_merge['Valor']


restante = df_merge['Diferença'].sum()
st.header(f'O Valor restante para o mês de {mes} é R${restante:.2f}')

chart = (
    alt.Chart(df_merge)
    .mark_bar()
    .encode(
        x='Valor',
        y=alt.Y('Categoria', sort='-x'),
        color=alt.condition(
            alt.datum.Valor > alt.datum.Meta,
            alt.value('#bc412b'),
            alt.value('#73956f')
        ),
        tooltip=['Categoria', 'Valor', 'Meta']
    )
    .properties(height=400)
)

st.altair_chart(chart, use_container_width=True)






