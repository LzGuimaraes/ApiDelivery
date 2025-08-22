from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies import pegar_sessao
from schemas import PedidoSchema
from models import Pedido

order_router = APIRouter(prefix="/pedidos", tags=["auth"])

@order_router.get("/")
async def pedidos():
    return {"Rota pedidos"}


@order_router.post("/pedido")
async def criar_pedidos(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    novo_pedido = Pedido(usuario=PedidoSchema.id_usuario)
    session.add(novo_pedido)
    session.commit()
    return{"mensagem": f"Pedido criado com sucesso. ID do pedido: {novo_pedido.id}"}


