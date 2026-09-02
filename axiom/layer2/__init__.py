"""
axiom.layer2 module

Layer 2: Compilation-Free Slicing & Call Graph Mapper
"""

from axiom.layer2.slicer import (
    CompilationFreeSlicer,
    SlicingContext,
    CallGraph,
    CallNode,
    CallEdge,
)

__all__ = [
    'CompilationFreeSlicer',
    'SlicingContext',
    'CallGraph',
    'CallNode',
    'CallEdge',
]
