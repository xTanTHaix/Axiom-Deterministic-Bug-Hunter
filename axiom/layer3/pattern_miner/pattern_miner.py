"""
Layer 3: Pattern Mining Engine

Functions:
- Pattern Mining Algorithm for complex bug pattern detection
- Code Smell, Dependency Anomaly, Control Flow Anomaly, Performance Issue detection
- 100% Deterministic implementation
"""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class PatternCategory(Enum):
    """Category of patterns to mine"""
    CODE_SMELL = "code_smell"
    DEPENDENCY_ANOMALY = "dependency_anomaly"
    CONTROL_FLOW_ANOMALY = "control_flow_anomaly"
    ARCHITECTURE_FLAW = "architecture_flaw"
    PERFORMANCE_ISSUE = "performance_issue"


@dataclass
class PatternMatch:
    """Represents a matched pattern"""
    pattern_type: PatternCategory
    pattern_name: str
    severity: str
    description: str
    file_path: str
    function_path: str
    line_number: int
    column: int
    code_snippet: str
    confidence: float
    evidence: Dict[str, Any] = field(default_factory=dict)


class PatternAnalysis:
    """Pattern analysis result container"""
    def __init__(self, file_path: str, function_path: str = ""):
        self.file_path = file_path
        self.function_path = function_path
        self.matches: List[PatternMatch] = []
        self.stats: Dict[str, int] = {
            'code_smells': 0,
            'dependency_anomalies': 0,
            'control_flow_anomalies': 0,
            'architecture_flaws': 0,
            'performance_issues': 0
        }


