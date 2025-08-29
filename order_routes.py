from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoSchema
from models import Pedido, Usuario, ItemPedido
from typing import List

order_router = APIRouter(prefix="/pedidos", tags=["auth"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def pedidos():
    return {"Rota pedidos"}


@order_router.post("/pedido")
async def criar_pedidos(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    novo_pedido = Pedido(usuario=PedidoSchema.id_usuario)
    session.add(novo_pedido)
    session.commit()
    return{"mensagem": f"Pedido criado com sucesso. ID do pedido: {novo_pedido.id}"}

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido:int,session: Session = Depends(pegar_sessao), usuario:Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first() 
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin or usuario.id != pedido.usuario:
        raise HTTPException(status_code= 401, detail="Você não pode fazer essa modificação")
    pedido.status = "CANCELADO"
    session.commit()
    return{
        "mensagem": f"Pedido número: {id_pedido} cancelado com sucesso",
        "pedido": pedido
    }

@order_router.get("/listar")
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario:Usuario = Depends(verificar_token)):
    if usuario.admin == False:
        raise HTTPException(status_code=401, detais= "voce não pode fazer essa operação")
    else:
        pedido = session.query(Pedido).all()
        return {
            "Pedidos": pedidos
        }

@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_pedido(id_pedido:int,
                            item_pedido_schema: ItemPedidoSchema,
                            session: Session = Depends(pegar_sessao), 
                            usuario:Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não existe")
    elif not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail ="Voce não tem autorização para fazer essa operação")
    item_pedido = ItemPedido(item_pedido_schema.quantidade,
                             item_pedido_schema.sabor,
                             item_pedido_schema.tamanho,
                             item_pedido_schema.preco_unitario,
                             id_pedido
                             )
    pedido.calcular_preco()
    session.add(item_pedido)
    session.commit()
    return{
        "mensagem": "Item criado com sucesso",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco
    }

@order_router.post("/pedido/remover-item/{id_item_pedido}")
async def remover_iten_pedido(id_item_pedido:int,
                            session: Session = Depends(pegar_sessao), 
                            usuario:Usuario = Depends(verificar_token)):
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id==id_item_pedido).first()
    pedido = session.query(Pedido).filter(Pedido.id ==item_pedido.pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item no pedido não existe")
    elif not usuario.admin and usuario.id != item_pedido.pedido.usuario:
        raise HTTPException(status_code=401, detail ="Voce não tem autorização para fazer essa operação")
    session.delete(item_pedido)                   
    pedido.calcular_preco()
    session.commit()
    return{
        "mensagem": "Item removido com sucesso",
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": item_pedido.pedido
    }

@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido:int,session: Session = Depends(pegar_sessao), usuario:Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first() 
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin or usuario.id != pedido.usuario:
        raise HTTPException(status_code= 401, detail="Você não pode fazer essa modificação")
    pedido.status = "FINALIZADO"
    session.commit()
    return{
        "mensagem": f"Pedido número: {id_pedido} finalizado com sucesso",
        "pedido": pedido
    }

@order_router.get("pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int,session: Session = Depends(pegar_sessao), usuario:Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    if not usuario.admin or usuario.id != pedido.usuario:
        raise HTTPException(status_code= 401, detail="Você não pode fazer essa modificação")
    return{
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
    }
    
@order_router.get("/listar/pedidos-usuario",response_model=List(ResponsePedidoSchema))
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario:Usuario = Depends(verificar_token)):
        pedidos = session.query(Pedido).filter(Pedido.usuario==usuario.id).all()
        return pedidos