"""
Layer 3: Static Rule Engine & Flow Analyzer (Dual-Role Deterministic)

Features:
- Micro Analyzer: Detect off-by-one, unchecked unpacking, type coercion
- Macro Analyzer: Detect lock scope, resource leak, race condition
- Critic/Consensus Resolver: Merge & dedup findings

Pure Deterministic Rule-Based — No LLM Required
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re
import ast as python_ast
from collections import defaultdict


class Severity(Enum):
    """Bug severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Rule:
    """Represents a static analysis rule"""
    name: str
    severity: Severity
    cwe: str
    description: str
    pattern: str  # Regex or AST pattern
    fix_suggestion: Optional[str] = None


@dataclass
class BugFinding:
    """Represents a bug finding"""
    rule_name: str
    severity: Severity
    message: str
    file_path: str
    function_path: str
    line_number: int
    column: int
    code_snippet: str
    fix_suggestion: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)


class MicroAnalyzer:
    """
    Micro Analyzer: Detects fine-grained bugs
    
    Features:
    - Off-by-one errors
    - Unchecked unpacking
    - Type coercion issues
    - Boundary condition violations
    """
    
    def __init__(self):
        self.rules = [
            Rule(
                name="OFF_BY_ONE",
                severity=Severity.HIGH,
                cwe="CWE-193",
                description="Off-by-one error in loop or array access",
                pattern=r"\[\s*(\w+)\s*\+\s*1\s*\]|range\s*\(\s*len\s*\([^)]+\)\s*-\s*1\s*\)",
                fix_suggestion="Use range() or adjust index"
            ),
            Rule(
                name="UNCHECKED_UNPACKING",
                severity=Severity.MEDIUM,
                cwe="CWE-685",
                description="Unpacking without length check",
                pattern=r"(\w+)\s*=\s*\((\w+)\)\s*\[",
                fix_suggestion="Add length check before unpacking"
            ),
            Rule(
                name="TYPE_COERCION",
                severity=Severity.LOW,
                cwe="CWE-681",
                description="Implicit type coercion",
                pattern=r"if\s+not\s+(\w+):",
                fix_suggestion="Use explicit type check"
            ),
            Rule(
                name="BARE_EXCEPT",
                severity=Severity.MEDIUM,
                cwe="CWE-396",
                description="Catching bare Exception hides unexpected bugs",
                pattern=r"^\s*except\s*:\s*$",
                fix_suggestion="Catch specific exceptions like `except Exception as e:`"
            ),
            Rule(
                name="HARDCODED_SECRET",
                severity=Severity.HIGH,
                cwe="CWE-798",
                description="Hardcoded credential or API secret detected",
                pattern=r"(?:SECRET|API_KEY|PASSWORD|AUTH_KEY|TOKEN)\s*=\s*['\"][A-Za-z0-9_\-]{10,}['\"]",
                fix_suggestion="Store secrets in environment variables"
            ),
        ]
    
    def analyze(self, code: str, file_path: str) -> List[BugFinding]:
        """
        Analyze code for micro-level bugs
        
        Args:
            code: Source code string
            file_path: Path to source file
            
        Returns:
            List of bug findings
        """
        findings = []
        lines = code.split('\n')
        
        for rule in self.rules:
            for i, line in enumerate(lines, 1):
                if re.search(rule.pattern, line):
                    finding = BugFinding(
                        rule_name=rule.name,
                        severity=rule.severity,
                        message=rule.description,
                        file_path=file_path,
                        function_path="",
                        line_number=i,
                        column=0,
                        code_snippet=line.strip(),
                        fix_suggestion=rule.fix_suggestion,
                        evidence={'line': line}
                    )
                    findings.append(finding)
        
        return findings


