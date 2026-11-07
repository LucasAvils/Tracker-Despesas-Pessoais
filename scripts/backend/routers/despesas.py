from fastapi import FastAPI, Depends, Query, HTTPException, APIRouter
from ..schemas import *
from typing import List, Optional
from .. import dbconnect

# Roteador com prefixo '/despesas' e agrupamento para o Swagger
router = APIRouter(prefix="/despesas", tags=["Despesas"])



# Listar despesas com filtros opcionais de ano e mês
@router.get("/", response_model=List[DespesasResponse])
def listar_despesas(ano: Optional[int] = None, mes: Optional[int] = Query(None, ge=1, le=12), db=Depends(dbconnect.get_db)):
    cursor = db.cursor()
    query = "SELECT * FROM despesas WHERE 1=1"
    params = []

    # Aplicação de filtros dinâmicos
    if ano:
        query += " AND strftime('%Y',data) = ?"
        params.append(str(ano))

    if mes:
        query += " AND strftime('%m', data) = ?"
        params.append(f"{mes:02d}")

    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]

# Cadastrar nova despesa
@router.post("/", response_model=DespesasCreate, status_code=201)
def criar_despesas(despesa: DespesasCreate, db=Depends(dbconnect.get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO despesas (data,valor, descricao,forma_pagamento_id, categoria_id) VALUES (?,?,?,?,?)",
        (despesa.data, despesa.valor, despesa.descricao, despesa.forma_pagamento_id, despesa.categoria_id)
    )
    db.commit()
    return {"id": cursor.lastrowid, **despesa.model_dump()}

# Deletar despesa por ID
@router.delete("/{id}")
def deletar_despesas(id: int, db=Depends(dbconnect.get_db)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM despesas WHERE id = ?", (id,))

    # Valida se o registro existia antes de confirmar a exclusão
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    else:
        db.commit()
        return {"mensagem": "Despesa deletada com sucesso"}
