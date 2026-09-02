"""
Test Layer 5: Audit Chain
"""

import pytest
from axiom.layer5.audit import AuditChain, MerkleChain, SQLiteSink, RuleLogger, AuditEventType


def test_audit_chain_init():
    """Test AuditChain initialization"""
    chain = AuditChain()
    assert chain is not None


def test_merkle_chain_init():
    """Test MerkleChain initialization"""
    chain = MerkleChain()
    assert chain is not None


def test_sqlite_sink_init():
    """Test SQLiteSink initialization"""
    sink = SQLiteSink()
    assert sink is not None


def test_rule_logger_init():
    """Test RuleLogger initialization"""
    logger = RuleLogger()
    assert logger is not None


def test_audit_event_type():
    """Test AuditEventType enum"""
    assert AuditEventType.ANALYSIS_START.value == "analysis_start"
    assert AuditEventType.BUG_FOUND.value == "bug_found"
    assert AuditEventType.VERIFICATION_PASS.value == "verification_pass"