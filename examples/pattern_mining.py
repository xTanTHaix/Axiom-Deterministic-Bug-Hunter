"""
Example: Pattern Mining Engine (Layer 3)
Demonstrates code smell, deep nesting, and anti-pattern discovery.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import axiom
from axiom.layer3.pattern_miner.pattern_miner import PatternMiner

# Sample code with deep nesting and code smells
SAMPLE_CODE = """
def deeply_nested_processor(matrix):
    total = 0
    for row in matrix:
        for val in row:
            if val > 0:
                if val % 2 == 0:
                    if val < 100:
                        total += val
    return total

def very_long_function():
    # Simulate long function smell
    a = 1
    b = 2
    c = a + b
    return c
"""

def main():
    print("=" * 60)
    print("🧬 Running Pattern Mining Engine Example")
    print("=" * 60)

    sentinel = axiom.ASTSentinel()
    ast_root, _ = sentinel.parse_code(SAMPLE_CODE, "sample.py")

    miner = PatternMiner(ast_root, "sample.py")
    matches = miner.mine_patterns()

    print(f"Total pattern matches mined: {len(matches)}")
    for match in matches:
        print(f"\n  - Category: {match.pattern_type.value}")
        print(f"    Pattern: {match.pattern_type.value}")
        print(f"    Severity: {match.severity}")
        print(f"    Line: {match.line_number}")
        print(f"    Description: {match.description}")

    summary = miner.get_summary()
    print("\n📊 Pattern Mining Summary:")
    print(f"   By Category: {summary['by_category']}")
    print(f"   By Severity: {summary['by_severity']}")
    print("\n✅ Pattern Mining completed successfully!")

if __name__ == "__main__":
    main()
