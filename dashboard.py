import streamlit as st
import pandas as pd
import dbconnect as db


conn = db.connect_db()
cursor = db.get_cursor(conn)

query = "SELECT data AS 'Data', valor AS 'Valor', modo_pagamento AS 'Modo de Pagamento', descricao_pagamento AS 'Descrição do Pagamento', categoria AS 'Categoria' FROM despesas"

df = db.pandas_query(query)


config = {"Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
          "Valor": st.column_config.NumberColumn("Valor", format="R$%.2f")}

mes = st.selectbox("Selecione o mês", options=["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"], index=0, key="Mes")
ano = st.number_input("Insira o ano", min_value=2000, max_value=2100, value=2024, step=1, key="Ano")

dicMesDia = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
             "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12}

months_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']


df['Data'] = pd.to_datetime(df['Data'])
df['Valor'] = pd.to_numeric(df['Valor'])

dfAno = df[df['Data'].dt.year == ano]
dfMês = dfAno[dfAno['Data'].dt.month == dicMesDia[mes]]

df['Data'] = pd.to_datetime(df['Data'])
df['Valor'] = pd.to_numeric(df['Valor'])

dfAno = df[df['Data'].dt.year == ano]
dfMês = dfAno[dfAno['Data'].dt.month == dicMesDia[mes]]


sumCategoria = dfMês.groupby('Categoria')['Valor'].sum().reset_index()


st.dataframe(dfMês,column_config=config, hide_index=True)
st.dataframe(sumCategoria,column_config=config,hide_index=True)


tab1, tab2 = st.tabs([f"Gráfico de despesas por mês em {ano}",f"Gráfico de Investimentos por mês em {ano}"])

with tab1:
    dfAno["month"] = dfAno["Data"].apply(lambda x: months_pt[x.month - 1])
    dfAno["i_month"] = dfAno["Data"].dt.month
    
    dfAno["month"] = pd.Categorical(dfAno["month"], categories=months_pt, ordered=True)

    dfAno = dfAno.sort_values(by='i_month')

    dfChart = dfAno.groupby('month')['Valor'].sum().reset_index()
    st.header("Gráfico de despesas no ano selecionado")

    st.bar_chart(dfChart, x='month', y='Valor', x_label='Mês', y_label='Valor (R$)', use_container_width=True)

with tab2:
    dfInvestimentos = dfAno[dfAno['Categoria'] == "Investimentos"]
    st.bar_chart(dfInvestimentos, x='month', y='Valor', x_label='Mês', y_label='Valor (R$)', use_container_width=True)
    dfInvestimentosSum = dfInvestimentos["Valor"].sum()
    int(dfInvestimentosSum)
    st.markdown(f"**Total Investido no ano de {ano}: R$ {dfInvestimentosSum:.2f}**")