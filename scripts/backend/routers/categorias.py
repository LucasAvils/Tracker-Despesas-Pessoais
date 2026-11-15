from fastapi import FastAPI, Depends, HTTPException, APIRouter
from ..schemas import *
from typing import List, Optional
from .. import dbconnect


router = APIRouter(prefix="/categorias",tags=["Categorias"])

# Listar categorias
@router.get("/", response_model=List[CategoriaResponse])
def listar_categorias(db=Depends(dbconnect.get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id,nome,meta_gastos FROM categoria")
    return [dict(row) for row in cursor.fetchall()]

@router.post("/{id}")
def alterar_meta_gastos(id:int,meta_gastos:float, db=Depends(dbconnect.get_db)):
    cursor = db.cursor()
    cursor.execute("UPDATE categoria SET meta_gastos = ? WHERE id = ?",(meta_gastos, id))
    # Valida se o registro existia antes de confirmar a exclusão
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    else:
        db.commit()
        return {"mensagem": "Categoria alterada com sucesso"}