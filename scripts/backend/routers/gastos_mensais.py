from fastapi import Depends,APIRouter,HTTPException
from ..schemas import *
from typing import List
from .. import dbconnect

router = APIRouter(prefix = "/gastos-mensais",tags=["gastos-mensais"])


#todo: add filtering to get more refined data from this function
@router.get("/", response_model=List[GastosMensaisResponse])
def listar_gastos_mensais(db=Depends(dbconnect.get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM gastos_mensais")
    return [dict(row) for row in cursor.fetchall()]

@router.post("/",response_model=GastosMensaisCreate)
def criar_gasto_mensal(gasto_mensal:GastosMensaisCreate, db=Depends(dbconnect.get_db)):
    cursor = db.cursor()
    cursor.execute("INSERT INTO gastos_mensais (nome,valor_estimado,dia_vencimento,categoria_id,forma_pagamento_id) VALUES (?,?,?,?,?)",
                   (gasto_mensal.nome,gasto_mensal.valor_estimado,gasto_mensal.dia_vencimento,gasto_mensal.categoria_id,gasto_mensal.forma_pagamento_id)
                   )
    db.commit()
    return {"id": cursor.lastrowid, **gasto_mensal.model_dump()}

@router.delete("/{id}")
def deletar_gasto_mensal(id:int, db=Depends(dbconnect.get_db)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM gastos_mensais where id = ?",(id,))

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Gasto Mensal Não encontrado")

    else:
        db.commit()
        return{"Mensagem":"Gasto mensal Deletado com sucesso."}