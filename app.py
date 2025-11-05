import streamlit as st
import csv
import os
import pandas as pd

def saveData(data, valor, modoPagamento, descricaoPagamento, categoria):
    
    file_exists =  os.path.isfile("Bases/despesas.csv")

    dataNovo = data.strftime('%Y/%m/%d')

    with open("despesas.csv",mode = 'a',newline='',encoding='utf-8') as file:
        
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Data", "Valor", "Modo de Pagamento", "Descrição do Pagamento", "Categoria"])

        writer.writerow([dataNovo, valor, modoPagamento, descricaoPagamento, categoria])

    st.success("Despesa adicionada com sucesso!")

def handle_submit(data,valor,modoPagamento,descricaoPagamento,categoria):
    if data and valor and modoPagamento and descricaoPagamento and categoria:
            saveData(data, valor, modoPagamento, descricaoPagamento, categoria)
            
    else:
        st.warning("Por favor, preencha todos os campos.")

with st.form("form_despesas",clear_on_submit=True):
    st.write("Despesas")
    data = st.date_input("Selecione uma data", value="today",key="Data",format='DD/MM/YYYY')
    valor = st.number_input("Insira o valor:",format="%0.2f",value=None, key="Valor")
    modoPagamento = st.selectbox("Selecione a forma de pagamento",options=["Débito/Pix","Crédito"],index=None, key="ModoPagamento")
    descricaoPagamento = st.text_input("Descrição da despesa",key="DescricaoPagamento")
    categoria = st.selectbox("Selecione a categoria", options=["Lazer/Vontades","Necessidades","Investimentos"], index=None,key="Categoria")
    
    submitted = st.form_submit_button("Adicionar despesa")
    if submitted:
        handle_submit(data, valor, modoPagamento, descricaoPagamento, categoria)


df = pd.read_csv("despesas.csv")

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



