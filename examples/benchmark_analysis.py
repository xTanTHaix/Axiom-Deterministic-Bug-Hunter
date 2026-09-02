"""
Example: Benchmark Analyzer (Layer 4)
Demonstrates performance bottleneck analysis, time complexity, and memory efficiency checks.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import axiom
from axiom.layer4.benchmark.benchmark import BenchmarkAnalyzer

SAMPLE_CODE = """
def process_matrix(matrix):
    results = []
    # Quadratic complexity O(n^2)
    for row in matrix:
        for val in row:
            if val in results:
                results.append(val)
    return results
"""

def main():
    print("=" * 60)
    print("⚡ Running Benchmark Analyzer Example")
    print("=" * 60)

    sentinel = axiom.ASTSentinel()
    ast_root, _ = sentinel.parse_code(SAMPLE_CODE, "matrix.py")

    analyzer = BenchmarkAnalyzer(ast_root, "matrix.py")
    summary = analyzer.analyze()

    print("\n📊 Benchmark Analysis Summary:")
    print(f"   Complexity Issues Found: {len(summary.get('complexity_issues', []))}")
    for issue in summary.get('complexity_issues', []):
        print(f"\n  - Type: {issue.complexity_type.value}")
        print(f"    Line: {issue.line_number}")
        print(f"    Estimated: {issue.estimated_complexity}")
        print(f"    Description: {issue.description}")
        print(f"    Recommendation: {issue.recommendation}")

    print("\n✅ Benchmark Analysis completed successfully!")

if __name__ == "__main__":
    main()
