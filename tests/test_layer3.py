"""
Test Layer 3: Static Rule Engine
"""

import pytest
import tempfile
import os
from axiom.layer3.analyzer import StaticRuleEngine, MicroAnalyzer, MacroAnalyzer, Severity


def test_static_rule_engine_init():
    """Test StaticRuleEngine initialization"""
    engine = StaticRuleEngine()
    assert engine is not None


def test_static_rule_engine_analyze():
    """Test analyze method"""
    engine = StaticRuleEngine()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def add(a, b):\n    return a + b\n")
        f.flush()
        file_path = f.name
    try:
        result = engine.analyze_file(file_path)
        assert result is not None
        assert 'findings' in result
        assert 'total_count' in result
    finally:
        os.unlink(file_path)


def test_micro_analyzer_init():
    """Test MicroAnalyzer initialization"""
    analyzer = MicroAnalyzer()
    assert analyzer is not None


def test_micro_analyzer_analyze():
    """Test MicroAnalyzer analyze"""
    analyzer = MicroAnalyzer()
    code = """
for i in range(len(data) + 1):
    x = data[i + 1]
"""
    result = analyzer.analyze(code, "test.py")
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0


def test_macro_analyzer_init():
    """Test MacroAnalyzer initialization"""
    analyzer = MacroAnalyzer()
    assert analyzer is not None


def test_macro_analyzer_analyze():
    """Test MacroAnalyzer analyze"""
    analyzer = MacroAnalyzer()
    code = """
def process():
    file = open('test.txt')
    data = file.read()
"""
    result = analyzer.analyze(code, "test.py")
    assert result is not None
    assert isinstance(result, list)