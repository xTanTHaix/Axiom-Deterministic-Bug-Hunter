"""
Test Layer 1: AST Sentinel (Tree-sitter Parsing)
"""

import pytest
from axiom.layer1.ast_sentinel import ASTSentinel


def test_ast_sentinel_init():
    """Test ASTSentinel initialization"""
    sentinel = ASTSentinel()
    assert sentinel is not None


def test_ast_sentinel_parse_simple():
    """Test parsing a simple Python expression"""
    sentinel = ASTSentinel()
    code = "x = 1 + 2"
    ast = sentinel.parsers["python"](code)
    assert ast is not None
    assert len(ast.children) > 0


def test_ast_sentinel_parse_function():
    """Test parsing a function definition"""
    sentinel = ASTSentinel()
    code = """
def greet(name):
    print(f"Hello, {name}!")
"""
    ast = sentinel.parsers["python"](code)
    assert ast is not None
    assert len(ast.children) > 0


def test_ast_sentinel_parse_class():
    """Test parsing a class definition"""
    sentinel = ASTSentinel()
    code = """
class MyClass:
    def __init__(self):
        self.value = 0
"""
    ast = sentinel.parsers["python"](code)
    assert ast is not None
    assert len(ast.children) > 0


def test_ast_sentinel_parse_import():
    """Test parsing an import statement"""
    sentinel = ASTSentinel()
    code = "import os\nfrom sys import path"
    ast = sentinel.parsers["python"](code)
    assert ast is not None
    assert len(ast.children) > 0


def test_ast_sentinel_parse_complex():
    """Test parsing a complex Python program"""
    sentinel = ASTSentinel()
    code = """
import os
from typing import List, Dict

class DataProcessor:
    def __init__(self, data: List[Dict[str, int]]):
        self.data = data
    
    def process(self) -> int:
        return sum(v for d in self.data for v in d.values())
"""
    ast = sentinel.parsers["python"](code)
    assert ast is not None
    assert len(ast.children) > 0


def test_ast_sentinel_parse_empty():
    """Test parsing empty code"""
    sentinel = ASTSentinel()
    code = ""
    ast = sentinel.parsers["python"](code)
    assert ast is not None
    assert len(ast.children) == 0


def test_ast_sentinel_parse_multiline():
    """Test parsing multiline code"""
    sentinel = ASTSentinel()
    code = """
x = 1
y = 2
z = 3
result = x + y + z
"""
    ast = sentinel.parsers["python"](code)
    assert ast is not None
    assert len(ast.children) > 0