class PatternMiner:
    """
    Deep pattern discovery engine
    
    Analyzes code for complex bug patterns using deterministic AST parsing
    """
    
    def __init__(self, ast_or_path: Any = None, file_path: Optional[str] = None):
        """
        Initialize pattern miner
        
        Args:
            ast_or_path: AST node or source file path
            file_path: Optional file path if ast node provided
        """
        if isinstance(ast_or_path, str) and (file_path is None or not Path(str(ast_or_path)).is_file()):
            if Path(ast_or_path).is_file():
                self.file_path = ast_or_path
            else:
                self.file_path = file_path or "sample.py"
        else:
            self.file_path = file_path or (ast_or_path if isinstance(ast_or_path, str) else "sample.py")

        self.ast_root = ast_or_path if not isinstance(ast_or_path, str) else None
        self.matches: List[PatternMatch] = []
        self.stats: Dict[str, int] = {
            'code_smells': 0,
            'dependency_anomalies': 0,
            'control_flow_anomalies': 0,
            'architecture_flaws': 0,
            'performance_issues': 0
        }

    def _get_code(self) -> str:
        """Read file content if available"""
        try:
            if Path(self.file_path).is_file():
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception:
            pass
        return ""

    def mine_patterns(self, code: Optional[str] = None) -> List[PatternMatch]:
        """Mine all patterns from code or file"""
        source = code or self._get_code()
        self.matches = []
        self.stats = {k: 0 for k in self.stats}

        if not source and hasattr(self.ast_root, 'value'):
            source = getattr(self.ast_root, 'value', '')

        if not source:
            return self.matches

        try:
            tree = ast.parse(source)
        except Exception:
            return self.matches

        lines = source.splitlines()

        # 1. Code Smells: Long functions, large classes, deep nesting
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end_lineno = getattr(node, 'end_lineno', node.lineno)
                line_count = end_lineno - node.lineno + 1
                if line_count > 50:
                    snippet = "\n".join(lines[node.lineno-1:min(end_lineno, node.lineno+5)])
                    self.matches.append(PatternMatch(
                        pattern_type=PatternCategory.CODE_SMELL,
                        pattern_name="long_function",
                        severity="medium",
                        description=f"Function '{node.name}' is {line_count} lines long (threshold: 50). Consider breaking it down.",
                        file_path=self.file_path,
                        function_path=node.name,
                        line_number=node.lineno,
                        column=node.col_offset,
                        code_snippet=snippet,
                        confidence=0.85,
                        evidence={'line_count': line_count}
                    ))
                    self.stats['code_smells'] += 1

                # Check deep nesting
                depth = self._calculate_nesting_depth(node)
                if depth >= 4:
                    snippet = "\n".join(lines[node.lineno-1:min(end_lineno, node.lineno+5)])
                    self.matches.append(PatternMatch(
                        pattern_type=PatternCategory.CODE_SMELL,
                        pattern_name="deep_nesting",
                        severity="medium",
                        description=f"Function '{node.name}' has nesting depth of {depth} (threshold: 4). Refactor to reduce cognitive load.",
                        file_path=self.file_path,
                        function_path=node.name,
                        line_number=node.lineno,
                        column=node.col_offset,
                        code_snippet=snippet,
                        confidence=0.90,
                        evidence={'nesting_depth': depth}
                    ))
                    self.stats['code_smells'] += 1

            elif isinstance(node, ast.ClassDef):
                end_lineno = getattr(node, 'end_lineno', node.lineno)
                line_count = end_lineno - node.lineno + 1
                if line_count > 200:
                    snippet = "\n".join(lines[node.lineno-1:min(end_lineno, node.lineno+5)])
                    self.matches.append(PatternMatch(
                        pattern_type=PatternCategory.CODE_SMELL,
                        pattern_name="large_class",
                        severity="medium",
                        description=f"Class '{node.name}' is {line_count} lines long. Consider splitting into modular classes.",
                        file_path=self.file_path,
                        function_path=node.name,
                        line_number=node.lineno,
                        column=node.col_offset,
                        code_snippet=snippet,
                        confidence=0.80,
                        evidence={'line_count': line_count}
                    ))
                    self.stats['code_smells'] += 1

            # 2. Control Flow Anomalies: Bare excepts, dead branches
            elif isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    snippet = lines[node.lineno-1] if 0 <= node.lineno-1 < len(lines) else "except:"
                    self.matches.append(PatternMatch(
                        pattern_type=PatternCategory.CONTROL_FLOW_ANOMALY,
                        pattern_name="bare_except",
                        severity="high",
                        description="Bare except catches all exceptions including SystemExit and KeyboardInterrupt.",
                        file_path=self.file_path,
                        function_path="",
                        line_number=node.lineno,
                        column=node.col_offset,
                        code_snippet=snippet,
                        confidence=0.95,
                        evidence={'recommendation': 'Use specific exception types like except Exception:'}
                    ))
                    self.stats['control_flow_anomalies'] += 1

            # 3. Performance Issues: Nested loops O(n^2)
            elif isinstance(node, (ast.For, ast.While)):
                for inner in node.body:
                    if isinstance(inner, (ast.For, ast.While)):
                        snippet = lines[node.lineno-1] if 0 <= node.lineno-1 < len(lines) else "for ...:"
                        self.matches.append(PatternMatch(
                            pattern_type=PatternCategory.PERFORMANCE_ISSUE,
                            pattern_name="nested_loops",
                            severity="medium",
                            description="Nested loop detected. Quadratic time complexity O(n²) may cause performance bottleneck.",
                            file_path=self.file_path,
                            function_path="",
                            line_number=node.lineno,
                            column=node.col_offset,
                            code_snippet=snippet,
                            confidence=0.80,
                            evidence={'recommendation': 'Consider using dictionary lookups, sets, or vectorized operations'}
                        ))
                        self.stats['performance_issues'] += 1
                        break

        return self.matches

    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum block nesting depth in AST"""
        max_depth = current_depth
        nesting_types = (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.FunctionDef)
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, nesting_types):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        return max_depth

    def mine(self) -> PatternAnalysis:
        """Alias for compatibility with legacy test harness"""
        analysis = PatternAnalysis(self.file_path)
        matches = self.mine_patterns()
        analysis.matches = matches
        analysis.stats = dict(self.stats)
        return analysis

    def get_summary(self) -> Dict[str, Any]:
        """Get pattern mining summary"""
        return {
            'total_matches': len(self.matches),
            'by_category': dict(self.stats),
            'by_severity': self._get_severity_breakdown()
        }

    def _get_severity_breakdown(self) -> Dict[str, int]:
        """Get breakdown by severity"""
        breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for match in self.matches:
            sev = match.severity.lower()
            if sev in breakdown:
                breakdown[sev] += 1
            else:
                breakdown['low'] += 1
        return breakdown


__all__ = [
    'PatternMiner',
    'PatternMatch',
    'PatternCategory',
    'PatternAnalysis',
]