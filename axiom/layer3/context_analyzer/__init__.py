"""
Layer 3: Context Analyzer

Exports:
- CrossModuleAnalyzer: Cross-module analysis engine
"""

from .context_analyzer import (
    CrossModuleAnalyzer,
    GlobalTypeSystem,
    CallGraphAnalyzer,
    StateConsistencyChecker,
    ContextFinding,
    AnalysisType
)

__all__ = [
    'CrossModuleAnalyzer',
    'GlobalTypeSystem',
    'CallGraphAnalyzer',
    'StateConsistencyChecker',
    'ContextFinding',
    'AnalysisType',
]