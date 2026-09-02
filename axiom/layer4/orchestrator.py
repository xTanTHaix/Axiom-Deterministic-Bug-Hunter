"""
Orchestrator for running Axiom Aegis analysis

This file coordinates the 5-layer analysis pipeline.
"""

import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import argparse

# Ensure UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
try:
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def print_banner() -> None:
    """Print Axiom Aegis banner"""
    print("\n" + "=" * 60)
    print("⚡ AxiOM AEGIS v3.0 — Pure Deterministic Bug Hunter")
    print("=" * 60)
    print()


def run_analysis(
    target: str,
    dry_run: bool = False,
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run full analysis on target
    
    Args:
        target: File or directory to analyze
        dry_run: Skip mock test generation
        output_file: Optional output file path
        
    Returns:
        Analysis results dictionary
    """
    from axiom.layer1.ast_sentinel import ASTSentinel, Severity
    from axiom.layer2.slicer import CompilationFreeSlicer
    from axiom.layer3.analyzer import StaticRuleEngine
    from axiom.layer4.mock_verifier import DynamicVerifier
    from axiom.layer5.audit import AuditChain
    
    print_banner()
    print(f"📁 Target: {target}\n")
    
    # Initialize components
    ast_sentinel = ASTSentinel()
    slicer = CompilationFreeSlicer()
    rule_engine = StaticRuleEngine()
    verifier = DynamicVerifier()
    audit = AuditChain()
    
    # Find Python files
    target_path = Path(target)
    python_files = list(target_path.rglob("*.py"))
    
    if not python_files:
        print(f"❌ No Python files found in: {target}")
        return {'error': 'No Python files found'}
    
    print(f"🔍 Found {len(python_files)} Python file(s)\n")
    
    # Analyze each file
    all_results = []
    total_findings = 0
    critical_findings = 0
    high_findings = 0
    
    for file_path in python_files:
        print(f"📄 Analyzing: {file_path.name}")
        
        try:
            # Layer 1: AST Sentinel
            ast_root, ast_findings = ast_sentinel.parse_file(str(file_path))
            
            # Layer 2: Slicing (sample functions)
            with open(file_path) as f:
                code = f.read()
            
            import re
            functions = [m.group(1) for m in re.finditer(r'def\s+(\w+)\s*\(', code)]
            
            for func in functions[:3]:  # Sample first 3 functions
                try:
                    slicer.slice_function(code, str(file_path), f"app.{func}")
                except:
                    pass
            
            # Layer 3: Static Rules
            analysis = rule_engine.analyze_file(str(file_path))

            # Layer 4: Dynamic Verification (dry run or full)
            verification_results = []
            if not dry_run:
                verification_results = verifier.verify_all(
                    analysis['findings'],
                    code,
                    str(file_path)
                )

            # Layer 5: Audit
            event_id = audit.log_analysis_start(str(file_path), "")
            audit.log_analysis_end(
                event_id,
                analysis['critical_count'] + analysis['high_count'],
                len(verification_results)
            )

            # Collect results
            file_result = {
                'file': str(file_path),
                'ast_issues': len(ast_findings),
                'static_issues': len(analysis['findings']),
                'critical': analysis['critical_count'],
                'high': analysis['high_count'],
                'verification_count': len(verification_results)
            }
            all_results.append(file_result)

            total_findings += len(analysis['findings'])
            critical_findings += analysis['critical_count']
            high_findings += analysis['high_count']
            
        except Exception as e:
            print(f"   ⚠️  Error analyzing {file_path}: {e}")
    
    # Summary
    print()
    print("-" * 60)
    print("📊 Analysis Summary:")
    print(f"   Files Analyzed: {len(python_files)}")
    print(f"   Total Issues: {total_findings}")
    print(f"   Critical:     {critical_findings}")
    print(f"   High:         {high_findings}")
    print("-" * 60)
    
    # Save results
    if output_file:
        results = {
            'target': target,
            'files': all_results,
            'summary': {
                'total_findings': total_findings,
                'critical': critical_findings,
                'high': high_findings,
                'files_analyzed': len(python_files)
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"   📝 Results saved to: {output_file}")
    
    return {
        'success': True,
        'files_analyzed': len(python_files),
        'total_findings': total_findings,
        'critical': critical_findings,
        'high': high_findings,
        'results': all_results
    }


def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        prog="axiom",
        description="Axiom Aegis v3.0: Pure Deterministic Bug Hunter"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze files")
    analyze_parser.add_argument("target", help="Target file or directory")
    analyze_parser.add_argument("--dry-run", action="store_true", help="Skip mock tests")
    analyze_parser.add_argument("--output", "-o", help="Output file for results")
    
    # UI command
    subparsers.add_parser("ui", help="Launch GUI")

    # Watch command
    subparsers.add_parser("watch", help="Watch mode")

    # Report command
    subparsers.add_parser("report", help="Generate report")

    # Version flag
    parser.add_argument("--version", action="store_true", help="Show version")
    
    args = parser.parse_args()
    
    if args.version:
        import axiom
        print(f"Axiom Aegis v{axiom.__version__}")
        return 0
    
    if args.ui:
        try:
            from axiom.ui.app import launch_ui
            launch_ui()
            return 0
        except ImportError:
            print("❌ GUI module not found")
            return 1
    
    if args.watch:
        print("⚠️  Watch mode not yet implemented in v3.0")
        return 0
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Run analysis
    try:
        result = run_analysis(
            target=args.target,
            dry_run=args.dry_run,
            output_file=args.output
        )
        
        if result.get('critical', 0) > 0:
            print("⚠️  CRITICAL ISSUES DETECTED")
            return 1
        
        print("\n✅ Analysis completed successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
