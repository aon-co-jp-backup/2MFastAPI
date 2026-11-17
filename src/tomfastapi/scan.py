"""Find Flask / Django / FastAPI projects below a directory (files are only read, never imported)."""
from __future__ import annotations

import os
import re
from dataclasses import asdict, dataclass, field
from typing import Dict, List

from tofastapi.scan import SKIP_DIRS, scan as scan_2fastapi

_FASTAPI_APP = re.compile(r"^(\w+)\s*(?::\s*[\w\[\]., ]+)?=\s*(?:\w+\.)?FastAPI\s*\(", re.M)
_ROUTE = re.compile(r"@\s*\w+\.(get|post|put|delete|patch|head|options|api_route|websocket)\s*\(")
LIBS = {
    "sqlalchemy": "SQLAlchemy", "sqlmodel": "SQLModel", "pydantic": "Pydantic", "jwt": "PyJWT", "jose": "python-jose",
    "passlib": "passlib", "alembic": "Alembic", "celery": "Celery", "redis": "Redis", "httpx": "httpx",
    "fastapi_users": "fastapi-users", "tortoise": "Tortoise ORM", "beanie": "Beanie", "motor": "Motor",
    "slowapi": "slowapi", "fastapi_cache": "fastapi-cache", "jinja2": "Jinja2", "websockets": "websockets",
}


@dataclass
class Project:
    kind: str  # flask | django | fastapi
    name: str
    path: str
    entry: str = ""  # fastapi: file that creates FastAPI(...)
    app_var: str = "app"
    routes: int = 0
    libs: List[str] = field(default_factory=list)
    inner: object = None  # tofastapi Project for flask / django

    def to_dict(self) -> Dict:
        d = asdict(self)
        d.pop("inner", None)
        return d


def _read(p: str) -> str:
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def _libs(src: str) -> List[str]:
    found = []
    for mod, label in LIBS.items():
        if re.search(r"^\s*(from|import)\s+%s\b" % re.escape(mod), src, re.M) and label not in found:
            found.append(label)
    return found


def scan_fastapi(root: str) -> List[Project]:
    root = os.path.abspath(root)
    by_dir: Dict[str, Project] = {}
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted(d for d in dns if d not in SKIP_DIRS and not d.endswith(".egg-info"))
        for fn in sorted(fns):
            if not fn.endswith(".py"):
                continue
            src = _read(os.path.join(dp, fn))
            m = _FASTAPI_APP.search(src)
            if m is None or "fastapi" not in src:
                continue
            top = dp
            while top != root and os.path.isfile(os.path.join(os.path.dirname(top), "__init__.py")):
                top = os.path.dirname(top)
            p = by_dir.setdefault(top, Project("fastapi", os.path.basename(top) or "app", top))
            if not p.entry:
                p.entry = os.path.relpath(os.path.join(dp, fn), top)
                p.app_var = m.group(1)
    for p in by_dir.values():
        for dp, dns, fns in os.walk(p.path):
            dns[:] = sorted(d for d in dns if d not in SKIP_DIRS and not d.endswith(".egg-info"))
            for fn in fns:
                if fn.endswith(".py"):
                    s = _read(os.path.join(dp, fn))
                    p.routes += len(_ROUTE.findall(s))
                    for lib in _libs(s):
                        if lib not in p.libs:
                            p.libs.append(lib)
    return sorted(by_dir.values(), key=lambda x: x.path)


def scan(root: str) -> List[Project]:
    out: List[Project] = []
    for q in scan_2fastapi(root):
        if q.kind in ("flask", "django"):
            p = Project(q.kind, q.name, q.path, q.entry, routes=q.routes)
            p.inner = q
            out.append(p)
    flask_django = [p.path for p in out]
    for p in scan_fastapi(root):
        if not any(p.path == d or p.path.startswith(d + os.sep) for d in flask_django):
            out.append(p)
    return out
