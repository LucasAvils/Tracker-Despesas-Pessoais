from fastapi import FastAPI, Depends, Query, HTTPException, APIRouter
from ..schemas import *
from typing import List, Optional
from .. import dbconnect


router = APIRouter(prefix="/categorias",tags=["Categorias"])

# Listar categorias
@router.get("/categorias", response_model=List[CategoriaResponse])
def listar_categorias(db=Depends(dbconnect.get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id,nome,meta_gastos FROM categoria")
    return [dict(row) for row in cursor.fetchall()]


