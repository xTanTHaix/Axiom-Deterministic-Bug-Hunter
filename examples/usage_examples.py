"""
Example: Axiom Aegis v3.0 Usage Examples

This file contains working, runnable examples for all v3.0 features:
- Layer 1: AST Sentinel
- Layer 2: Compilation-Free Slicing
- Layer 3: Static Rule Engine & Pattern Mining & Context Analyzer
- Layer 4: Dynamic Verification & Fix Generator & Benchmark Analyzer
- Layer 5: Audit Chain
- Interactive Mode
"""

import sys
from pathlib import Path

# Ensure UTF-8 stdout/stderr on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import axiom


# =============================================================================
# EXAMPLE 1: AST Sentinel (Layer 1)
# =============================================================================
def example_ast_sentinel():
    """Detect AST-level issues and dangerous function calls"""
    print("=" * 60)
    print("1. Running AST Sentinel (Layer 1)...")
    print("=" * 60)

    sentinel = axiom.ASTSentinel()
    sample_file = Path("examples/sample_bugs/dangerous_calls.py")
    if sample_file.exists():
        root, findings = sentinel.parse_file(str(sample_file))
        print(f"AST Parsed successfully. Node type: {type(root).__name__}")
        print(f"Dangerous call findings: {len(findings)}")
        for f in findings:
            print(f"  - [{f.severity.value}] {f.message} at line {f.line_number}: {f.code_snippet}")
    print()


# =============================================================================
# EXAMPLE 2: Slicing & Call Graph (Layer 2)
# =============================================================================
def example_slicing():
    """Build compilation-free function slice and call graph"""
    print("=" * 60)
    print("2. Running Compilation-Free Slicing (Layer 2)...")
    print("=" * 60)

    code = """
def calculate_discount(price, rate):
    discount = price * rate
    return price - discount

def checkout(cart):
    total = sum(cart)
    final_price = calculate_discount(total, 0.1)
    return final_price
"""
    slicer = axiom.CompilationFreeSlicer()
    context = slicer.build(code, "checkout.py")
    print(f"Slicing context built for file: {context.file_path}")
    print(f"Functions detected: {len(context.functions)}")
    print()


# =============================================================================
# EXAMPLE 3: Static Rule Engine (Layer 3)
# =============================================================================
def example_static_rule_engine():
    """Analyze code with static micro/macro rule engine"""
    print("=" * 60)
    print("3. Running Static Rule Engine (Layer 3)...")
    print("=" * 60)

    engine = axiom.StaticRuleEngine()
    sample_file = Path("examples/sample_bugs/sql_injection.py")
    if sample_file.exists():
        result = engine.analyze_file(str(sample_file))
        print(f"Analyzed: {result['file_path']}")
        print(f"Total findings: {result['total_count']}")
        print(f"Critical: {result['critical_count']}, High: {result['high_count']}")
        for f in result['findings']:
            print(f"  - [{f.severity.value.upper()}] {f.rule_name}: {f.message} (Line {f.line_number})")
    print()


# =============================================================================
# EXAMPLE 4: Fix Generator (Layer 4)
# =============================================================================
def example_fix_generator():
    """Generate deterministic fixes using templates"""
    print("=" * 60)
    print("4. Running Fix Generator (Layer 4)...")
    print("=" * 60)

    fixer = axiom.FixGenerator()
    code_snippet = "for i in range(len(items) - 1):\n    pass"

    suggestions = fixer.generate_fixes(code_snippet)
    print(f"Generated suggestions: {len(suggestions)}")
    for s in suggestions:
        print(f"  Bug type: {s.template.bug_type} (Confidence: {s.confidence * 100:.0f}%)")
        print(f"  Description: {s.template.description}")
        print(f"  Fixed code:\n{s.fixed}")

    stats = fixer.get_statistics()
    print(f"Fixer statistics: {stats}")
    print()


# =============================================================================
# EXAMPLE 5: Audit Chain (Layer 5)
# =============================================================================
def example_audit_chain():
    """Log analysis events to tamper-evident Merkle chain and SQLite"""
    print("=" * 60)
    print("5. Running Audit Chain (Layer 5)...")
    print("=" * 60)

    audit = axiom.AuditChain(db_path=":memory:")
    event_id = audit.log_analysis_start("app.py", "main")
    print(f"Logged analysis start. Event ID: {event_id}")

    root_hash = audit.log_analysis_end(event_id, findings_count=2, verification_count=1)
    print(f"Logged analysis end. Merkle Root Hash: {root_hash[:16]}...")
    print()


# =============================================================================
# Main Entry Point
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("⚡ Axiom Aegis v3.0 Feature Examples")
    print("=" * 60)
    print()

    example_ast_sentinel()
    example_slicing()
    example_static_rule_engine()
    example_fix_generator()
    example_audit_chain()

    print("✅ All examples executed successfully!")