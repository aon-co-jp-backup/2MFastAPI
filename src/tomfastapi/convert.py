"""Convert one project to MFastAPI: Flask/Django via 2FastAPI (target mfastapi), FastAPI by adding the accelerator launcher."""
from __future__ import annotations

import os
import shutil
from typing import List, Tuple

from tofastapi.scan import SKIP_DIRS, convert_project_to

from .scan import Project

LAUNCHER = """# MFastAPI: the same app with Rust route acceleration (made by 2MFastAPI).
# Run: uvicorn run_mfastapi:app --reload
from %(module)s import %(var)s as app

try:
    import mfastapi

    mfastapi.accelerate(app)  # call after all routes are registered
except ImportError:  # plain FastAPI behaviour when MFastAPI is not installed
    pass
"""
MFASTAPI_NOTE = "# MFastAPI is published as GitHub release wheels: https://github.com/aon-co-jp/MFastAPI/releases (pip install <wheel>)\n"


def _w(path: str, text: str, mode: str = "w") -> None:
    with open(path, mode, encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def convert(p: Project, out_dir: str) -> Tuple[int, List[str]]:
    os.makedirs(out_dir, exist_ok=True)
    if p.kind in ("flask", "django"):
        routes, warns = convert_project_to(p.inner, out_dir, "mfastapi")
        _w(os.path.join(out_dir, "requirements.txt"), MFASTAPI_NOTE, "a")
        return routes, warns
    # FastAPI: keep every file as-is
    for dp, dns, fns in os.walk(p.path):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.endswith(".egg-info")]
        rel = os.path.relpath(dp, p.path)
        os.makedirs(os.path.join(out_dir, rel), exist_ok=True)
        for fn in fns:
            shutil.copy2(os.path.join(dp, fn), os.path.join(out_dir, rel, fn))
    module = os.path.splitext(p.entry)[0].replace(os.sep, ".").replace("/", ".")
    _w(os.path.join(out_dir, "run_mfastapi.py"), LAUNCHER % {"module": module, "var": p.app_var})
    req = os.path.join(out_dir, "requirements.txt")
    if not os.path.isfile(req):
        _w(req, "fastapi\nuvicorn\n")
    with open(req, encoding="utf-8") as fh:
        sep = "" if fh.read().endswith("\n") else "\n"
    _w(req, sep + MFASTAPI_NOTE, "a")
    warns = []
    if p.libs:
        warns.append("libraries kept unchanged (they run on top of MFastAPI): " + ", ".join(p.libs))
    _w(os.path.join(out_dir, "CONVERSION_REPORT.md"),
       "# 2MFastAPI conversion report\n\nSource: FastAPI project `%s` (%d routes)\n\nRun `uvicorn run_mfastapi:app --reload`.\n\n## Notes\n\n%s\n" % (p.name, p.routes, "\n".join("- " + w for w in warns) or "- none"))
    return p.routes, warns
