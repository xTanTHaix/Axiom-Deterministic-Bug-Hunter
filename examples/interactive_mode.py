"""
Example: Interactive Bug Review Mode
Demonstrates confidence scoring, interactive review data models, and feedback tracking.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from axiom.cli.interactive.interactive import InteractiveMode, Finding, UserAction

def main():
    print("=" * 60)
    print("📋 Running Interactive Review Mode Example")
    print("=" * 60)

    # Simulate detected findings
    sample_finding = Finding(
        id="finding_001",
        rule_name="SQL_INJECTION",
        severity="critical",
        description="Unsanitized dynamic SQL query construction",
        file_path="app/db.py",
        function_path="get_user",
        line_number=42,
        code_snippet="query = f'SELECT * FROM users WHERE name = {user_input}'",
        confidence=0.95,
        evidence={"param": "user_input", "type": "string_formatting"},
        cwe="CWE-89",
        fix_suggestion="Use parameterized query: cursor.execute('SELECT * FROM users WHERE name = ?', (user_input,))"
    )

    mode = InteractiveMode(findings=[sample_finding], dry_run=True)

    print(f"Loaded {len(mode.findings)} finding(s) for interactive review.")
    print(f"\nFinding Details:")
    print(f"  ID: {sample_finding.id}")
    print(f"  Rule: {sample_finding.rule_name} (CWE: {sample_finding.cwe})")
    print(f"  Confidence: {sample_finding.confidence * 100:.0f}%")
    print(f"  Location: {sample_finding.file_path}:{sample_finding.line_number}")
    print(f"  Code: {sample_finding.code_snippet}")
    print(f"  Suggestion: {sample_finding.fix_suggestion}")

    # Simulate user confirmation action
    sample_finding.user_action = UserAction.CONFIRM
    print(f"\nSimulated User Action: {sample_finding.user_action.value.upper()}")

    print("\n✅ Interactive Review Example completed successfully!")

if __name__ == "__main__":
    main()
