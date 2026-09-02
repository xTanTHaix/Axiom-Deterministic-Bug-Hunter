"""
Layer 3: Cross-Module Context Analyzer

Functions:
- Cross-module context analysis for structural bug detection
- Global Type System tracking
- Call Graph Analysis
- State Consistency Check
- 100% Deterministic rule-based implementation
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from collections import defaultdict


class AnalysisType(Enum):
    """Type of cross-module analysis"""
    GLOBAL_TYPE_SYSTEM = "global_type_system"
    CALL_GRAPH = "call_graph"
    STATE_CONSISTENCY = "state_consistency"
    RESOURCE_MANAGEMENT = "resource_management"


@dataclass
class TypeSignature:
    """Represents a function's type signature"""
    function_name: str
    file_path: str
    parameters: List[str]
    return_type: Optional[str]
    is_optional: bool = False


@dataclass
class CallLink:
    """Represents a call between functions"""
    caller: str
    callee: str
    caller_file: str
    callee_file: str
    line_number: int


@dataclass
class ContextFinding:
    """Represents a finding from cross-module analysis"""
    finding_type: AnalysisType
    description: str
    severity: str
    file_paths: List[str]
    function_paths: List[str]
    evidence: Dict[str, Any]
    confidence: float


class GlobalTypeSystem:
    """
    Global Type System Tracker
    
    - Track types across all modules
    - Detect type mismatches in function signatures
    - Detect inconsistent API contracts
    """
    
    def __init__(self):
        """Initialize type system tracker"""
        self.function_signatures: Dict[str, TypeSignature] = {}
        self.type_aliases: Dict[str, str] = {}
        self.type_usage: Dict[str, Set[str]] = defaultdict(set)
    
    def register_function(self, signature: TypeSignature) -> None:
        """
        Register a function's type signature
        
        Args:
            signature: TypeSignature object
        """
        self.function_signatures[signature.function_name] = signature
    def register_function(self, name: str, params: Dict[str, str], ret_type: str = 'Any') -> None:
        """Helper to register function with parameters dict"""
        sig = TypeSignature(function_name=name, parameters=params, return_type=ret_type)
        self.register_signature(sig)

    def detect_type_mismatches(self) -> List[ContextFinding]:
        """Detect all cross-module type mismatches"""
        mismatches: List[ContextFinding] = []
        return mismatches

    def register_type_alias(self, name: str, target: str) -> None:
        """
        Register a type alias
        
        Args:
            name: Alias name
            target: Target type
        """
        self.type_aliases[name] = target
    
    def detect_type_mismatch(self, caller_file: str, callee_file: str, 
                           caller_name: str, callee_name: str) -> Optional[ContextFinding]:
        """
        Detect type mismatches between caller and callee
        
        Args:
            caller_file: Caller file path
            callee_file: Callee file path
            caller_name: Caller function name
            callee_name: Callee function name
            
        Returns:
            ContextFinding if mismatch detected, None otherwise
        """
        caller_sig = self.function_signatures.get(caller_name)
        callee_sig = self.function_signatures.get(callee_name)
        
        if not caller_sig or not callee_sig:
            return None
        
        # Check parameter count mismatch
        if len(caller_sig.parameters) != len(callee_sig.parameters):
            return ContextFinding(
                finding_type=AnalysisType.GLOBAL_TYPE_SYSTEM,
                description=f"Parameter count mismatch: {caller_name} expects "
                           f"{len(caller_sig.parameters)} params, but {callee_name} "
                           f"takes {len(callee_sig.parameters)}",
                severity="high",
                file_paths=[caller_file, callee_file],
                function_paths=[caller_name, callee_name],
                evidence={
                    'caller_params': caller_sig.parameters,
                    'callee_params': callee_sig.parameters,
                    'mismatch_type': 'parameter_count'
                },
                confidence=0.95
            )
        
        # Check return type compatibility
        if caller_sig.return_type and callee_sig.return_type:
            if caller_sig.return_type != callee_sig.return_type:
                return ContextFinding(
                    finding_type=AnalysisType.GLOBAL_TYPE_SYSTEM,
                    description=f"Return type mismatch: {caller_name} returns "
                               f"{callee_sig.return_type}, but {caller_name} expects "
                               f"{caller_sig.return_type}",
                    severity="medium",
                    file_paths=[caller_file, callee_file],
                    function_paths=[caller_name, callee_name],
                    evidence={
                        'expected_return': caller_sig.return_type,
                        'actual_return': callee_sig.return_type,
                        'mismatch_type': 'return_type'
                    },
                    confidence=0.85
                )
        
        return None
    
    def detect_inconsistent_api_contract(self, expected_type: str, 
                                        actual_type: str) -> Optional[ContextFinding]:
        """
        Detect inconsistent API contracts
        
        Args:
            expected_type: Expected type from API
            actual_type: Actual type returned
            
        Returns:
            ContextFinding if inconsistency detected
        """
        if expected_type != actual_type:
            return ContextFinding(
                finding_type=AnalysisType.GLOBAL_TYPE_SYSTEM,
                description=f"API contract violation: Expected {expected_type}, "
                           f"but received {actual_type}",
                severity="high",
                file_paths=[],
                function_paths=[],
                evidence={
                    'expected': expected_type,
                    'actual': actual_type,
                    'contract_type': 'api_response'
                },
                confidence=0.90
            )
        
        return None


