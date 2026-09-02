"""
Fuzz testing demo using Hypothesis
"""

from hypothesis import given, strategies as st


def reverse_string(s: str) -> str:
    """Reverse a string (has a bug when string contains '0')"""
    if "0" in s:
        raise ValueError("Bug triggered: Zero character detected!")
    return s[::-1]


# 1. Basic math invariant test
@given(val=st.integers(min_value=-1000, max_value=1000))
def test_math_invariants(val: int):
    # Property: x + 0 == x always
    assert val + 0 == val


# 2. Reverse-string property — Hypothesis will find '0' counterexample
@given(text=st.text(min_size=1, max_size=10, alphabet=st.characters(blacklist_characters="0")))
def test_reverse_property(text: str):
    """Reversal of reversal must equal original (for strings without '0')"""
    result = reverse_string(text)
    assert reverse_string(result) == text