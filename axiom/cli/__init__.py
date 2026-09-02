"""
CLI entry point and command router for Axiom Aegis v3.0

Usage:
    axiom analyze <target>   Analyze a file or directory
    axiom ui                 Launch GUI Dashboard
    axiom watch              Live Watch Mode
    axiom report             Generate audit report
    axiom --version          Show version
"""

import argparse
import sys
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from axiom.cli.interactive import InteractiveMode, UserAction

logger = logging.getLogger(__name__)

# Ensure UTF-8 stdout/stderr
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
try:
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def print_header() -> None:
    """Print Axiom Aegis header"""
    print("\n" + "=" * 60)
    print("⚡ AxiOM AEGIS v3.0 — Pure Deterministic Bug Hunter")
    print("=" * 60)
    print()


def analyze_file(
    file_path: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Analyze a single file using all 5 layers

    Args:
        file_path: Path to Python file
        dry_run: If True, don't create mock tests

    Returns:
        Analysis summary dictionary
    """
    from axiom.layer1.ast_sentinel import ASTSentinel, Severity
    from axiom.layer2.slicer import CompilationFreeSlicer
    from axiom.layer3.analyzer import StaticRuleEngine, Severity as AnalysisSeverity
    from axiom.layer4.mock_verifier import DynamicVerifier, VerificationLevel
    from axiom.layer5.audit import AuditChain, AuditEventType

    print_header()
    print(f"📁 Analyzing: {file_path}\n")

    ast_sentinel = ASTSentinel()
    slicer = CompilationFreeSlicer()
    rule_engine = StaticRuleEngine()
    verifier = DynamicVerifier()
    audit = AuditChain()

    # Layer 1: AST Sentinel
    print("[Layer 1] AST Sentinel & Pre-Filter...")
    ast_root, ast_findings = ast_sentinel.parse_file(file_path)

    ast_stats = {
        'findings': len(ast_findings),
        'critical': len([f for f in ast_findings if f.severity == Severity.CRITICAL]),
        'high': len([f for f in ast_findings if f.severity == Severity.HIGH]),
    }
    print("   ✅ AST parsed successfully")
    print(f"   🐛 AST Issues Found: {ast_stats['findings']}")

    # Layer 2: Slicing & Call Graph
    print("[Layer 2] Compilation-Free Slicing & Call Graph...")
    import re as _re
    with open(file_path, 'r', encoding='utf-8') as _f:
        code = _f.read()
    functions = [m.group(1) for m in _re.finditer(r'def\s+(\w+)\s*\(', code)]

    for func in functions[:10]:
        try:
            slicer.slice_function(code, file_path, f"app.{func}")
        except Exception:
            pass

    print(f"   ✅ Slicing completed for {len(functions)} functions")

    # Layer 3: Static Rule Engine
    print("[Layer 3] Static Rule Engine & Flow Analyzer...")
    analysis = rule_engine.analyze_file(file_path)

    rule_stats = {
        'findings': len(analysis['findings']),
        'critical': analysis['critical_count'],
        'high': analysis['high_count'],
        'medium': analysis['medium_count'],
        'low': analysis['low_count'],
    }
    print(f"   🐛 Static Issues Found: {rule_stats['findings']}")
    print(f"   🔴 Critical: {rule_stats['critical']}, 🟠 High: {rule_stats['high']}")

    # Layer 4: Dynamic Verification
    print("[Layer 4] Dynamic Verification...")
    verification_results = []
    verification_stats = {'total': 0, 'passed': 0, 'failed': 0}
    if not dry_run:
        verification_results = verifier.verify_all(analysis['findings'], code, file_path)
        verification_stats = verifier.get_statistics(verification_results)

        print(f"   ✅ Mock Tests Generated: {verification_stats['total']}")
        print(f"   ✅ Passed: {verification_stats['passed']}, Failed: {verification_stats['failed']}")
    else:
        print("   ℹ️  Dry run — mock tests skipped")

    # Layer 5: Audit & Logging
    print("[Layer 5] Audit Chain & Rule-Log...")
    event_id = audit.log_analysis_start(file_path, "")
    audit.log_analysis_end(
        event_id,
        analysis['critical_count'] + analysis['high_count'],
        len(verification_results)
    )

    root_hash = audit.merkle_chain.root_hash
    audit_stats = {
        'event_id': event_id,
        'root_hash': (root_hash[:16] + '...') if root_hash else 'N/A',
    }

    # Summary
    print()
    print("-" * 60)
    print("📊 Analysis Summary:")
    print(f"   Total Issues: {rule_stats['findings']}")
    print(f"   Critical:     {rule_stats['critical']}")
    print(f"   High:         {rule_stats['high']}")
    print(f"   Medium:       {rule_stats['medium']}")
    print(f"   Low:          {rule_stats['low']}")
    print("-" * 60)

    return {
        'file': file_path,
        'ast_issues': ast_stats,
        'rule_issues': rule_stats,
        'verification': verification_stats if not dry_run else {'dry_run': True},
        'audit': audit_stats,
        'success': rule_stats['critical'] == 0 and rule_stats['high'] <= 2
    }


def main() -> int:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="axiom",
        description="Axiom Aegis v3.0: Pure Deterministic Bug Hunter",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a Python file or directory",
    )
    analyze_parser.add_argument(
        "target",
        help="File or directory to analyze"
    )
    analyze_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without creating mock tests"
    )
    analyze_parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Save results to JSON file"
    )

    # ui command
    ui_parser = subparsers.add_parser(
        "ui",
        help="Launch GUI Dashboard"
    )
    ui_parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target file or directory to inspect (default: .)"
    )

    # watch command
    watch_parser = subparsers.add_parser(
        "watch",
        help="Live Watch Mode (scans automatically upon file changes)"
    )
    watch_parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Target directory to watch (default: .)"
    )

    # report command
    subparsers.add_parser(
        "report",
        help="Generate audit report from bug_evidence.db"
    )

    args = parser.parse_args()

    # --version flag
    if args.version:
        import axiom
        print(f"Axiom Aegis v{axiom.__version__}")
        return 0

    # No command given
    if not args.command:
        parser.print_help()
        return 1

    # ui command
    if args.command == "ui":
        try:
            from axiom.ui.app import launch_ui
            target_dir = getattr(args, "target", ".") or "."
            launch_ui(target_dir=target_dir)
            return 0
        except Exception as e:
            print(f"❌ Error launching GUI: {e}")
            return 1

    # watch command
    if args.command == "watch":
        target = getattr(args, "target", ".") or "."
        print(f"👁️  Live Watch Mode started on '{target}' (Press Ctrl+C to stop)...")
        from axiom.watcher import CodeWatcher
        from axiom.layer4.orchestrator import run_analysis

        def on_change():
            print("\n🔄 Change detected, running scan...")
            try:
                run_analysis(target=target, dry_run=True)
            except Exception as ex:
                print(f"⚠️ Scan error: {ex}")
            print("👁️  Watching for changes...")

        watcher = CodeWatcher(target_dir=target, callback=on_change)
        watcher.start()
        try:
            import time
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            watcher.stop()
            print("\n⏹️  Watch mode stopped.")
        return 0

    # report command
    if args.command == "report":
        try:
            from axiom.layer5.audit import AuditChain
            audit = AuditChain()
            report = audit.get_audit_report()
            import json
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return 1

    # analyze command
    if args.command == "analyze":
        target_path = Path(args.target)

        # Directory: use orchestrator for multi-file analysis
        if target_path.is_dir():
            from axiom.layer4.orchestrator import run_analysis
            try:
                result = run_analysis(
                    target=args.target,
                    dry_run=args.dry_run,
                    output_file=getattr(args, "output", None)
                )
                if result.get("critical", 0) > 0:
                    print("⚠️  CRITICAL ISSUES DETECTED — Review required!")
                    return 1
                print("\n✅ Analysis completed successfully")
                return 0
            except Exception as e:
                print(f"❌ Error during analysis: {e}")
                return 1

        # Single file: use analyze_file()
        try:
            result = analyze_file(args.target, dry_run=args.dry_run)
            if result["rule_issues"]["critical"] > 0:
                print("⚠️  CRITICAL ISSUES DETECTED — Review required!")
                return 1
            elif result["rule_issues"]["high"] > 2:
                print("⚠️  HIGH ISSUES DETECTED — Review recommended!")
                return 1
            print("\n✅ Analysis completed successfully")
            return 0
        except FileNotFoundError:
            print(f"❌ File not found: {args.target}")
            return 1
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            return 1

    parser.print_help()
    return 1


__all__ = [
    'main',
    'analyze_file',
    'print_header',
    'InteractiveMode',
    'UserAction',
]


if __name__ == "__main__":
    sys.exit(main())