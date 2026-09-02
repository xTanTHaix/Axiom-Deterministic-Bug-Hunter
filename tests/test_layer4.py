"""
Test Layer 4: Dynamic Verification
"""

import pytest
from axiom.layer4.mock_verifier import DynamicVerifier, MockGenerator, RemediationLoop, VerificationLevel


def test_dynamic_verifier_init():
    """Test DynamicVerifier initialization"""
    verifier = DynamicVerifier()
    assert verifier is not None


def test_mock_generator_init():
    """Test MockGenerator initialization"""
    generator = MockGenerator()
    assert generator is not None


def test_remediation_loop_init():
    """Test RemediationLoop initialization"""
    loop = RemediationLoop()
    assert loop is not None


def test_verification_level():
    """Test VerificationLevel enum"""
    assert VerificationLevel.P1.value == "P1"
    assert VerificationLevel.P2.value == "P2"
    assert VerificationLevel.P3.value == "P3"