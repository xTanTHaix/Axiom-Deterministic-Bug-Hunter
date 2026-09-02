"""
Example: Full 5-Layer Integration Demo
Demonstrates all Axiom Aegis layers operating cohesively in a single pipeline.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import axiom

def main():
    print("=" * 60)
    print("⚡ Running Axiom Aegis Full 5-Layer Integration")
    print("=" * 60)

    target_files = list(Path("examples/sample_bugs").glob("*.py"))
    print(f"Loaded {len(target_files)} sample files for end-to-end processing.")

    # 1. Layer 1: AST Sentinel
    print("\n[Layer 1] AST Sentinel parsing...")
    sentinel = axiom.ASTSentinel()
    total_ast_issues = 0
    for f in target_files:
        _, findings = sentinel.parse_file(str(f))
        total_ast_issues += len(findings)
    print(f"   AST parsing complete. Dangerous calls/issues: {total_ast_issues}")

    # 2. Layer 2: Compilation-Free Slicing
    print("\n[Layer 2] Compilation-Free Slicing...")
    slicer = axiom.CompilationFreeSlicer()
    total_functions = 0
    for f in target_files:
        with open(f, "r", encoding="utf-8") as fp:
            ctx = slicer.build(fp.read(), str(f))
            total_functions += len(ctx.functions)
    print(f"   Slices constructed for {total_functions} functions across codebase.")

    # 3. Layer 3: Static Rule Engine, Pattern Miner & Context Analyzer
    print("\n[Layer 3] Static Rule Engine & Pattern Mining...")
    engine = axiom.StaticRuleEngine()
    total_static_issues = 0
    for f in target_files:
        res = engine.analyze_file(str(f))
        total_static_issues += res['total_count']
    print(f"   Static Rules analyzed. Issues detected: {total_static_issues}")

    context_analyzer = axiom.CrossModuleAnalyzer(target_files)
    context_findings = context_analyzer.analyze()
    print(f"   Cross-Module Context analyzed. Findings: {len(context_findings)}")

    # 4. Layer 4: Dynamic Verification & Fix Generator
    print("\n[Layer 4] Dynamic Verification & Fix Generation...")
    fixer = axiom.FixGenerator()
    total_fixes = 0
    for f in target_files:
        with open(f, "r", encoding="utf-8") as fp:
            fixes = fixer.generate_fixes(fp.read())
            total_fixes += len(fixes)
    print(f"   Auto-Fixes generated: {total_fixes}")

    # 5. Layer 5: Audit Chain & Merkle Verification
    print("\n[Layer 5] Merkle Audit Chain...")
    audit = axiom.AuditChain(db_path=":memory:")
    event_id = audit.log_analysis_start("examples/sample_bugs", "integration_suite")
    root_hash = audit.log_analysis_end(event_id, findings_count=total_static_issues, verification_count=total_fixes)
    print(f"   Audit event logged. Merkle Root Hash: {root_hash[:16]}...")

    print("\n" + "=" * 60)
    print("✅ Full 5-Layer Integration successfully executed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
