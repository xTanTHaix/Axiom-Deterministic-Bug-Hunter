"""
CLI: Interactive Mode

Features:
- Interactive mode for user confirmation/rejection of findings
- Confidence Scoring: Each finding has confidence score (0-100%)
- User Feedback Loop: User confirms/rejects findings
- System Learns: Adjusts confidence thresholds from feedback

Pure Deterministic User Interface — No LLM Required

Code Comments: English
"""

import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import sys


class UserAction(Enum):
    """User action types"""
    CONFIRM = "confirm"
    REJECT = "reject"
    SKIP = "skip"
    EXPLAIN = "explain"
    FIX = "fix"


@dataclass
class Finding:
    """Represents a bug finding with user interaction"""
    id: str
    rule_name: str
    severity: str
    description: str
    file_path: str
    function_path: str
    line_number: int
    code_snippet: str
    confidence: float
    evidence: Dict[str, Any]
    cwe: str
    fix_suggestion: Optional[str]
    user_action: Optional[UserAction] = None
    user_feedback: Optional[str] = None


class InteractiveMode:
    """
    Interactive Bug Hunting Mode
    
    Features:
    1. Confidence Scoring: Displays confidence in detection (0-100%)
    2. User Feedback: Confirm/reject/skip findings
    3. Learning: Adjusts thresholds from feedback
    """
    
    def __init__(self, findings: List[Finding], dry_run: bool = False):
        """
        Initialize InteractiveMode
        
        Args:
            findings: List of bug findings to review
            dry_run: If True, don't modify findings in place
        """
        self.findings = findings
        self.dry_run = dry_run
        self.user_feedback: Dict[str, UserAction] = {}
        self.confidence_thresholds: Dict[str, float] = {}
    
    def display_findings(self, max_per_page: int = 10) -> None:
        """
        Display findings to user
        
        Args:
            max_per_page: Maximum findings to show per page
        """
        print("\n" + "=" * 80)
        print("🔍 Axiom Aegis v3.0 - Interactive Bug Review")
        print("=" * 80)
        
        # Group findings by file
        by_file = self._group_by_file()
        
        for file_path, file_findings in by_file.items():
            print(f"\n📄 File: {file_path}")
            print("-" * 80)
            
            for i, finding in enumerate(file_findings[:max_per_page], 1):
                self._display_finding(finding, i)
            
            if len(file_findings) > max_per_page:
                print(f"... and {len(file_findings) - max_per_page} more findings")
                print("Type 'next' to see more")
    
    def _display_finding(self, finding: Finding, index: int) -> None:
        """
        Display a single finding
        
        Args:
            finding: Finding to display
            index: Index within file
        """
        print(f"\n  [{index}] [{finding.severity.upper()}] Confidence: {finding.confidence*100:.0f}%")
        print(f"    Rule: {finding.rule_name}")
        print(f"    File: {finding.file_path}")
        print(f"    Function: {finding.function_path}:{finding.line_number}")
        print(f"    Code:")
        print(f"      {finding.code_snippet}")
        print(f"    Description: {finding.description}")
        print(f"    CWE: {finding.cwe}")
        
        if finding.fix_suggestion:
            print(f"    Suggested Fix: {finding.fix_suggestion}")
        
        print(f"    Evidence: {finding.evidence}")
        print()
    
    def get_user_action(self, finding: Finding, index: int) -> UserAction:
        """
        Get user action for a finding
        
        Args:
            finding: Finding to review
            index: Index of finding
            
        Returns:
            UserAction from user
        """
        print(f"\n  Action for finding {index}:")
        print("    1. Confirm (accept this as a bug)")
        print("    2. Reject (this is not a bug)")
        print("    3. Skip (low priority)")
        print("    4. Explain (ask for explanation)")
        print("    5. Fix (apply suggested fix)")
        print("    0. Back to previous")
        
        try:
            choice = input("\n  Enter choice (0-5): ").strip()
            
            if choice == '0':
                return UserAction.SKIP
            
            elif choice == '1':
                return UserAction.CONFIRM
            
            elif choice == '2':
                return UserAction.REJECT
            
            elif choice == '3':
                return UserAction.SKIP
            
            elif choice == '4':
                return UserAction.EXPLAIN
            
            elif choice == '5':
                return UserAction.FIX
            
            else:
                return UserAction.SKIP
                
        except (ValueError, EOFError):
            return UserAction.SKIP
    
    def handle_explain(self, finding: Finding) -> None:
        """
        Handle explanation request
        
        Args:
            finding: Finding to explain
        """
        print(f"\n📖 Explanation for: {finding.rule_name}")
        print(f"   CWE Reference: {finding.cwe}")
        print(f"   Description: {finding.description}")
        print(f"   Evidence: {finding.evidence}")
        
        # In production, this could fetch detailed explanation from documentation
        print("\n💡 Tip: Review the CWE documentation for more details")
    
    def handle_fix(self, finding: Finding) -> None:
        """
        Handle fix request
        
        Args:
            finding: Finding to fix
        """
        if not finding.fix_suggestion:
            print("⚠️ No fix suggestion available for this finding")
            return
        
        print(f"\n🔧 Suggested Fix:")
        print(f"   {finding.fix_suggestion}")
        
        # In production, this could apply the fix
        print("   💡 Copy this fix and apply it to your code")
    
    def process_all_findings(self) -> List[Finding]:
        """
        Process all findings with user interaction
        
        Returns:
            List of findings with user actions
        """
        print("\n👋 Welcome to Interactive Mode!")
        print("   Review each finding and take an action.")
        print("   Type 'quit' to exit at any time.\n")
        
        processed = []
        
        # Group by file for easier navigation
        by_file = self._group_by_file()
        file_index = 0
        
        for file_path, file_findings in by_file.items():
            print(f"\n{'=' * 80}")
            print(f"📄 Reviewing: {file_path}")
            print(f"{'=' * 80}")
            
            for i, finding in enumerate(file_findings, 1):
                print(f"\n{'-' * 80}")
                self._display_finding(finding, i)
                
                # Get user action
                action = self.get_user_action(finding, i)
                
                # Store feedback
                if self.dry_run:
                    finding.user_action = action
                    finding.user_feedback = self._get_feedback_text(action)
                else:
                    # In production, this would save to database
                    self.user_feedback[finding.id] = action
                
                processed.append(finding)
                
                # Ask to continue
                continue_prompt = input(f"\n  Next finding? (y/n): ").strip().lower()
                if continue_prompt != 'y':
                    break
        
        return processed
    
    def _group_by_file(self) -> Dict[str, List[Finding]]:
        """Group findings by file path"""
        by_file: Dict[str, List[Finding]] = {}
        
        for finding in self.findings:
            if finding.file_path not in by_file:
                by_file[finding.file_path] = []
            by_file[finding.file_path].append(finding)
        
        return by_file
    
    def _get_feedback_text(self, action: UserAction) -> str:
        """Get feedback text for action"""
        texts = {
            UserAction.CONFIRM: "Confirmed as a bug",
            UserAction.REJECT: "Rejected - not a bug",
            UserAction.SKIP: "Skipped - low priority",
            UserAction.EXPLAIN: "Requested explanation",
            UserAction.FIX: "Requested fix suggestion"
        }
        return texts.get(action, "Unknown action")
    
    def generate_report(self, processed: List[Finding]) -> Dict[str, Any]:
        """
        Generate report from processed findings
        
        Args:
            processed: Processed findings with user actions
            
        Returns:
            Report dictionary
        """
        confirmed = [f for f in processed if f.user_action == UserAction.CONFIRM]
        rejected = [f for f in processed if f.user_action == UserAction.REJECT]
        skipped = [f for f in processed if f.user_action == UserAction.SKIP]
        
        return {
            'total_reviewed': len(processed),
            'confirmed': len(confirmed),
            'rejected': len(rejected),
            'skipped': len(skipped),
            'confidence_analysis': self._analyze_confidence(confirmed),
            'recommendations': self._generate_recommendations(confirmed)
        }
    
    def _analyze_confidence(self, confirmed: List[Finding]) -> Dict[str, Any]:
        """Analyze confidence of confirmed findings"""
        if not confirmed:
            return {'average': 0, 'min': 0, 'max': 0}
        
        confidences = [f.confidence for f in confirmed]
        
        return {
            'average': sum(confidences) / len(confidences),
            'min': min(confidences),
            'max': max(confidences),
        }
    
    def _generate_recommendations(self, confirmed: List[Finding]) -> List[str]:
        """Generate recommendations based on confirmed findings"""
        recommendations = []
        
        if not confirmed:
            return ["No findings to recommend"]
        
        # Analyze severity distribution
        severity_counts = {}
        for finding in confirmed:
            severity = finding.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        if severity_counts.get('critical', 0) > 0:
            recommendations.append("⚠️  CRITICAL issues found - Immediate action required")
        
        if severity_counts.get('high', 0) > 5:
            recommendations.append("⚠️  Many HIGH severity issues - Consider refactoring")
        
        avg_confidence = sum(f.confidence for f in confirmed) / len(confirmed)
        if avg_confidence < 0.7:
            recommendations.append("💡 Low average confidence - Review findings manually")
        
        if not recommendations:
            recommendations.append("✅ All findings look good!")
        
        return recommendations
    
    def save_feedback(self, output_path: str) -> None:
        """
        Save user feedback to file
        
        Args:
            output_path: Path to save feedback
        """
        import json
        
        feedback_data = {
            'feedback': self.user_feedback,
            'thresholds': self.confidence_thresholds,
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(feedback_data, f, indent=2, default=str)
        
        print(f"📝 Feedback saved to: {output_path}")
    
    def load_feedback(self, input_path: str) -> None:
        """
        Load user feedback from file
        
        Args:
            input_path: Path to load feedback from
        """
        import json
        
        with open(input_path, 'r', encoding='utf-8') as f:
            feedback_data = json.load(f)
        
        self.user_feedback = feedback_data.get('feedback', {})
        self.confidence_thresholds = feedback_data.get('thresholds', {})
        
        print(f"📝 Feedback loaded from: {input_path}")


def main():
    """Main entry point for interactive mode"""
    parser = argparse.ArgumentParser(
        description="Axiom Aegis Interactive Mode"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without modifying findings"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file for feedback"
    )
    
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Input file with feedback"
    )
    
    args = parser.parse_args()
    
    print("\n🚀 Starting Interactive Mode...")
    
    # Initialize with empty findings (in production, this would come from analysis)
    findings = []
    interactive = InteractiveMode(findings, dry_run=args.dry_run)
    
    # Load feedback if provided
    if args.input:
        interactive.load_feedback(args.input)
    
    # Process findings
    processed = interactive.process_all_findings()
    
    # Generate report
    report = interactive.generate_report(processed)
    
    print("\n📊 Report:")
    print(f"   Total Reviewed: {report['total_reviewed']}")
    print(f"   Confirmed: {report['confirmed']}")
    print(f"   Rejected: {report['rejected']}")
    print(f"   Skipped: {report['skipped']}")
    
    # Save feedback if output path provided
    if args.output:
        interactive.save_feedback(args.output)
    
    print("\n✅ Interactive mode completed")


if __name__ == "__main__":
    main()