"""
Layer 1: AST Sentinel & Pre-Filter

Responsible for:
- Parse code with Tree-sitter into AST
- Detect syntax errors, dangerous calls (eval, exec, os.system)
- Check missing imports and function signature mismatch
- Operate in sub-millisecond (< 5ms)
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import time

try:
    from tree_sitter import Language, Parser
    from tree_sitter_python import language
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False
    language = None  # type: ignore


class Severity(Enum):
    """Severity levels for bug findings"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "HIGH"
    CRITICAL = "critical"


@dataclass
class ASTNode:
    """Represents an AST node"""
    type: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    children: List['ASTNode'] = field(default_factory=list)
    value: str = ""
    parent: Optional['ASTNode'] = None


@dataclass
class BugFinding:
    """Represents a bug finding from Layer 1"""
    severity: Severity
    bug_type: str
    message: str
    file_path: str
    function_path: str
    line_number: int
    column: int
    ast_node_type: str
    code_snippet: str
    evidence: Dict[str, Any] = field(default_factory=dict)


class ASTSentinel:
    """
    Layer 1: Deterministic AST Sentinel & Pre-Filter
    
    Main responsibilities:
    1. Parse code into AST using Tree-sitter
    2. Detect syntax errors
    3. Extract dangerous calls (eval, exec, os.system, subprocess)
    4. Check missing imports
    5. Check function signature mismatch
    """
    
    # Dangerous function patterns (static detection)
    DANGEROUS_CALLS = {
        'eval': {'severity': Severity.CRITICAL, 'cwe': 'CWE-20'},
        'exec': {'severity': Severity.CRITICAL, 'cwe': 'CWE-20'},
        'compile': {'severity': Severity.HIGH, 'cwe': 'CWE-20'},
        'os.system': {'severity': Severity.HIGH, 'cwe': 'CWE-78'},
        'os.popen': {'severity': Severity.HIGH, 'cwe': 'CWE-78'},
        'subprocess.run': {'severity': Severity.HIGH, 'cwe': 'CWE-78'},
        'subprocess.Popen': {'severity': Severity.HIGH, 'cwe': 'CWE-78'},
        'os.popen': {'severity': Severity.HIGH, 'cwe': 'CWE-78'},
    }
    
    # Dangerous modules
    DANGEROUS_MODULES = {
        'os': {'severity': Severity.MEDIUM, 'cwe': 'CWE-78'},
        'sys': {'severity': Severity.LOW, 'cwe': 'CWE-285'},
        'subprocess': {'severity': Severity.HIGH, 'cwe': 'CWE-78'},
    }
    
    def __init__(self, enable_dangerous_call_detection: bool = True):
        """
        Initialize AST Sentinel
        
        Args:
            enable_dangerous_call_detection: Enable dangerous call detection
        """
        self.enable_dangerous_call_detection = enable_dangerous_call_detection
        self.parsers: Dict[str, Parser] = {}
        self._init_parsers()
    
    def _init_parsers(self) -> None:
        """Initialize Tree-sitter parsers"""
        if not HAS_TREE_SITTER or language is None:
            return
        
        try:
            lang = Language(language())
            parser = Parser(lang)
            try:
                parser.set_prewalk_callback(self._prewalk_callback)
            except Exception:
                pass  # Callback setup is optional
            
            # Wrap parser to be callable (tree-sitter 0.26+ removed __call__)
            class _CallableParser:
                def __init__(self, p: Parser) -> None:
                    self._parser = p
                def __call__(self, code: str) -> Any:
                    tree = self._parser.parse(code.encode())
                    return self._tree_to_astnode(tree)
            
                @staticmethod
                def _tree_to_astnode(tree: Any) -> Any:
                    """Convert tree-sitter Tree to ASTNode"""
                    root_node = tree.root_node
                    
                    def _convert_node(node: Any) -> ASTNode:
                        return ASTNode(
                            type=node.type,
                            start_line=node.start_point[0],
                            start_col=node.start_point[1],
                            end_line=node.end_point[0],
                            end_col=node.end_point[1],
                            children=[_convert_node(child) for child in node.children],
                            value=node.text.decode('utf-8', errors='replace') if hasattr(node, 'text') else ''
                        )
                    
                    return _convert_node(root_node)
            
            self.parsers['python'] = _CallableParser(parser)
        except Exception:
            self.parsers = {}
    
    def _prewalk_callback(self, tree: Any, node: Any) -> None:
        """Pre-walk callback for AST analysis"""
        pass  # Can be overridden for custom analysis
    
    def parse_file(self, file_path: str) -> Tuple[ASTNode, List[BugFinding]]:
        """
        Parse a file and detect bugs
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Tuple of (AST root node, list of bug findings)
        """
        start_time = time.time()
        findings: List[BugFinding] = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except FileNotFoundError:
            return None, [self._create_error_finding(file_path, "File not found")]
        except UnicodeDecodeError:
            return None, [self._create_error_finding(file_path, "Invalid encoding")]
        except Exception as e:
            return None, [self._create_error_finding(file_path, f"Parse error: {str(e)}")]
        
        # Parse with Tree-sitter
        if not HAS_TREE_SITTER or language is None:
            return None, [self._create_error_finding(file_path, "Tree-sitter not available")]
        
        try:
            if 'python' not in self.parsers:
                return None, [self._create_error_finding(file_path, "Tree-sitter parser not initialized")]
            root = self.parsers['python'](code)
        except Exception as e:
            return None, [self._create_error_finding(file_path, f"AST parse error: {str(e)}")]
        
        # Walk AST and detect bugs
        findings.extend(self._walk_ast(root, file_path, code, ""))
        
        processing_time = (time.time() - start_time) * 1000  # ms
        
        return root, findings
    
    def parse_code(self, code: str, file_path: str, function_path: str = "") -> Tuple[ASTNode, List[BugFinding]]:
        """
        Parse code string and detect bugs
        
        Args:
            code: Python source code
            file_path: Path to the file (for error reporting)
            function_path: Current function path (for context)
            
        Returns:
            Tuple of (AST root node, list of bug findings)
        """
        if not HAS_TREE_SITTER or language is None:
            return None, [self._create_error_finding(file_path, "Tree-sitter not available")]
        
        try:
            if 'python' not in self.parsers:
                return None, [self._create_error_finding(file_path, "Tree-sitter parser not initialized")]
            root = self.parsers['python'](code)
        except Exception as e:
            return None, [self._create_error_finding(file_path, f"AST parse error: {str(e)}")]
        
        findings = self._walk_ast(root, file_path, code, function_path)
        
        return root, findings
    
    def _walk_ast(self, node: ASTNode, file_path: str, code: str, function_path: str) -> List[BugFinding]:
        """
        Walk AST and detect bugs
        
        Args:
            node: Current AST node
            file_path: Path to the file
            code: Source code
            function_path: Current function path
            
        Returns:
            List of bug findings
        """
        findings: List[BugFinding] = []
        
        # Check for dangerous calls
        if self.enable_dangerous_call_detection:
            findings.extend(self._check_dangerous_calls(node, file_path, code, function_path))
        
        # Check for missing imports
        findings.extend(self._check_missing_imports(node, file_path, code, function_path))
        
        # Check for signature mismatch
        findings.extend(self._check_signature_mismatch(node, file_path, code, function_path))
        
        # Walk children
        for child in node.children:
            findings.extend(self._walk_ast(child, file_path, code, function_path))
        
        return findings
    
    def _check_dangerous_calls(self, node: ASTNode, file_path: str, code: str, function_path: str) -> List[BugFinding]:
        """
        Check for dangerous function calls
        
        Args:
            node: Current AST node
            file_path: Path to the file
            code: Source code
            function_path: Current function path
            
        Returns:
            List of bug findings
        """
        findings: List[BugFinding] = []
        
        if not isinstance(node, ASTNode):
            return findings
        
        # Check if this node is a function call
        if node.type not in ['function_call', 'call']:
            return findings
        
        # Get the function name
        func_name = node.children[0].value if len(node.children) > 0 else ""
        
        if func_name in self.DANGEROUS_CALLS:
            config = self.DANGEROUS_CALLS[func_name]
            severity = config['severity']
            cwe = config['cwe']
            
            # Get code snippet from source lines
            start_line = node.start_line
            start_col = node.start_col
            lines = code.split('\n')
            snippet = lines[start_line].strip() if start_line < len(lines) else ""
        
            findings.append(BugFinding(
                severity=severity,
                bug_type="dangerous_call",
                message=f"Dangerous function call: {func_name}",
                file_path=file_path,
                function_path=function_path,
                line_number=start_line + 1,  # 1-indexed
                column=start_col,
                ast_node_type=node.type,
                code_snippet=snippet[:200],
                evidence={
                    "cwe": cwe,
                    "function": func_name,
                    "risk": "High - Can execute arbitrary code"
                }
            ))
        
        return findings
    
    def _check_missing_imports(self, node: ASTNode, file_path: str, code: str, function_path: str) -> List[BugFinding]:
        """
        Check for missing imports
        
        Args:
            node: Current AST node
            file_path: Path to the file
            code: Source code
            function_path: Current function path
            
        Returns:
            List of bug findings
        """
        findings: List[BugFinding] = []
        
        # TODO: Implement missing import detection
        # This would require parsing all imports and checking usage
        
        return findings
    
    def _check_signature_mismatch(self, node: ASTNode, file_path: str, code: str, function_path: str) -> List[BugFinding]:
        """
        Check for function signature mismatches
        
        Args:
            node: Current AST node
            file_path: Path to the file
            code: Source code
            function_path: Current function path
            
        Returns:
            List of bug findings
        """
        findings: List[BugFinding] = []
        
        # TODO: Implement signature mismatch detection
        # This would require comparing with type stubs or documentation
        
        return findings
    
    def _create_error_finding(self, file_path: str, message: str) -> BugFinding:
        """Create an error finding"""
        return BugFinding(
            severity=Severity.CRITICAL,
            bug_type="parse_error",
            message=message,
            file_path=file_path,
            function_path="",
            line_number=0,
            column=0,
            ast_node_type="error",
            code_snippet="",
            evidence={"error": message}
        )
    
    def get_statistics(self, findings: List[BugFinding]) -> Dict[str, Any]:
        """
        Get statistics about findings
        
        Args:
            findings: List of bug findings
            
        Returns:
            Statistics dictionary
        """
        stats = {
            'total': len(findings),
            'by_severity': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'by_type': {}
        }
        
        for finding in findings:
            stats['by_severity'][finding.severity.value.lower()] += 1
            bug_type = finding.bug_type
            stats['by_type'][bug_type] = stats['by_type'].get(bug_type, 0) + 1
        
        return stats


# Main entry point for Layer 1
def detect_ast_issues(
    file_path: str,
    enable_dangerous_call_detection: bool = True
) -> Tuple[Optional[ASTNode], List[BugFinding]]:
    """
    Main function to detect AST issues
    
    Args:
        file_path: Path to the Python file
        enable_dangerous_call_detection: Enable dangerous call detection
        
    Returns:
        Tuple of (AST root node, list of bug findings)
    """
    sentinel = ASTSentinel(enable_dangerous_call_detection=enable_dangerous_call_detection)
    return sentinel.parse_file(file_path)


__all__ = [
    'ASTSentinel',
    'ASTNode',
    'BugFinding',
    'Severity',
    'detect_ast_issues',
]
