"""
Layer 2: Compilation-Free Slicing & Call Graph Mapper

Responsible for:
- Create slicing context for each function without compilation
- Create call graph showing function call relationships
- Infer missing types using heuristics
- Create multi-view context (text, AST, call graph)

"""

from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re


class ViewType(Enum):
    """Types of views for multi-view context"""
    TEXT = "text"
    AST = "ast"
    CALL_GRAPH = "call_graph"
    TYPE_INFERENCE = "type_inference"


@dataclass
class CallEdge:
    """Represents a call edge in call graph"""
    from_function: str
    to_function: str
    call_count: int = 1
    line_number: int = 0
    is_direct: bool = True  # Direct call vs through other function


@dataclass
class CallNode:
    """Represents a node in call graph"""
    function: str
    file_path: str
    line_number: int
    children: List['CallNode'] = field(default_factory=list)
    incoming_edges: List[CallEdge] = field(default_factory=list)
    outgoing_edges: List[CallEdge] = field(default_factory=list)


@dataclass
class SlicingContext:
    """
    Slicing context for a function
    
    Contains:
    - Sliced function body
    - Dependencies (imports, functions)
    - Inferred types
    - Call graph context
    """
    function_path: str  # e.g., "app.calculator.calculate_discount"
    file_path: str
    line_start: int
    line_end: int
    sliced_code: str
    dependencies: Dict[str, str] = field(default_factory=dict)
    inferred_types: Dict[str, str] = field(default_factory=dict)
    call_graph: 'CallGraph' = field(default_factory=lambda: CallGraph())
    text_view: str = ""
    ast_view: Any = None
    call_graph_view: Dict[str, Any] = field(default_factory=dict)
    functions: List['SlicingContext'] = field(default_factory=list)


@dataclass
class TypeInference:
    """Type inference result for a variable"""
    variable: str
    inferred_type: str
    confidence: float  # 0.0 to 1.0
    source: str  # "default", "usage", "annotation"


class CallGraph:
    """
    Call graph representation
    
    Stores function call relationships without compilation
    """
    
    def __init__(self):
        self.nodes: Dict[str, CallNode] = {}
        self.edges: List[CallEdge] = []
    
    def add_node(self, function: str, file_path: str, line_number: int) -> CallNode:
        """Add a node to call graph"""
        if function not in self.nodes:
            self.nodes[function] = CallNode(
                function=function,
                file_path=file_path,
                line_number=line_number
            )
        return self.nodes[function]
    
    def add_edge(self, from_func: str, to_func: str, line_number: int, is_direct: bool = True) -> CallEdge:
        """Add an edge to call graph"""
        edge = CallEdge(
            from_function=from_func,
            to_function=to_func,
            line_number=line_number,
            is_direct=is_direct
        )
        self.edges.append(edge)
        
        # Update outgoing edges
        from_node = self.nodes.get(from_func)
        if from_node:
            from_node.outgoing_edges.append(edge)
        
        # Update incoming edges
        to_node = self.nodes.get(to_func)
        if to_node:
            to_node.incoming_edges.append(edge)
        
        return edge
    
    def get_dependency_chain(self, target: str) -> List[str]:
        """Get dependency chain to reach target function"""
        chain = []
        visited = set()
        
        def dfs(current: str) -> None:
            if current in visited:
                return
            visited.add(current)
            chain.append(current)
            
            for edge in self.edges:
                if edge.to_function == current:
                    dfs(edge.from_function)
        
        dfs(target)
        return chain
    
    def get_ancestors(self, target: str) -> Set[str]:
        """Get all ancestor functions that call target"""
        ancestors = set()
        visited = set()
        
        def dfs(current: str) -> None:
            if current in visited or current == target:
                return
            visited.add(current)
            ancestors.add(current)
            
            for edge in self.edges:
                if edge.from_function == current:
                    dfs(edge.to_function)
        
        # Start from root (assume all functions are roots)
        for node in self.nodes.values():
            dfs(node.function)
        
        return ancestors


@dataclass
class SliceContext:
    """
    Slicing context for a function
    
    Args:
        function_path: Function path (e.g., "app.calculator.calculate_discount")
        file_path: Source file path
        line_start: Start line number
        line_end: End line number
        sliced_code: Sliced function code
        dependencies: Dict of dependencies
        inferred_types: Dict of inferred types
        call_graph: Call graph context
        text_view: Text view of code
        ast_view: AST representation
        call_graph_view: Call graph visualization
    """
    function_path: str
    file_path: str
    line_start: int
    line_end: int
    sliced_code: str
    dependencies: Dict[str, str]
    inferred_types: Dict[str, str]
    call_graph: CallGraph
    text_view: str
    ast_view: Any
    call_graph_view: Dict[str, Any]


