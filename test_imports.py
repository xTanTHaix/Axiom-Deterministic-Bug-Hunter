"""Test imports for axiom package"""

import sys

# Ensure UTF-8 stdout/stderr
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

print("Testing axiom imports...")

# Test Layer 1
print("\n1. Testing Layer 1 (AST Sentinel)...")
try:
    from axiom.layer1.ast_sentinel import ASTSentinel, Severity
    print(f"   ✅ ASTSentinel imported: {ASTSentinel}")
    print(f"   ✅ Severity enum: {Severity}")
except Exception as e:
    print(f"   ❌ Layer 1 error: {e}")
    import traceback
    traceback.print_exc()

# Test Layer 2
print("\n2. Testing Layer 2 (Slicing)...")
try:
    from axiom.layer2.slicer import CompilationFreeSlicer, CallGraph
    print(f"   ✅ CompilationFreeSlicer imported: {CompilationFreeSlicer}")
    print(f"   ✅ CallGraph imported: {CallGraph}")
except Exception as e:
    print(f"   ❌ Layer 2 error: {e}")
    import traceback
    traceback.print_exc()

# Test Layer 3
print("\n3. Testing Layer 3 (Analyzer)...")
try:
    from axiom.layer3.analyzer import StaticRuleEngine, MicroAnalyzer
    print(f"   ✅ StaticRuleEngine imported: {StaticRuleEngine}")
    print(f"   ✅ MicroAnalyzer imported: {MicroAnalyzer}")
except Exception as e:
    print(f"   ❌ Layer 3 analyzer error: {e}")
    import traceback
    traceback.print_exc()

print("\n4. Testing Layer 3 (Pattern Miner)...")
try:
    from axiom.layer3.pattern_miner.pattern_miner import PatternMiner
    print(f"   ✅ PatternMiner imported: {PatternMiner}")
except Exception as e:
    print(f"   ❌ PatternMiner error: {e}")
    import traceback
    traceback.print_exc()

print("\n5. Testing Layer 3 (Context Analyzer)...")
try:
    from axiom.layer3.context_analyzer.context_analyzer import CrossModuleAnalyzer
    print(f"   ✅ CrossModuleAnalyzer imported: {CrossModuleAnalyzer}")
except Exception as e:
    print(f"   ❌ Context Analyzer error: {e}")
    import traceback
    traceback.print_exc()

# Test Layer 4
print("\n6. Testing Layer 4 (Mock Verifier)...")
try:
    from axiom.layer4.mock_verifier import DynamicVerifier
    print(f"   ✅ DynamicVerifier imported: {DynamicVerifier}")
except Exception as e:
    print(f"   ❌ Mock Verifier error: {e}")
    import traceback
    traceback.print_exc()

print("\n7. Testing Layer 4 (Fix Generator)...")
try:
    from axiom.layer4.fix_generator import FixGenerator
    print(f"   ✅ FixGenerator imported: {FixGenerator}")
except Exception as e:
    print(f"   ❌ Fix Generator error: {e}")
    import traceback
    traceback.print_exc()

print("\n8. Testing Layer 4 (Benchmark)...")
try:
    from axiom.layer4.benchmark.benchmark import BenchmarkAnalyzer
    print(f"   ✅ BenchmarkAnalyzer imported: {BenchmarkAnalyzer}")
except Exception as e:
    print(f"   ❌ Benchmark error: {e}")
    import traceback
    traceback.print_exc()

# Test Layer 5
print("\n9. Testing Layer 5 (Audit)...")
try:
    from axiom.layer5.audit import AuditChain, MerkleChain
    print(f"   ✅ AuditChain imported: {AuditChain}")
    print(f"   ✅ MerkleChain imported: {MerkleChain}")
except Exception as e:
    print(f"   ❌ Layer 5 error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ All imports completed!")
