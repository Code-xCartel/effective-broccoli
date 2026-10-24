import ast
from pathlib import Path

import pytest

FORBIDDEN = {"asyncio", "socket", "sqlite3", "curses", "json"}
DOMAIN = Path(__file__).parent.parent / "src" / "effective_broccoli" / "domain"


@pytest.mark.parametrize("path", sorted(DOMAIN.rglob("*.py")), ids=lambda p: p.name)
def test_domain_stays_pure(path):
    tree = ast.parse(path.read_text())
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not imported & FORBIDDEN, f"{path.name} reaches for {imported & FORBIDDEN}"
