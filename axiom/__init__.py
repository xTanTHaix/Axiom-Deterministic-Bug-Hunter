"""
Axiom Aegis v3.0 - Ultimate Pure Deterministic Bug Hunter

Multi-Strategy Convergence Architecture:
- Layer 1-5: Core 5-layer deterministic pipeline
- Pattern Mining: Deep bug pattern discovery
- Context Analysis: Cross-module system analysis
- Fix Generator: Auto code suggestions
- Benchmark Analyzer: Performance analysis
- Interactive Mode: User feedback loop

All features are 100% Deterministic - No LLM, No Hallucination

Version: 3.0.0
"""

__version__ = "3.0.0"

# =============================================================================
# LAYER 1: AST Sentinel
# =============================================================================
from axiom.layer1.ast_sentinel import (
    ASTSentinel,
    detect_ast_issues,
)

# DangerousCall is not defined in ast_sentinel.py, remove from imports

# =============================================================================
# LAYER 2: Compilation-Free Slicing
# =============================================================================
from axiom.layer2.slicer import (
    CompilationFreeSlicer,
    CallGraphBuilder
)

# =============================================================================
# LAYER 3: Static Rule Engine & Enhanced Analysis
# =============================================================================
from axiom.layer3.analyzer import (
    StaticRuleEngine,
    MicroAnalyzer,
    MacroAnalyzer,
    CriticConsensusResolver,
    BugFinding
)

# =============================================================================
# LAYER 3: Pattern Mining Engine (v3.0 New)
# =============================================================================
from axiom.layer3.pattern_miner.pattern_miner import (
    PatternMiner,
    PatternMatch,
    PatternCategory
)

# =============================================================================
# LAYER 3: Cross-Module Context Analyzer (v3.0 New)
# =============================================================================
from axiom.layer3.context_analyzer.context_analyzer import (
    CrossModuleAnalyzer,
    GlobalTypeSystem,
    CallGraphAnalyzer,
    StateConsistencyChecker,
    ContextFinding,
    AnalysisType
)

# =============================================================================
# LAYER 4: Dynamic Verification
# =============================================================================
from axiom.layer4.mock_verifier import (
    DynamicVerifier,
    MockGenerator,
    RemediationLoop
)

# =============================================================================
# LAYER 4: Fix Generator (v3.0 New)
# =============================================================================
from axiom.layer4.fix_generator import (
    FixGenerator,
    FixTemplate
)

# =============================================================================
# LAYER 4: Benchmark Analyzer (v3.0 New)
# =============================================================================
from axiom.layer4.benchmark import (
    BenchmarkAnalyzer,
    ComplexityAnalyzer,
    MemoryAnalyzer,
    ResourceAnalyzer,
    ComplexityFinding,
    MemoryFinding,
    ResourceFinding
)

# =============================================================================
# LAYER 5: Audit & Telemetry
# =============================================================================
from axiom.layer5.audit import (
    AuditChain,
    MerkleChain,
    SQLiteSink,
    RuleLogger
)

# =============================================================================
# CLI
# =============================================================================
from axiom.cli.interactive import (
    InteractiveMode,
    UserAction,
    main as cli_main
)

__all__ = [
    # Version
    '__version__',
    
    # Layer 1
    'ASTSentinel',
    'detect_ast_issues',
    
    # Layer 2
    'CompilationFreeSlicer',
    'CallGraphBuilder',
    
    # Layer 3 - Static Rules
    'StaticRuleEngine',
    'MicroAnalyzer',
    'MacroAnalyzer',
    'CriticConsensusResolver',
    'BugFinding',
    
    # Layer 3 - Pattern Mining (v3.0)
    'PatternMiner',
    'PatternMatch',
    'PatternCategory',
    
    # Layer 3 - Context Analysis (v3.0)
    'CrossModuleAnalyzer',
    'GlobalTypeSystem',
    'CallGraphAnalyzer',
    'StateConsistencyChecker',
    'ContextFinding',
    'AnalysisType',
    
    # Layer 4 - Dynamic Verification
    'DynamicVerifier',
    'MockGenerator',
    'RemediationLoop',
    
    # Layer 4 - Fix Generator (v3.0)
    'FixGenerator',
    'FixTemplate',
    
    # Layer 4 - Benchmark (v3.0)
    'BenchmarkAnalyzer',
    'ComplexityAnalyzer',
    'MemoryAnalyzer',
    'ResourceAnalyzer',
    'ComplexityFinding',
    'MemoryFinding',
    'ResourceFinding',
    
    # Layer 5
    'AuditChain',
    'MerkleChain',
    'SQLiteSink',
    'RuleLogger',
    
    # CLI
    'InteractiveMode',
    'UserAction',
    'cli_main',
]