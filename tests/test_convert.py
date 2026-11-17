import importlib
import os
import sys

import pytest
from fastapi.testclient import TestClient

from tomfastapi.cli import main
from tomfastapi.convert import convert
from tomfastapi.scan import scan

EX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "examples")


def _load(directory, module, tag):
    """Import `module` from `directory` under a private name, with the directory on sys.path."""
    sys.path.insert(0, directory)
    before = set(sys.modules)
    try:
        mod = importlib.import_module(module)
    finally:
        sys.path.remove(directory)
        for k in set(sys.modules) - before:  # forget what the project imported (name clashes between samples)
            if k.split(".")[0] in {module, "api", "config", "main", "app", "blog", "mysite"} or k == module:
                sys.modules.pop(k, None)
    return mod


def _project(path):
    ps = [p for p in scan(path) if os.path.abspath(p.path) == os.path.abspath(path)]
    assert ps, path
    return ps[0]


def test_scan_finds_all_kinds():
    kinds = {p.name: p.kind for p in scan(EX)}
    assert kinds["fastapi_app"] == "fastapi"
    assert kinds["flask_app8"] == "flask"
    assert "django" in kinds.values()


def test_fastapi_combination_same_responses(tmp_path):
    src = os.path.join(EX, "fastapi_app")
    p = _project(src)
    assert p.kind == "fastapi" and {"SQLAlchemy", "Pydantic"} <= set(p.libs)
    out = str(tmp_path / "out")
    routes, warns = convert(p, out)
    assert routes == 3 and os.path.isfile(os.path.join(out, "run_mfastapi.py"))
    orig = TestClient(_load(src, "main", "o").app)
    conv = TestClient(_load(out, "run_mfastapi", "c").app)
    seq = [("GET", "/items", None), ("POST", "/items", {"name": "a"}), ("POST", "/items", {"name": "b", "note": "x"}),
           ("POST", "/items", {}), ("GET", "/items", None), ("GET", "/items/2", None), ("GET", "/items/9", None)]
    for m, u, j in seq:
        a, b = orig.request(m, u, json=j), conv.request(m, u, json=j)
        assert (a.status_code, a.json()) == (b.status_code, b.json()), (m, u)


def test_flask_sqlalchemy_marshmallow_jwt(tmp_path):
    src = os.path.join(EX, "flask_app8")
    out = str(tmp_path / "out")
    routes, _ = convert(_project(src), out)
    assert routes >= 5
    assert "mfastapi" in open(os.path.join(out, "run_mfastapi.py")).read()
    fl = _load(src, "app", "o").app.test_client()
    fa = TestClient(_load(out, "run_mfastapi", "c").app)
    for m, u, j in [("POST", "/register", {"name": "x"}), ("POST", "/register", {"name": "ann", "password": "secret1"}),
                    ("POST", "/login", {"name": "ann", "password": "bad"})]:
        a, b = fl.open(u, method=m, json=j), fa.request(m, u, json=j)
        assert a.status_code == b.status_code and a.get_json() == b.json(), (m, u)
    ta = fl.post("/login", json={"name": "ann", "password": "secret1"}).get_json()["access_token"]
    a = fl.get("/me", headers={"Authorization": "Bearer " + ta})
    b = fa.get("/me", headers={"Authorization": "Bearer " + ta})  # a token issued by the Flask app
    assert a.status_code == b.status_code == 200 and a.get_json() == b.json()
    assert fa.get("/me").status_code == fl.get("/me").status_code == 401


def test_drf_modelviewset(tmp_path):
    src = os.path.join(EX, "drf_proj3")
    out = str(tmp_path / "out")
    os.environ["DATABASE_URL"] = "sqlite://"
    routes, _ = convert(_project(src), out)
    assert routes == 6
    fa = TestClient(_load(out, "run_mfastapi", "c").app)
    r = fa.post("/api/books/", json={"title": "Dune"})
    assert r.status_code == 201 and r.json()["pages"] == 100
    assert fa.get("/api/books/1/").json()["title"] == "Dune"
    assert fa.get("/api/books/9/").status_code == 404


def test_cli_auto(tmp_path, capsys):
    assert main(["auto", EX, "-o", str(tmp_path / "all")]) == 0
    out = capsys.readouterr().out
    assert "fastapi fastapi_app" in out and "flask flask_app8" in out
    assert os.path.isfile(str(tmp_path / "all" / "fastapi_app" / "run_mfastapi.py"))
