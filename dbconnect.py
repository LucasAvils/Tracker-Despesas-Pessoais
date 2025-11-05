import sqlite3

def connect_db():
    conn =  sqlite3.connect('database/despesas-pessoais')
    cur =  conn.cursor()
    return cur

def create_table_despesas(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS despesas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    

if __name__ == '__main__':
    cursor = connect_db()
    create_table_despesas(cursor)
    insert_despesa(cursor, '2024-06-01', 100.0, 'Cartão de Crédito', 'Compra no supermercado', 'Alimentação')
    