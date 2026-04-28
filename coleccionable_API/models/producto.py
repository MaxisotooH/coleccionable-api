from typing import Any, List

from pydantic import BaseModel


class AtributoEspecifico(BaseModel):
    k: str
    v: Any


class Producto(BaseModel):
    sku: str
    nombre: str
    categoria: str
    precio_clp: int
    stock_actual: int
    atributos_especificos: List[AtributoEspecifico]
