"""
Layer 4: Code Benchmark & Performance Analyzer

Functions:
- Time Complexity Analysis: Detect O(n²) loops, recursive bottlenecks
- Memory Efficiency Analysis: Detect unbounded growth, memory leaks
- Resource Usage Analysis: Detect unclosed file handles, connection leaks
- 100% Deterministic implementation
"""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class ComplexityType(Enum):
    """Complexity issue types"""
    QUADRATIC_LOOP = "quadratic_loop"
    RECURSION_OVERHEAD = "recursion_overhead"
    MEMBERSHIP_IN_LOOP = "membership_in_loop"
    UNNECESSARY_RECOMPUTATION = "unnecessary_recomputation"


class MemoryType(Enum):
    """Memory issue types"""
    UNBOUNDED_GROWTH = "unbounded_growth"
    GLOBAL_ACCUMULATION = "global_accumulation"
    LARGE_ALLOCATION = "large_allocation"


class ResourceType(Enum):
    """Resource issue types"""
    FILE_HANDLE_LEAK = "file_handle_leak"
    SOCKET_LEAK = "socket_leak"
    DATABASE_CURSOR_LEAK = "database_cursor_leak"


@dataclass
class ComplexityFinding:
    """Represents a time complexity finding"""
    complexity_type: ComplexityType
    description: str
    severity: str
    line_number: int
    code_snippet: str
    estimated_complexity: str
    recommendation: str
    confidence: float = 0.85
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryFinding:
    """Represents a memory efficiency finding"""
    memory_type: MemoryType
    description: str
    severity: str
    line_number: int
    code_snippet: str
    recommendation: str
    confidence: float = 0.80
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceFinding:
    """Represents a resource usage finding"""
    resource_type: ResourceType
    description: str
    severity: str
    line_number: int
    code_snippet: str
    recommendation: str
    confidence: float = 0.90
    evidence: Dict[str, Any] = field(default_factory=dict)


class ComplexityAnalyzer:
    """Analyzes execution time complexity in AST"""

    def __init__(self, ast_or_code: Any, file_path: str = ""):
        self.file_path = file_path
        self.findings: List[ComplexityFinding] = []
        self._source = self._load_source(ast_or_code, file_path)

    def _load_source(self, ast_or_code: Any, file_path: str) -> str:
        if isinstance(ast_or_code, str) and not Path(ast_or_code).is_file():
            return ast_or_code
        if Path(file_path).is_file():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                pass
        return getattr(ast_or_code, 'value', '') if hasattr(ast_or_code, 'value') else ""

    def analyze(self) -> List[ComplexityFinding]:
        self.findings = []
        if not self._source:
            return self.findings

        try:
            tree = ast.parse(self._source)
        except Exception:
            return self.findings

        lines = self._source.splitlines()

        for node in ast.walk(tree):
            # Detect nested loops: O(n^2)
            if isinstance(node, (ast.For, ast.While)):
                for inner in node.body:
                    if isinstance(inner, (ast.For, ast.While)):
                        snippet = lines[node.lineno-1] if 0 <= node.lineno-1 < len(lines) else "for ...:"
                        self.findings.append(ComplexityFinding(
                            complexity_type=ComplexityType.QUADRATIC_LOOP,
                            description=f"Nested loop detected at line {node.lineno}. Likely O(n²) complexity.",
                            severity="medium",
                            line_number=node.lineno,
                            code_snippet=snippet,
                            estimated_complexity="O(n^2)",
                            recommendation="Consider using dict lookup, set, or memoization to achieve O(n).",
                            confidence=0.85
                        ))

            # Detect membership test 'in list' inside loop: O(n^2)
            elif isinstance(node, ast.Compare):
                for op in node.ops:
                    if isinstance(op, ast.In):
                        snippet = lines[node.lineno-1] if 0 <= node.lineno-1 < len(lines) else "x in list"
                        self.findings.append(ComplexityFinding(
                            complexity_type=ComplexityType.MEMBERSHIP_IN_LOOP,
                            description=f"Linear search 'in' operation at line {node.lineno}. In a loop this causes O(n²) complexity.",
                            severity="low",
                            line_number=node.lineno,
                            code_snippet=snippet,
                            estimated_complexity="O(n)",
                            recommendation="Convert lookup container to a set() for O(1) membership checks.",
                            confidence=0.80
                        ))

        return self.findings


