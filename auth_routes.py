from fastapi import APIRouter, Depends, HTTPException
from models import Usuario, db
from dependencies import pegar_sessao
from main import bcrypt_context
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def criar_token(id_email):
    token = f"znasdnaçl{id_email}"
    return token

def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return False
    elif bcrypt_context.verify(senha, usuario.senha):
        return False
    return usuario


@auth_router.get("/")
async def autenticar():
    return {"mensagem":"Você acessou a rota padrão de autenticação", "autenticado": False}

@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="E-mail do usuário ja cadastrado")
    else:
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_criptografada, usuario_schema.ativo, usuario_schema.admin )
        session.add(novo_usuario)
        session.commit()
        return HTTPException(status_code=200, detail= f"usuario cadastrado com sucesso {usuario_schema.email}") 
    
@auth_router.post("/login")
async def login(login_schema:LoginSchema, session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session )
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario não encontrado ou credenciais invalidas")
    else:
        access_token = criar_token(usuario.id)
        return {"access_token" : access_token,
                "token_type" : "Bearer"}
        
