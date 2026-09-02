"""
Example: Cross-Module Context Analyzer (Layer 3)
Demonstrates multi-module type consistency, call graphs, and global state tracking.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import axiom

def main():
    print("=" * 60)
    print("🌐 Running Cross-Module Context Analyzer Example")
    print("=" * 60)

    # Gather files from sample_bugs
    files = list(Path("examples/sample_bugs").glob("*.py"))
    print(f"Analyzing {len(files)} modules in system context...")

    analyzer = axiom.CrossModuleAnalyzer(files)
    findings = analyzer.analyze()

    print(f"\nTotal cross-module findings: {len(findings)}")
    for f in findings:
        print(f"\n  - Type: {f.finding_type.value}")
        print(f"    Severity: {f.severity}")
        print(f"    Confidence: {f.confidence * 100:.0f}%")
        print(f"    Description: {f.description}")
        if f.file_paths:
            print(f"    Files: {', '.join(f.file_paths)}")

    summary = analyzer.get_summary()
    print("\n📊 Cross-Module Summary:")
    print(f"   By Type: {summary['by_type']}")
    print(f"   Total: {summary['total_findings']}")
    print("\n✅ Cross-Module Analysis completed successfully!")

if __name__ == "__main__":
    main()
