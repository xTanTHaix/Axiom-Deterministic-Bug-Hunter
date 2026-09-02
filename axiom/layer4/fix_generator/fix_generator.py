"""
Layer 4: Fix Generator Engine

Functions:
- Generate code fixes automatically using deterministic templates
- Support for common bug patterns:
  - Off-by-one errors
  - Null check issues
  - Resource management
  - Type coercion
  - Exception handling
- 100% Deterministic template-based implementation
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import re


class FixTemplate:
    """
    Represents a fix template for a specific bug pattern
    
    Attributes:
        bug_type: Type of bug this template fixes
        pattern: Regex pattern to match the bug
        before: Code pattern before fix
        after: Code pattern after fix
        description: Description of the fix
        confidence: Confidence score (0.0-1.0)
    """
    
    def __init__(
        self,
        bug_type: str,
        pattern: str,
        before: str,
        after: str,
        description: str,
        confidence: float = 0.8
    ):
        self.bug_type = bug_type
        self.pattern = pattern
        self.before = before
        self.after = after
        self.description = description
        self.confidence = confidence
    
    def matches(self, code: str) -> bool:
        """Check if template matches the given code"""
        if self.pattern:
            return bool(re.search(self.pattern, code))
        return self.before in code
    
    def generate_fix(self, code: str) -> str:
        """Generate fixed code using this template"""
        if self.pattern:
            # If pattern matches, replace with after template or regex sub
            if r'\1' in self.after or r'\g<' in self.after:
                return re.sub(self.pattern, self.after, code)
            elif re.search(self.pattern, code):
                m = re.search(self.pattern, code)
                if m and m.groups():
                    return re.sub(self.pattern, f"range({m.group(1)})" if 'range' in self.pattern else self.after, code)
                return re.sub(self.pattern, self.after, code)
        return code.replace(self.before, self.after)


class FixSuggestion:
    """
    Represents a generated fix suggestion
    
    Attributes:
        original: Original code snippet
        fixed: Fixed code snippet
        template: Template used for fix
        confidence: Confidence score
    """
    
    def __init__(
        self,
        original: str,
        fixed: str,
        template: FixTemplate,
        confidence: float = 0.85
    ):
        self.original = original
        self.fixed = fixed
        self.template = template
        self.confidence = confidence
    
    def __repr__(self) -> str:
        return f"FixSuggestion({self.template.bug_type}, confidence={self.confidence})"


class FixGenerator:
    """
    Code fix generator using deterministic templates
    
    Analyzes code for common bug patterns and generates fixes
    using predefined templates
    """
    
    def __init__(self):
        """Initialize fix generator with templates"""
        self._generated_count: int = 0
        self.templates: Dict[str, FixTemplate] = {
            'off-by-one': FixTemplate(
                bug_type='off-by-one',
                pattern=r'range\s*\(\s*(len\([^)]+\)|\w+)\s*-\s*1\s*\)',
                before='range({}) - 1',
                after=r'range(\1)',
                description='Remove -1 from range when starting from index 0',
                confidence=0.85
            ),
            'null-pointer': FixTemplate(
                bug_type='null-pointer',
                pattern=r'(\w+)\s*\[\s*(\d+)\s*\]',
                before='data[{}]',
                after=r'\1.get(\2)',
                description='Use .get() instead of direct indexing to avoid null pointer',
                confidence=0.80
            ),
            'resource-leak': FixTemplate(
                bug_type='resource-leak',
                pattern=r'(\w+)\s*=\s*open\s*\(([^)]+)\)',
                before='f = open({})',
                after=r'with open(\2) as \1:',
                description='Use context manager for file handling',
                confidence=0.90
            ),
            'bare-except': FixTemplate(
                bug_type='exception',
                pattern=r'except\s*:',
                before='except:',
                after='except Exception as e:',
                description='Use specific exception handling instead of bare except',
                confidence=0.85
            ),
            'nested-function': FixTemplate(
                bug_type='code-smell',
                pattern=r'def\s+\w+\s*\(.*\):.*?def\s+\w+\s*\(.*\):',
                before='def {}\n...\ndef {}\n...',
                after='def {}\n...\ndef {}\n...',
                description='Consider flattening nested function calls',
                confidence=0.70
            ),
        }
    
    def generate_fixes(self, code: str) -> List[FixSuggestion]:
        """
        Generate all applicable fixes for the given code

        Args:
            code: Source code to analyze

        Returns:
            List of FixSuggestion objects
        """
        suggestions = []

        for bug_type, template in self.templates.items():
            if template.matches(code):
                fixed = template.generate_fix(code)
                suggestions.append(FixSuggestion(
                    original=code,
                    fixed=fixed,
                    template=template,
                    confidence=template.confidence
                ))

        self._generated_count += len(suggestions)
        return suggestions

    def validate_fix(self, original_code: str, fixed_code: str) -> bool:
        """
        Validate that fixed code is syntactically correct

        Args:
            original_code: Original code
            fixed_code: Fixed code

        Returns:
            True if valid, False otherwise
        """
        try:
            import ast

            ast.parse(original_code)
            ast.parse(fixed_code)

            return True
        except SyntaxError:
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get fix generation statistics"""
        return {
            'total_templates': len(self.templates),
            'generated_fixes': self._generated_count,
            'template_coverage': self._get_template_coverage()
        }

    def _get_template_coverage(self) -> Dict[str, int]:
        """Get count of templates per bug type"""
        coverage: Dict[str, int] = {}
        for template in self.templates.values():
            coverage[template.bug_type] = coverage.get(template.bug_type, 0) + 1
        return coverage


__all__ = [
    'FixGenerator',
    'FixTemplate',
    'FixSuggestion',
]
