from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import despesas

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