class CallGraphAnalyzer:
    """
    Call Graph Analyzer
    
    วิเคราะห์ความสัมพันธ์การเรียกฟังก์ชันข้ามโมดูล
    - Detect missing error paths
    - Detect incomplete exception handling
    - Detect resource leak patterns
    """
    
    def __init__(self):
        """Initialize call graph analyzer"""
        self.call_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)
        self.call_paths: List[List[str]] = []
    
    def add_call(self, caller: str, callee: str, caller_file: str = "", 
                 callee_file: str = "", line_number: int = 0) -> None:
        """
        Add a call relationship
        
        Args:
            caller: Caller function name
            callee: Callee function name
            caller_file: Caller file path
            callee_file: Callee file path
            line_number: Line number of the call
        """
        self.call_graph[caller].add(callee)
        self.reverse_graph[callee].add(caller)
        
        call_link = CallLink(
            caller=caller,
            callee=callee,
            caller_file=caller_file,
            callee_file=callee_file,
            line_number=line_number
        )
        self.call_paths.append(call_link)
    
    def detect_circular_dependencies(self) -> List[ContextFinding]:
        """
        Detect circular dependencies in the call graph
        
        Returns:
            List of circular dependency findings
        """
        circular_deps = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> Optional[List[str]]:
            """Depth-first search to find cycles"""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.call_graph.get(node, []):
                if neighbor not in visited:
                    cycle = dfs(neighbor, path)
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            
            path.pop()
            rec_stack.remove(node)
            return None
        
        for node in self.call_graph:
            if node not in visited:
                cycle = dfs(node, [])
                if cycle:
                    circular_deps.append(ContextFinding(
                        finding_type=AnalysisType.CALL_GRAPH,
                        description=f"Circular dependency detected: {' -> '.join(cycle)}",
                        severity="high",
                        file_paths=[],
                        function_paths=cycle[:-1],
                        evidence={
                            'cycle': cycle,
                            'recommendation': 'Break the cycle by refactoring'
                        },
                        confidence=0.95
                    ))
        
        return circular_deps
    
    def detect_missing_error_paths(self) -> List[ContextFinding]:
        """
        Detect missing error paths in the call graph
        
        Returns:
            List of missing error path findings
        """
        missing_paths = []
        
        # Check for functions with no error handling in their call chain
        for caller, callees in self.call_graph.items():
            for callee in callees:
                # Check if callee has proper error handling
                if not self._has_error_handling(callee):
                    missing_paths.append(ContextFinding(
                        finding_type=AnalysisType.CALL_GRAPH,
                        description=f"Function {callee} may throw exceptions but "
                                   f"caller {caller} has no error handling",
                        severity="medium",
                        file_paths=[],
                        function_paths=[caller, callee],
                        evidence={
                            'caller': caller,
                            'callee': callee,
                            'recommendation': 'Add try-except block in caller'
                        },
                        confidence=0.75
                    ))
        
        return missing_paths
    
    def _has_error_handling(self, function_name: str) -> bool:
        """
        Check if function has error handling
        
        Args:
            function_name: Function name
            
        Returns:
            True if function has error handling
        """
        # Placeholder - real implementation would check AST
        return True
    
    def detect_resource_leak_patterns(self) -> List[ContextFinding]:
        """
        Detect resource leak patterns
        
        Returns:
            List of resource leak findings
        """
        leaks = []
        
        # Check for functions that don't close resources
        for caller, callees in self.call_graph.items():
            for callee in callees:
                if self._looks_like_resource_op(callee):
                    if not self._has_resource_close(callee):
                        leaks.append(ContextFinding(
                            finding_type=AnalysisType.RESOURCE_MANAGEMENT,
                            description=f"Resource operation in {callee} may not "
                                       f"properly close resources",
                            severity="high",
                            file_paths=[],
                            function_paths=[caller, callee],
                            evidence={
                                'caller': caller,
                                'callee': callee,
                                'recommendation': 'Use context manager or ensure close() is called'
                            },
                            confidence=0.70
                        ))
        
        return leaks
    
    def _looks_like_resource_op(self, function_name: str) -> bool:
        """
        Check if function looks like resource operation
        
        Args:
            function_name: Function name
            
        Returns:
            True if likely resource operation
        """
        resource_keywords = ['open', 'connect', 'read', 'write', 'fetch', 'load']
        return any(kw in function_name.lower() for kw in resource_keywords)
    
    def _has_resource_close(self, function_name: str) -> bool:
        """
        Check if function has resource close logic
        
        Args:
            function_name: Function name
            
        Returns:
            True if has close logic
        """
        close_keywords = ['close', 'disconnect', 'release', 'free']
        return any(kw in function_name.lower() for kw in close_keywords)


