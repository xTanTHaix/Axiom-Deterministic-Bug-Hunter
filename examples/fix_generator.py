"""
Example: Fix Generator (Layer 4)
Demonstrates auto fix generation using deterministic templates.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import axiom

# Sample code with bugs
SAMPLE_BUGS = [
    ("off-by-one", "for i in range(len(items) - 1):\n    process(items[i])"),
    ("null-pointer", "if user is None:\n    return None\nname = user.get_name()"),
    ("resource-leak", "f = open('data.txt', 'r')\ncontent = f.read()"),
]

def main():
    print("=" * 60)
    print("💡 Running Fix Generator Example")
    print("=" * 60)

    fixer = axiom.FixGenerator()
    print(f"Loaded {len(fixer.templates)} deterministic fix templates.")

    for bug_name, code in SAMPLE_BUGS:
        print(f"\n--- Testing Bug Pattern: '{bug_name}' ---")
        print("Original Code:")
        print(code)

        fixes = fixer.generate_fixes(code)
        if fixes:
            for fix in fixes:
                print(f"\n[Generated Fix] (Confidence: {fix.confidence * 100:.0f}%)")
                print(f"Description: {fix.template.description}")
                print("Fixed Code:")
                print(fix.fixed)
        else:
            print("No auto-fix template matched.")

    stats = fixer.get_statistics()
    print("\n📊 Fix Generator Statistics:")
    print(f"   Total Templates: {stats['total_templates']}")
    print(f"   Generated Fixes: {stats['generated_fixes']}")
    print("\n✅ Fix Generator completed successfully!")

if __name__ == "__main__":
    main()
