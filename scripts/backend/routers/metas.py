from fastapi import FastAPI, Depends, Query, HTTPException, APIRouter
from ..schemas import *
from typing import List, Optional
from .. import dbconnect

# Roteador com prefixo '/metas' e agrupamento para o Swagger
router = APIRouter(prefix="/metas", tags=["Metas"])

@router.get("/", response_model=MetasResponse)
def listar_metas(db=Depends(dbconnect.get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM metas")
    return [dict(row) for row in cursor.fetchall()]

@router.post("/", status_code=201)
def criar_despesas(Meta: MetasCreate, db=Depends(dbconnect.get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO metas (nome,valor_alvo, valor_atual, data_limte) VALUES (?,?,?,?)",
        (Meta.nome, Meta.valor_alvo, Meta.valor_atual, Meta.data_limite)
    )
    db.commit()
    return {"id": cursor.lastrowid, **Meta.model_dump()}

@router.post("/{id}")
def alterar_valor(id:int,valor:float,db = Depends(dbconnect.get_db)):
    cursor = db.cursor()
    cursor.execute("UPDATE metas SET valor_atual = ? WHERE id = ?",(valor, id))

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    else:
        db.commit()
        return {"mensagem": "Categoria alterada com sucesso"}


@router.delete("/{id}")
def deletar_meta(id: int, db=Depends(dbconnect.get_db)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM metas WHERE id = ?", (id,))

    # Valida se o registro existia antes de confirmar a exclusão
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    else:
        db.commit()
        return {"mensagem": "Meta deletada com sucesso"}