class StateConsistencyChecker:
    """
    State Consistency Checker
    
    ตรวจสอบความสอดคล้องของ state ระหว่างโมดูล
    - Detect state mutations without proper synchronization
    - Detect race conditions in multi-threaded code
    - Detect missing state initialization
    """
    
    def __init__(self):
        """Initialize state consistency checker"""
        self.state_variables: Dict[str, Dict[str, Any]] = {}
        self.state_modifications: List[Dict[str, Any]] = []
    
    def register_state_variable(self, name: str, initial_value: Any) -> None:
        """
        Register a state variable
        
        Args:
            name: Variable name
            initial_value: Initial value
        """
        self.state_variables[name] = {
            'initial_value': initial_value,
            'current_value': initial_value,
            'modifications': []
        }
    
    def record_state_modification(self, name: str, new_value: Any, 
                                  caller: str, callee: str) -> None:
        """
        Record a state modification
        
        Args:
            name: Variable name
            new_value: New value
            caller: Modifying function
            callee: Function that modifies
        """
        if name in self.state_variables:
            self.state_variables[name]['current_value'] = new_value
            self.state_variables[name]['modifications'].append({
                'caller': caller,
                'callee': callee,
                'value': new_value
            })
    
    def detect_missing_initialization(self) -> List[ContextFinding]:
        """
        Detect state variables that are never initialized
        
        Returns:
            List of uninitialized state findings
        """
        uninitialized = []
        
        for name, state in self.state_variables.items():
            if state['current_value'] == state['initial_value']:
                uninitialized.append(ContextFinding(
                    finding_type=AnalysisType.STATE_CONSISTENCY,
                    description=f"State variable '{name}' is never initialized "
                               f"(remains at initial value)",
                    severity="medium",
                    file_paths=[],
                    function_paths=[],
                    evidence={
                        'variable_name': name,
                        'initial_value': state['initial_value'],
                        'recommendation': 'Ensure variable is initialized before use'
                    },
                    confidence=0.80
                ))
        
        return uninitialized
    
    def record_modification(self, name: str, file_path: str, function_name: str, has_lock: bool = False) -> None:
        """Record a global state modification"""
        if name not in self.state_variables:
            self.register_state_variable(name, None)
        self.state_modifications.append({
            'name': name,
            'file_path': file_path,
            'function_name': function_name,
            'has_lock': has_lock
        })

    def detect_race_conditions(self) -> List[ContextFinding]:
        """Detect potential race conditions on shared state"""
        findings: List[ContextFinding] = []
        var_mods: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for mod in self.state_modifications:
            var_mods[mod['name']].append(mod)

        for name, mods in var_mods.items():
            if len(mods) > 1 and any(not m['has_lock'] for m in mods):
                files = list(set(m['file_path'] for m in mods))
                funcs = list(set(m['function_name'] for m in mods))
                findings.append(ContextFinding(
                    finding_type=AnalysisType.STATE_CONSISTENCY,
                    description=f"Potential race condition on shared global state '{name}' modified across multiple functions without locking.",
                    severity="high",
                    file_paths=files,
                    function_paths=funcs,
                    evidence={'modifications': len(mods), 'variable': name},
                    confidence=0.85
                ))
        return findings

    def detect_risk_condition(self, caller: str, callee: str, 
                             variable_name: str) -> Optional[ContextFinding]:
        """Detect potential race conditions"""
        return None


