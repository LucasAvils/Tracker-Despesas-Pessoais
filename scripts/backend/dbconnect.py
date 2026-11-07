import sqlite3
from pathlib import Path
import pandas as pd

# Diretório raiz do projeto e caminho do banco de dados SQLite
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "database" / "despesas-pessoais"

ddl_script = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS "categoria" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"nome" TEXT NOT NULL UNIQUE,
	"meta_gastos" REAL
);

CREATE TABLE IF NOT EXISTS "forma_pagamento" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"nome" TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS "metas" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"nome" TEXT NOT NULL,
	"valor_alvo" REAL NOT NULL,
	"valor_atual" REAL NOT NULL DEFAULT 0.0,
	"data_limite" DATE
);

CREATE TABLE IF NOT EXISTS "gastos_mensais" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"nome" TEXT NOT NULL,
	"valor_estimado" REAL NOT NULL,
	"dia_vencimento" INTEGER CHECK("dia_vencimento" BETWEEN 1 AND 31),
	"categoria_id" INTEGER NOT NULL,
	"forma_pagamento_id" INTEGER NOT NULL,
	FOREIGN KEY ("categoria_id") REFERENCES "categoria"("id") 
		ON UPDATE CASCADE ON DELETE RESTRICT,
	FOREIGN KEY ("forma_pagamento_id") REFERENCES "forma_pagamento"("id") 
		ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS "renda" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"descricao" TEXT NOT NULL,
	"valor" REAL NOT NULL,
	"data" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "despesas" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"data" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"valor" REAL NOT NULL,
	"descricao" TEXT,
	"forma_pagamento_id" INTEGER NOT NULL,
	"categoria_id" INTEGER NOT NULL,
	FOREIGN KEY ("categoria_id") REFERENCES "categoria"("id") 
		ON UPDATE CASCADE ON DELETE RESTRICT,
	FOREIGN KEY ("forma_pagamento_id") REFERENCES "forma_pagamento"("id") 
		ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS "idx_despesas_data" ON "despesas"("data");
CREATE INDEX IF NOT EXISTS "idx_despesas_categoria" ON "despesas"("categoria_id");
CREATE INDEX IF NOT EXISTS "idx_renda_data" ON "renda"("data");
"""

def get_db(db_path=DB_PATH):
    conn = connect_db()
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def connect_db(db_path=DB_PATH):
    # Assegura que o diretório database exista
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

def create_tables(cursor_or_conn):
    if isinstance(cursor_or_conn, sqlite3.Connection):
        cursor = cursor_or_conn.cursor()
    else:
        cursor = cursor_or_conn
    cursor.executescript(ddl_script)
    cursor.connection.commit()

def get_or_create_categoria(cursor, nome, meta_gastos=None):
    cursor.execute("SELECT id FROM categoria WHERE nome = ?", (nome,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO categoria (nome, meta_gastos) VALUES (?, ?)", (nome, meta_gastos))
    cursor.connection.commit()
    return cursor.lastrowid

def get_or_create_forma_pagamento(cursor, nome):
    cursor.execute("SELECT id FROM forma_pagamento WHERE nome = ?", (nome,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO forma_pagamento (nome) VALUES (?)", (nome,))
    cursor.connection.commit()
    return cursor.lastrowid

def insert_despesa(cursor, data, valor, descricao, forma_pagamento_id, categoria_id):
    cursor.execute('''
        INSERT INTO despesas (data, valor, descricao, forma_pagamento_id, categoria_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (data, valor, descricao, forma_pagamento_id, categoria_id))
    cursor.connection.commit()
    return cursor.lastrowid

def fetch_despesas(cursor, limit=100):
    query = """
        SELECT d.id, d.data, d.valor, d.descricao, f.nome AS forma_pagamento, c.nome AS categoria
        FROM despesas d
        JOIN forma_pagamento f ON d.forma_pagamento_id = f.id
        JOIN categoria c ON d.categoria_id = c.id
        ORDER BY d.data DESC
        LIMIT ?
    """
    cursor.execute(query, (limit,))
    return cursor.fetchall()

def fetch_metas(cursor):
    cursor.execute('SELECT * FROM metas')
    return cursor.fetchall()

def close_connection(cursor_or_conn):
    if isinstance(cursor_or_conn, sqlite3.Connection):
        cursor_or_conn.close()
    else:
        cursor_or_conn.connection.close()

def pandas_query(query, conn=None):
    close_after = False
    if conn is None:
        conn = connect_db()
        close_after = True
    df = pd.read_sql_query(query, conn)
    if close_after:
        conn.close()
    return df

def get_cursor(conn):
    return conn.cursor()

if __name__ == '__main__':
    conn = connect_db()
    cursor = get_cursor(conn)
    create_tables(cursor)
    cat_id = get_or_create_categoria(cursor, 'Alimentação')
    fp_id = get_or_create_forma_pagamento(cursor, 'Cartão de Crédito')
    insert_despesa(cursor, '2024-06-01', 100.0, 'Compra no supermercado', fp_id, cat_id)
    print("Despesas cadastradas no teste:")
    for row in fetch_despesas(cursor, limit=5):
        print(row)
    close_connection(cursor)
