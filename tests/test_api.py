from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from coleccionable_API.database import get_db_required
from coleccionable_API.main import app


class _ListCursor:
    def __init__(self, items: list) -> None:
        self._items = items

    def sort(self, *args, **kwargs) -> "_ListCursor":
        return self

    def limit(self, n: int) -> "_ListCursor":
        self._items = self._items[:n]
        return self

    async def to_list(self, length: int) -> list:
        return self._items[:length]


class _ProductosCol:
    """Colección en memoria mínima para probar flujos HTTP."""

    def __init__(self) -> None:
        self._by_sku: dict[str, dict] = {}

    def find(self, filtro=None, *args, **kwargs) -> _ListCursor:
        if not filtro:
            rows = list(self._by_sku.values())[::-1]
            return _ListCursor(rows)
        if "$elemMatch" in str(filtro):
            em = (filtro or {}).get("atributos_especificos", {}).get("$elemMatch", {})
            k, v = em.get("k"), em.get("v")
            out = [
                d
                for d in self._by_sku.values()
                for a in d.get("atributos_especificos", [])
                if a.get("k") == k and a.get("v") == v
            ]
            return _ListCursor(out)
        return _ListCursor(list(self._by_sku.values())[::-1])

    async def find_one(
        self,
        filtro: dict,
        proyeccion: dict | None = None,
        *args: object,
        **kwargs: object,
    ) -> dict | None:
        sku = filtro.get("sku")
        if sku in self._by_sku:
            doc = dict(self._by_sku[sku])
            if proyeccion == {"_id": 0}:
                doc.pop("_id", None)
            return doc
        return None

    async def insert_one(self, documento: dict) -> MagicMock:
        sku = documento["sku"]
        self._by_sku[sku] = {**documento, "_id": "oid-test"}
        m = MagicMock()
        m.inserted_id = "oid-test"
        return m

    async def update_one(self, filtro: dict, op: dict) -> MagicMock:
        m = MagicMock()
        if filtro.get("sku") not in self._by_sku:
            m.matched_count = 0
            return m
        s = filtro["sku"]
        p = op.get("$set", {})
        self._by_sku[s] = {**self._by_sku[s], **p}
        m.matched_count = 1
        return m

    async def delete_one(self, filtro: dict) -> MagicMock:
        m = MagicMock()
        s = filtro.get("sku")
        if s in self._by_sku:
            del self._by_sku[s]
            m.deleted_count = 1
        else:
            m.deleted_count = 0
        return m

    async def count_documents(self, filtro: object) -> int:
        return len(self._by_sku)


def _build_fake_db() -> MagicMock:
    db = MagicMock()
    db.productos = _ProductosCol()
    return db


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


def test_root_ok(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "online"
    assert "docs" in data


def test_diagnostico_sin_mongo_en_tests(client: TestClient) -> None:
    r = client.get("/diagnostico")
    assert r.status_code == 200
    j = r.json()
    assert "connection" in j


def test_listar_productos_503_si_no_hay_db(client: TestClient) -> None:
    r = client.get("/productos")
    assert r.status_code == 503


def test_listar_vacio_con_db_mock() -> None:
    fake = _build_fake_db()
    app.dependency_overrides[get_db_required] = lambda: fake
    with TestClient(app) as c:
        r = c.get("/productos")
        assert r.status_code == 200
        assert r.json() == []
    app.dependency_overrides.clear()


def test_crear_y_leer_por_sku() -> None:
    fake = _build_fake_db()
    app.dependency_overrides[get_db_required] = lambda: fake
    body = {
        "sku": "T-1",
        "nombre": "Test",
        "categoria": "fig",
        "precio_clp": 1000,
        "stock_actual": 1,
        "atributos_especificos": [{"k": "color", "v": "rojo"}],
    }
    with TestClient(app) as c:
        r1 = c.post("/productos", json=body)
        assert r1.status_code == 201
        r2 = c.get("/productos/T-1")
        assert r2.status_code == 200
        data = r2.json()
        assert data["sku"] == "T-1"
        assert data["nombre"] == "Test"
    app.dependency_overrides.clear()


def test_conflicto_sku_duplicado() -> None:
    fake = _build_fake_db()
    app.dependency_overrides[get_db_required] = lambda: fake
    body = {
        "sku": "DUP",
        "nombre": "A",
        "categoria": "c",
        "precio_clp": 1,
        "stock_actual": 0,
        "atributos_especificos": [],
    }
    with TestClient(app) as c:
        assert c.post("/productos", json=body).status_code == 201
        r = c.post("/productos", json=body)
        assert r.status_code == 409
    app.dependency_overrides.clear()


def test_busqueda_por_atributo() -> None:
    fake = _build_fake_db()
    app.dependency_overrides[get_db_required] = lambda: fake
    item = {
        "sku": "A-2",
        "nombre": "x",
        "categoria": "c",
        "precio_clp": 1,
        "stock_actual": 0,
        "atributos_especificos": [{"k": "edicion", "v": "limitada"}],
    }
    with TestClient(app) as c:
        c.post("/productos", json=item)
        r = c.get("/productos/buscar/atributo", params={"clave": "edicion", "valor": "limitada"})
        assert r.status_code == 200
        arr = r.json()
        assert len(arr) == 1
    app.dependency_overrides.clear()