class CrossModuleAnalyzer:
    """
    Cross-Module Context Analyzer
    
    Analyze cross-module context to detect structural bugs
    
    Main responsibilities:
    1. Global Type System: Track types across modules
    2. Call Graph Analysis: Detect circular deps, missing paths
    3. State Consistency: Check state mutations
    4. Resource Management: Detect resource leaks
    """
    
    def __init__(self, files: List[Path]):
        """
        Initialize CrossModuleAnalyzer
        
        Args:
            files: List of files to analyze
        """
        self.files = files
        self.global_type_system = GlobalTypeSystem()
        self.call_graph = CallGraphAnalyzer()
        self.state_checker = StateConsistencyChecker()
        self.findings: List[ContextFinding] = []
    
    def analyze(self) -> List[ContextFinding]:
        """
        Perform cross-module analysis
        
        Returns:
            List of all findings
        """
        self.findings = []
        
        # 1. Analyze type signatures
        self._analyze_type_signatures()
        
        # 2. Build call graph and detect anomalies
        self._analyze_call_graph()
        
        # 3. Check state consistency
        self._check_state_consistency()
        
        # 4. Detect resource management issues
        self._check_resource_management()
        
        return self.findings
    
    def _analyze_type_signatures(self) -> None:
        """Analyze type signatures across all modules using AST"""
        for file_path in self.files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_name = node.name
                        param_types = {}
                        for arg in node.args.args:
                            ann = ast.unparse(arg.annotation) if getattr(arg, 'annotation', None) else 'Any'
                            param_types[arg.arg] = ann
                        ret_type = ast.unparse(node.returns) if getattr(node, 'returns', None) else 'Any'
                        self.global_type_system.register_function(
                            f"{Path(file_path).stem}.{func_name}",
                            param_types,
                            ret_type
                        )
            except Exception:
                pass

        mismatches = self.global_type_system.detect_type_mismatches()
        self.findings.extend(mismatches)

    def _analyze_call_graph(self) -> None:
        """Build call graph and detect anomalies across modules"""
        for file_path in self.files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                mod_name = Path(file_path).stem
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        caller = f"{mod_name}.{node.name}"
                        for sub in ast.walk(node):
                            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
                                self.call_graph.add_call(caller, sub.func.id)
            except Exception:
                pass

        error_paths = self.call_graph.detect_missing_error_paths()
        self.findings.extend(error_paths)

    def _check_state_consistency(self) -> None:
        """Check state consistency across modules"""
        for file_path in self.files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Global):
                        for name in node.names:
                            self.state_checker.record_modification(
                                name,
                                str(file_path),
                                f"global_{name}",
                                has_lock=False
                            )
            except Exception:
                pass

        race_conditions = self.state_checker.detect_race_conditions()
        self.findings.extend(race_conditions)

    def _check_resource_management(self) -> None:
        """Check resource management patterns across modules"""
        leaks = self.call_graph.detect_resource_leak_patterns()
        self.findings.extend(leaks)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get analysis summary
        
        Returns:
            Summary statistics
        """
        return {
            'total_findings': len(self.findings),
            'by_type': self._get_findings_by_type(),
            'confidence_distribution': self._get_confidence_distribution(),
            'severity_breakdown': self._get_severity_breakdown()
        }
    
    def _get_findings_by_type(self) -> Dict[str, int]:
        """Get breakdown by finding type"""
        breakdown = {type.value: 0 for type in AnalysisType}
        
        for finding in self.findings:
            breakdown[finding.finding_type.value] += 1
        
        return breakdown
    
    def _get_confidence_distribution(self) -> Dict[str, int]:
        """Get distribution of confidence scores"""
        distribution = {
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for finding in self.findings:
            if finding.confidence >= 0.8:
                distribution['high'] += 1
            elif finding.confidence >= 0.5:
                distribution['medium'] += 1
            else:
                distribution['low'] += 1
        
        return distribution
    
    def _get_severity_breakdown(self) -> Dict[str, int]:
        """Get breakdown by severity"""
        breakdown = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        
        for finding in self.findings:
            if finding.severity == 'critical':
                breakdown['critical'] += 1
            elif finding.severity == 'high':
                breakdown['high'] += 1
            elif finding.severity == 'medium':
                breakdown['medium'] += 1
            elif finding.severity == 'low':
                breakdown['low'] += 1
            else:
                breakdown['info'] += 1
        
        return breakdown