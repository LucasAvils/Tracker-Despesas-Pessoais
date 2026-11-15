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

class GastosMensaisResponse(BaseModel):
    id: int
    nome: str
    valor_estimado: float
    dia_vencimento: str
    categoria_id: int
    forma_pagamento_id: int

class GastosMensaisCreate(BaseModel):
    nome: str
    valor_estimado: float
    dia_vencimento: int
    categoria_id: int
    forma_pagamento_id: int

class MetasCreate(BaseModel):
    nome: str
    valor_alvo: float
    valor_atual: float
    data_limite: Optional[str] = None

class MetasResponse(BaseModel):
    id: int
    nome: str
    valor_alvo: float
    valor_atual: float
    data_limite: Optional[str] = None

class MetasCreate(BaseModel):
    nome: str
    valor_alvo: float
    valor_atual: float
    data_limite: Optional[str] = None

class RendaResponse(BaseModel):
    id: int
    descricao: str
    valor: float
    data: str

class RendaCreate(BaseModel):
    descricao: str
    valor: float
    data: str
