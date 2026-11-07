from pydantic import BaseModel
from typing import Optional

# Resposta de Categoria (leitura)
class CategoriaResponse(BaseModel):
    id: int
    nome: str
    meta_gastos: Optional[float] = None


# Resposta de Despesa (leitura com ID gerado)
class DespesasResponse(BaseModel):
    id: int
    data: str
    valor: float
    descricao: Optional[str] = None
    forma_pagamento_id: Optional[int] = None
    categoria_id: Optional[int] = None


# Payload de criação de Despesa (entrada via POST)
class DespesasCreate(BaseModel):
    data: str
    valor: float
    descricao: Optional[str] = None
    forma_pagamento_id: int
    categoria_id: int
