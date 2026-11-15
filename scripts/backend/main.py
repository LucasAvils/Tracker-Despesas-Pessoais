from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import despesas,categorias,gastos_mensais,metas,renda

# Instância principal da aplicação
app = FastAPI(title="API de Despesas Pessoais")

# Configuração de CORS: permite requisições vindas do frontend/navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro dos roteadores modulares
app.include_router(despesas.router)
app.include_router(categorias.router)
app.include_router(gastos_mensais.router)
app.include_router(metas.router)
app.include_router(renda.router)