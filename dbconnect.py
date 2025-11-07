import sqlite3
import pandas as pd

def connect_db():
    conn =  sqlite3.connect('database/despesas-pessoais')
    return conn

def create_table_despesas(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS despesas (
                        data TEXT NOT NULL,
                        valor REAL NOT NULL,
                        modo_pagamento TEXT NOT NULL,
                        descricao_pagamento TEXT NOT NULL,
                        categoria TEXT NOT NULL
                    )''')
    cursor.connection.commit()

def insert_despesa(cursor, data, valor, modo_pagamento, descricao_pagamento, categoria):
    cursor.execute('''
    INSERT INTO despesas (data, valor, modo_pagamento, descricao_pagamento, categoria)
    VALUES (?, ?, ?, ?, ?)
                ''', (data, valor, modo_pagamento, descricao_pagamento, categoria))

    cursor.connection.commit()

def fetch_despesas(cursor):
    cursor.execute('SELECT * FROM despesas')
    return cursor.fetchall()

def fetch_meta(cursor):
    cursor.execute('SELECT * FROM meta')
    return cursor.fetchall()

def close_connection(cursor):
    cursor.connection.close()

def pandas_query(query):
    conn =  sqlite3.connect('database/despesas-pessoais')
    return pd.read_sql_query(query, conn)

def get_cursor(conn):
    return conn.cursor()

if __name__ == '__main__':
    conn = connect_db()
    cursor = get_cursor()
    create_table_despesas(cursor)
    insert_despesa(cursor, '2024-06-01', 100.0, 'Cartão de Crédito', 'Compra no supermercado', 'Alimentação')
    close_connection(cursor)
    print(fetch_despesas(cursor))
    