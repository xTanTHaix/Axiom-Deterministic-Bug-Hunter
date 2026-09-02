"""
Test imports for all axiom modules
"""

import sys

def test_import_axiom():
    """Test importing axiom package"""
    import axiom
    assert hasattr(axiom, '__version__')
    assert axiom.__version__ == '3.0.0'

def test_import_layer1():
    """Test importing layer1"""
    import axiom.layer1
    assert hasattr(axiom.layer1, 'ast_sentinel')

def test_import_layer2():
    """Test importing layer2"""
    import axiom.layer2
    assert hasattr(axiom.layer2, 'slicer')

def test_import_layer3():
    """Test importing layer3"""
    import axiom.layer3
    assert hasattr(axiom.layer3, 'analyzer')
    assert hasattr(axiom.layer3, 'pattern_miner')
    assert hasattr(axiom.layer3, 'context_analyzer')

def test_import_layer4():
    """Test importing layer4"""
    import axiom.layer4
    assert hasattr(axiom.layer4, 'mock_verifier')
    assert hasattr(axiom.layer4, 'fix_generator')
    assert hasattr(axiom.layer4, 'benchmark')

def test_import_layer5():
    """Test importing layer5"""
    import axiom.layer5
    assert hasattr(axiom.layer5, 'audit')

def test_import_cli():
    """Test importing CLI"""
    import axiom.cli
    assert hasattr(axiom.cli, 'main')

def test_import_config():
    """Test importing config"""
    from axiom.config import Config, load_config
    config = Config()
    assert config is not None

def test_import_all_layers():
    """Test importing all layers at once"""
    import axiom
    import axiom.layer1
    import axiom.layer2
    import axiom.layer3
    import axiom.layer4
    import axiom.layer5

def test_import_submodules():
    """Test importing submodules"""
    from axiom.layer1.ast_sentinel import ASTSentinel
    from axiom.layer2.slicer import CompilationFreeSlicer
    from axiom.layer3.analyzer import StaticRuleEngine
    from axiom.layer3.pattern_miner import PatternMiner
    from axiom.layer3.context_analyzer import CrossModuleAnalyzer
    from axiom.layer4.mock_verifier import DynamicVerifier
    from axiom.layer4.fix_generator import FixGenerator
    from axiom.layer4.benchmark import BenchmarkAnalyzer
    from axiom.layer5.audit import AuditChain