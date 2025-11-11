import streamlit as st
import os
import pandas as pd
import dbconnect as db

st.title("Despesas Pessoais")

st.set_page_config(page_title="Despesas Pessoais", layout="wide")

pg =  st.navigation([st.Page("dashboard.py", title="Dashboard"),st.Page("metaGastos.py",title="Meta de gastos"),st.Page("adicionarGastos.py",title="Adicionar Despesa")])
pg.run()




