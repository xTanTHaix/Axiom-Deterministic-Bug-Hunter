"""
Test Layer 2: Compilation-Free Slicing
"""

import pytest
from axiom.layer2.slicer import CompilationFreeSlicer


def test_slicer_init():
    """Test Slicer initialization"""
    slicer = CompilationFreeSlicer()
    assert slicer is not None


def test_slicer_parse_simple():
    """Test parsing a simple function"""
    slicer = CompilationFreeSlicer()
    code = """
def add(a, b):
    return a + b
"""
    result = slicer.build(code, "test.py")
    assert result is not None
    assert len(result.functions) > 0


def test_slicer_parse_multiple_functions():
    """Test parsing multiple functions"""
    slicer = CompilationFreeSlicer()
    code = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
"""
    result = slicer.build(code, "test.py")
    assert result is not None
    assert len(result.functions) == 2


def test_slicer_parse_with_classes():
    """Test parsing with classes"""
    slicer = CompilationFreeSlicer()
    code = """
class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
"""
    result = slicer.build(code, "test.py")
    assert result is not None
    assert len(result.functions) > 0


def test_slicer_parse_with_imports():
    """Test parsing with imports"""
    slicer = CompilationFreeSlicer()
    code = """
import os
from typing import List

def process(data: List[str]) -> str:
    return " ".join(data)
"""
    result = slicer.parse(code, "test.py")
    assert result is not None
    assert len(result.functions) > 0


def test_slicer_parse_empty():
    """Test parsing empty code"""
    slicer = CompilationFreeSlicer()
    code = ""
    result = slicer.build(code, "test.py")
    assert result is not None
    assert len(result.functions) == 0