class MacroAnalyzer:
    """
    Macro Analyzer: Detects high-level issues
    
    Features:
    - Lock scope violations
    - Resource leaks
    - Race conditions
    - Memory leaks
    """
    
    def __init__(self):
        self.rules = [
            Rule(
                name="RESOURCE_LEAK",
                severity=Severity.HIGH,
                cwe="CWE-775",
                description="Unmanaged file resource opened without context manager",
                pattern=r"(?:^\s*|\s+)\w+\s*=\s*open\s*\(",
                fix_suggestion="Use 'with open(...) as f:' statement"
            ),
            Rule(
                name="SQL_INJECTION",
                severity=Severity.CRITICAL,
                cwe="CWE-89",
                description="Unsanitized dynamic SQL query construction",
                pattern=r"(?:execute|cursor\.execute)\s*\(\s*(?:f['\"].*(?:SELECT|INSERT|UPDATE|DELETE)|['\"].*%\s*\w+|['\"].*format\()",
                fix_suggestion="Use parameterized queries instead of string formatting"
            ),
            Rule(
                name="LOCK_SCOPE",
                severity=Severity.CRITICAL,
                cwe="CWE-667",
                description="Lock held during blocking operation",
                pattern=r"with\s+lock:\s*\n\s+.*blocking",
                fix_suggestion="Minimize lock scope"
            ),
            Rule(
                name="RACE_CONDITION",
                severity=Severity.HIGH,
                cwe="CWE-362",
                description="Potential race condition",
                pattern=r"if\s+not\s+lock\.acquire\(\):",
                fix_suggestion="Add proper synchronization"
            ),
        ]
    
    def analyze(self, code: str, file_path: str) -> List[BugFinding]:
        """
        Analyze code for macro-level issues
        
        Args:
            code: Source code string
            file_path: Path to source file
            
        Returns:
            List of bug findings
        """
        findings = []
        lines = code.split('\n')
        
        for rule in self.rules:
            for i, line in enumerate(lines, 1):
                if re.search(rule.pattern, line):
                    finding = BugFinding(
                        rule_name=rule.name,
                        severity=rule.severity,
                        message=rule.description,
                        file_path=file_path,
                        function_path="",
                        line_number=i,
                        column=0,
                        code_snippet=line.strip(),
                        fix_suggestion=rule.fix_suggestion,
                        evidence={'line': line}
                    )
                    findings.append(finding)
        
        return findings


class CriticConsensusResolver:
    """
    Critic/Consensus Resolver: Merge & dedup findings
    
    Features:
    - Merge duplicate findings
    - Resolve conflicts between analyzers
    - Generate consensus report
    """
    
    def __init__(self):
        self.merged_findings: Dict[str, BugFinding] = {}
    
    def resolve(self, findings: List[BugFinding]) -> List[BugFinding]:
        """
        Resolve conflicting findings
        
        Args:
            findings: List of bug findings from all analyzers
            
        Returns:
            Resolved and deduped findings
        """
        resolved = []
        seen = set()
        
        for finding in findings:
            key = (finding.rule_name, finding.file_path, finding.line_number)
            
            if key not in seen:
                seen.add(key)
                resolved.append(finding)
        
        return resolved
    
    def merge(self, findings: List[BugFinding]) -> List[BugFinding]:
        """
        Merge duplicate findings
        
        Args:
            findings: List of bug findings
            
        Returns:
            Merged findings
        """
        merged = self.resolve(findings)
        
        # Group by file
        by_file = defaultdict(list)
        for finding in merged:
            by_file[finding.file_path].append(finding)
        
        # Dedup within file
        for file_path, file_findings in by_file.items():
            seen_rules = set()
            for finding in file_findings:
                if finding.rule_name not in seen_rules:
                    seen_rules.add(finding.rule_name)
        
        return list(by_file.values())


class StaticRuleEngine:
    """
    Static Rule Engine: Main entry point for Layer 3
    
    Features:
    - Run all analyzers
    - Collect findings
    - Resolve conflicts
    - Generate report
    """
    
    def __init__(self):
        self.micro_analyzer = MicroAnalyzer()
        self.macro_analyzer = MacroAnalyzer()
        self.resolver = CriticConsensusResolver()
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a single file
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Analysis results dictionary
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Run micro analyzer
        micro_findings = self.micro_analyzer.analyze(code, file_path)
        
        # Run macro analyzer
        macro_findings = self.macro_analyzer.analyze(code, file_path)
        
        # Merge findings
        all_findings = micro_findings + macro_findings
        
        # Resolve conflicts
        resolved = self.resolver.resolve(all_findings)
        
        # Generate report
        report = {
            'file_path': file_path,
            'findings': resolved,
            'critical_count': len([f for f in resolved if f.severity == Severity.CRITICAL]),
            'high_count': len([f for f in resolved if f.severity == Severity.HIGH]),
            'medium_count': len([f for f in resolved if f.severity == Severity.MEDIUM]),
            'low_count': len([f for f in resolved if f.severity == Severity.LOW]),
            'total_count': len(resolved),
        }
        
        return report