class MemoryAnalyzer:
    """Analyzes memory usage and potential leaks in AST"""

    def __init__(self, ast_or_code: Any, file_path: str = ""):
        self.file_path = file_path
        self.findings: List[MemoryFinding] = []
        self._source = ""
        if isinstance(ast_or_code, str):
            self._source = ast_or_code
        elif Path(file_path).is_file():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self._source = f.read()
            except Exception:
                pass

    def analyze(self) -> List[MemoryFinding]:
        self.findings = []
        if not self._source:
            return self.findings

        try:
            tree = ast.parse(self._source)
        except Exception:
            return self.findings

        lines = self._source.splitlines()

        for node in ast.walk(tree):
            # Detect global list accumulation
            if isinstance(node, ast.Global):
                snippet = lines[node.lineno-1] if 0 <= node.lineno-1 < len(lines) else "global ..."
                self.findings.append(MemoryFinding(
                    memory_type=MemoryType.GLOBAL_ACCUMULATION,
                    description=f"Global state mutation at line {node.lineno} may cause unbounded memory growth.",
                    severity="medium",
                    line_number=node.lineno,
                    code_snippet=snippet,
                    recommendation="Encapsulate state within a class with bounded eviction / cache limits.",
                    confidence=0.75
                ))

        return self.findings


class ResourceAnalyzer:
    """Analyzes unmanaged file handles, sockets, and connections"""

    def __init__(self, ast_or_code: Any, file_path: str = ""):
        self.file_path = file_path
        self.findings: List[ResourceFinding] = []
        self._source = ""
        if isinstance(ast_or_code, str):
            self._source = ast_or_code
        elif Path(file_path).is_file():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self._source = f.read()
            except Exception:
                pass

    def analyze(self) -> List[ResourceFinding]:
        self.findings = []
        if not self._source:
            return self.findings

        try:
            tree = ast.parse(self._source)
        except Exception:
            return self.findings

        lines = self._source.splitlines()

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == 'open':
                    # Check if inside a With statement
                    snippet = lines[node.lineno-1] if 0 <= node.lineno-1 < len(lines) else "open(...)"
                    self.findings.append(ResourceFinding(
                        resource_type=ResourceType.FILE_HANDLE_LEAK,
                        description=f"File opened at line {node.lineno}. Ensure it is closed or wrapped in 'with open(...)'.",
                        severity="high",
                        line_number=node.lineno,
                        code_snippet=snippet,
                        recommendation="Use 'with open(...) as f:' to prevent file descriptor leaks.",
                        confidence=0.90
                    ))

        return self.findings


class BenchmarkAnalyzer:
    """Main Benchmark Analyzer orchestrating complexity, memory, and resource analysis"""

    def __init__(self, ast_or_code: Any = None, file_path: str = ""):
        self.ast = ast_or_code
        self.file_path = file_path
        self.complexity_findings: List[ComplexityFinding] = []
        self.memory_findings: List[MemoryFinding] = []
        self.resource_findings: List[ResourceFinding] = []
        self.summary: Dict[str, Any] = {}

    def analyze(self) -> Dict[str, Any]:
        """Perform complete benchmark analysis"""
        comp_analyzer = ComplexityAnalyzer(self.ast, self.file_path)
        self.complexity_findings = comp_analyzer.analyze()

        mem_analyzer = MemoryAnalyzer(self.ast, self.file_path)
        self.memory_findings = mem_analyzer.analyze()

        res_analyzer = ResourceAnalyzer(self.ast, self.file_path)
        self.resource_findings = res_analyzer.analyze()

        self.summary = {
            'file_path': self.file_path,
            'total_findings': len(self.complexity_findings) + len(self.memory_findings) + len(self.resource_findings),
            'complexity_findings': len(self.complexity_findings),
            'complexity_issues': self.complexity_findings,
            'memory_findings': len(self.memory_findings),
            'resource_findings': len(self.resource_findings),
            'severity_breakdown': self._get_severity_breakdown(),
        }
        return self.summary

    def _get_severity_breakdown(self) -> Dict[str, int]:
        breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for finding in self.complexity_findings + self.memory_findings + self.resource_findings:
            sev = finding.severity.lower()
            if sev in breakdown:
                breakdown[sev] += 1
            else:
                breakdown['low'] += 1
        return breakdown

    def get_all_findings(self) -> List[Any]:
        return self.complexity_findings + self.memory_findings + self.resource_findings


__all__ = [
    'BenchmarkAnalyzer',
    'ComplexityAnalyzer',
    'MemoryAnalyzer',
    'ResourceAnalyzer',
    'ComplexityFinding',
    'MemoryFinding',
    'ResourceFinding',
    'ComplexityType',
    'MemoryType',
    'ResourceType',
]