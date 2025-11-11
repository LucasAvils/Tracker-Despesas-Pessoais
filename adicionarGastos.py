import streamlit as st
import os
import pandas as pd
import dbconnect as db



def saveData(data, valor, modoPagamento, descricaoPagamento, categoria,cursor):

    dataNovo = data.strftime('%Y/%m/%d')

    db.insert_despesa(cursor, dataNovo, valor, modoPagamento, descricaoPagamento, categoria)

    st.success("Despesa adicionada com sucesso!")

def handle_submit(data,valor,modoPagamento,descricaoPagamento,categoria):
    if data and valor and modoPagamento and descricaoPagamento and categoria:
            saveData(data, valor, modoPagamento, descricaoPagamento, categoria,cursor)
            
    else:
        st.warning("Por favor, preencha todos os campos.")

conn = db.connect_db()
cursor = db.get_cursor(conn)

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
