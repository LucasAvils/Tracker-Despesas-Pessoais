from fastapi import FastAPI, Depends, Query, HTTPException, APIRouter
from ..schemas import *
from typing import List, Optional
from .. import dbconnect

router = APIRouter(prefix="/renda", tags=["Renda"])

@router.get("/", response_model=List[RendaResponse])
def listar_renda(ano:Optional[int] = None, mes:Optional[int] = None, db=Depends(dbconnect.get_db)):
    cursor = db.cursor()
    query = "SELECT * FROM renda WHERE 1=1"
    params = []
    if ano:
        query += " AND strftime('%Y',data) = ?"
        params.append(str(ano))

    if mes:
        query += " AND strftime('%m', data) = ?"
        params.append(f"{mes:02d}")

    cursor.execute(query,params)

    return [dict(row) for row in cursor.fetchall()]

@router.post("/", response_model=RendaCreate)
def criar_renda(renda:RendaCreate, db=Depends(dbconnect.get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO renda (descricao,valor,data) VALUES (?,?,?)",(renda.descricao,renda.valor,renda.data)
    )
    db.commit()
    return {"id": cursor.lastrowid, **renda.model_dump()}

@router.delete("/{id}")
def deletar_renda(id:int, db = Depends(dbconnect.get_db)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM renda WHERE id = ?",(id,))

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Renda não encontrada")
    else:
        db.commit()
        return {"mensagem": "Renda deletada com sucesso"}