class CompilationFreeSlicer:
    """
    Layer 2: Compilation-Free Slicing & Call Graph Mapper
    
    Responsibilities:
    1. Create slicing context for functions
    2. Build call graph from source code
    3. Infer missing types using heuristics
    4. Create multi-view context
    """
    
    # Type inference rules (heuristic)
    TYPE_INFERENCE_RULES = {
        'int': 'int',
        'float': 'float',
        'str': 'str',
        'bool': 'bool',
        'None': 'NoneType',
        'list': 'list',
        'dict': 'dict',
        'tuple': 'tuple',
        'set': 'set',
    }
    
    def __init__(self):
        """Initialize slicer"""
        self._line_cache: Dict[str, str] = {}
    
    def slice_function(self, code: str, file_path: str, function_path: str) -> SliceContext:
        """
        Create slicing context for a function
        
        Args:
            code: Source code
            file_path: File path
            function_path: Function path (e.g., "app.calculator.calculate_discount")
            
        Returns:
            Slicing context
        """
        # Parse code to find function
        lines = code.split('\n')
        func_lines = self._extract_function_lines(code, function_path)
        
        if not func_lines:
            raise ValueError(f"Function '{function_path}' not found in code")
        
        line_start, line_end = func_lines
        sliced_code = code[line_start * 800:(line_end + 1) * 800]  # Approximate
        
        # Create slicing context
        context = SlicingContext(
            function_path=function_path,
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            sliced_code=sliced_code,
            dependencies=self._extract_dependencies(code, function_path),
            inferred_types=self._infer_types(sliced_code, function_path),
            call_graph=self._build_call_graph(code, function_path),
            text_view=self._format_text_view(sliced_code),
            ast_view=self._format_ast_view(sliced_code),
            call_graph_view=self._format_call_graph_view(self._build_call_graph(code, function_path))
        )
        
        return context
    
    def _extract_function_lines(self, code: str, function_path: str) -> Optional[Tuple[int, int]]:
        """
        Extract line numbers for a function
        
        Args:
            code: Source code
            function_path: Function path
            
        Returns:
            Tuple of (start_line, end_line) or None if not found
        """
        # Simple heuristic: look for function definition
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            # Match function definition
            if re.search(rf'def\s+{re.escape(function_path.split(".")[-1])}\s*\(', line):
                # Find end of function (next def, class, or end of file)
                end_line = i
                for j in range(i + 1, len(lines)):
                    if re.match(r'(def|class)\s+\w+', lines[j]):
                        end_line = j
                        break
                return i, end_line
        
        return None
    
    def _extract_dependencies(self, code: str, function_path: str) -> Dict[str, str]:
        """
        Extract dependencies from function
        
        Args:
            code: Source code
            function_path: Function path
            
        Returns:
            Dict of dependencies
        """
        dependencies = {}
        
        # Extract imports
        imports = self._extract_imports(code)
        for module, imported_name in imports:
            dependencies[imported_name] = f"module:{module}"
        
        # Extract used functions
        used_functions = self._extract_used_functions(code, function_path)
        for func_name in used_functions:
            dependencies[func_name] = "external"
        
        return dependencies
    
    def _extract_imports(self, code: str) -> List[Tuple[str, str]]:
        """
        Extract imports from code
        
        Args:
            code: Source code
            
        Returns:
            List of (module, imported_name) tuples
        """
        imports = []
        
        # Match import statements
        import_pattern = r'import\s+(\w+)|from\s+(\w+)\s+import\s+(\w+)'
        
        for match in re.finditer(import_pattern, code):
            if match.group(1):
                # import module
                imports.append((match.group(1), match.group(1)))
            elif match.group(2) and match.group(3):
                # from module import name
                imports.append((match.group(2), match.group(3)))
        
        return imports
    
    def _extract_used_functions(self, code: str, function_path: str) -> List[str]:
        """
        Extract used functions from code
        
        Args:
            code: Source code
            function_path: Function path
            
        Returns:
            List of used function names
        """
        used_functions = []
        
        # Match function calls (simple heuristic)
        call_pattern = r'\b(\w+)\s*\('
        
        for match in re.finditer(call_pattern, code):
            func_name = match.group(1)
            
            # Skip if it's the current function or built-in
            if func_name == function_path.split('.')[-1] or func_name in ['print', 'len', 'range', 'str', 'int', 'float']:
                continue
            
            used_functions.append(func_name)
        
        return used_functions
    
    def _infer_types(self, code: str, function_path: str) -> Dict[str, str]:
        """
        Infer types using heuristic rules
        
        Args:
            code: Source code
            function_path: Function path
            
        Returns:
            Dict of variable -> inferred type
        """
        inferred_types = {}
        
        # Extract variable assignments
        assign_pattern = r'(\w+)\s*=\s*(\w+|["\']|\(|\[|\{)'
        
        for match in re.finditer(assign_pattern, code):
            var_name = match.group(1)
            value = match.group(2)
            
            # Infer type from value
            if value.startswith('"') or value.startswith("'"):
                inferred_types[var_name] = 'str'
            elif value == '()':
                inferred_types[var_name] = 'function'
            elif value == '[]':
                inferred_types[var_name] = 'list'
            elif value == '{}':
                inferred_types[var_name] = 'dict'
            else:
                inferred_types[var_name] = 'any'
        
        return inferred_types
    
    def _build_call_graph(self, code: str, function_path: str) -> CallGraph:
        """
        Build call graph from code
        
        Args:
            code: Source code
            function_path: Function path
            
        Returns:
            Call graph
        """
        call_graph = CallGraph()
        
        # Extract function calls
        call_pattern = r'(\w+)\s*\('
        
        for match in re.finditer(call_pattern, code):
            func_name = match.group(1)
            
            # Skip built-ins and current function
            if func_name in ['print', 'len', 'range', 'str', 'int', 'float', 'bool', 'type'] or func_name == function_path.split('.')[-1]:
                continue
            
            # Add call edge
            call_graph.add_edge(function_path, func_name, line_number=code.count('\n', 0, match.start()))
        
        return call_graph
    
    def _format_text_view(self, code: str) -> str:
        """Format code as text view"""
        return code
    
    def _format_ast_view(self, code: str) -> str:
        """Format code as AST view"""
        # TODO: Generate AST representation
        return "AST: [Not implemented - requires tree-sitter]"
    
    def _format_call_graph_view(self, call_graph: CallGraph) -> Dict[str, Any]:
        """Format call graph as visualization"""
        return {
            'nodes': list(call_graph.nodes.values()),
            'edges': call_graph.edges,
            'visualization': self._generate_call_graph_visualization(call_graph)
        }
    
    def _generate_call_graph_visualization(self, call_graph: CallGraph) -> str:
        """Generate ASCII visualization of call graph"""
        lines = []
        
        # Group by function
        functions = list(call_graph.nodes.keys())
        
        for i, func in enumerate(functions):
            node = call_graph.nodes[func]
            outgoing = len(node.outgoing_edges)
            incoming = len(node.incoming_edges)
            
            lines.append(f"{i+1}. {func}")
            lines.append(f"   └─ Outgoing: {outgoing}, Incoming: {incoming}")
        
        return '\n'.join(lines)
    
    def get_slicing_context(self, file_path: str, function_path: str) -> Optional[SlicingContext]:
        """
        Get slicing context for a file and function
        
        Args:
            file_path: Source file path
            function_path: Function path
            
        Returns:
            Slicing context or None if not found
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
        
        return self.slice_function(code, file_path, function_path)

    def _extract_function_names(self, code: str) -> List[str]:
        """Extract function names from code using regex"""
        functions = []
        # Match function definitions: def func_name(
        for match in re.finditer(r'\bdef\s+(\w+)\s*\(', code):
            func_name = match.group(1)
            if func_name not in functions:
                functions.append(func_name)
        return functions

    def build(self, code: str, file_path: str) -> SlicingContext:
        """
        Build slicing context for all functions in code

        Args:
            code: Source code
            file_path: File path

        Returns:
            SlicingContext with all functions sliced
        """
        context = SlicingContext(
            function_path=file_path,
            file_path=file_path,
            line_start=0,
            line_end=len(code.split('\n')) - 1,
            sliced_code=code,
            dependencies={},
            inferred_types={},
            call_graph=CallGraph(),
            text_view='',
            ast_view=None,
            call_graph_view={}
        )

        functions = self._extract_function_names(code)
        for func_name in functions:
            func_path = f"{file_path}.{func_name}"
            try:
                sliced = self.slice_function(code, file_path, func_path)
                context.functions.append(sliced)
            except Exception:
                pass

        return context

    def parse(self, code: str, file_path: str) -> SlicingContext:
        """
        Parse code and build slicing context for all functions

        Args:
            code: Source code
            file_path: File path

        Returns:
            SlicingContext with all functions sliced
        """
        return self.build(code, file_path)


class CallGraphBuilder:
    """
    Call graph builder utility class
    
    Provides methods to build and analyze call graphs programmatically
    """
    
    def __init__(self, code: str, function_path: str):
        """
        Initialize builder with code and function path
        
        Args:
            code: Source code to analyze
            function_path: Target function path
        """
        self.code = code
        self.function_path = function_path
    
    def build(self) -> CallGraph:
        """
        Build call graph from code
        
        Returns:
            CallGraph instance
        """
        call_graph = CallGraph()
        
        # Extract function calls
        call_pattern = r'(\w+)\s*\('
        
        for match in re.finditer(call_pattern, self.code):
            func_name = match.group(1)
            
            # Skip built-ins and current function
            if func_name in ['print', 'len', 'range', 'str', 'int', 'float', 'bool', 'type'] or func_name == self.function_path.split('.')[-1]:
                continue
            
            # Add call edge
            call_graph.add_edge(self.function_path, func_name, line_number=self.code.count('\n', 0, match.start()))
        
        return call_graph


__all__ = [
    'CompilationFreeSlicer',
    'SlicingContext',
    'CallGraph',
    'CallNode',
    'CallEdge',
    'SliceContext',
    'CallGraphBuilder',
]
