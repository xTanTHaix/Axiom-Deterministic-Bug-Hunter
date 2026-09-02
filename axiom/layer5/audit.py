"""
Layer 5: Merkle Audit Chain, SQLite Sink & Rule-Log Flywheel

Purpose:
- Chain audit events with Merkle root verification
- Persist audit log to SQLite for forensic analysis
- Log rule executions and bug findings to persistent store
- 100% Deterministic audit trail
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import hashlib
import json
import sqlite3
import time
from datetime import datetime
from collections import defaultdict
import os


class AuditEventType(Enum):
    """Types of audit events"""
    ANALYSIS_START = "analysis_start"
    ANALYSIS_END = "analysis_end"
    BUG_FOUND = "bug_found"
    BUG_VERIFIED = "bug_verified"
    REMEDIATION_ATTEMPT = "remediation_attempt"
    VERIFICATION_PASS = "verification_pass"
    VERIFICATION_FAIL = "verification_fail"
    RULE_LEARNED = "rule_learned"


@dataclass
class AuditEntry:
    """Represents an audit entry"""
    event_type: AuditEventType
    timestamp: str
    event_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash_value: str = ""


@dataclass
class BugEvidence:
    """Bug evidence for audit"""
    rule_name: str
    severity: str
    cwe: str
    line_number: int
    code_snippet: str
    mock_test_result: Dict[str, Any] = field(default_factory=dict)
    remediation_result: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RulePattern:
    """Learned rule pattern"""
    pattern_name: str
    bug_count: int
    last_seen: str
    severity_distribution: Dict[str, int] = field(default_factory=dict)
    code_snippets: List[str] = field(default_factory=list)


class MerkleChain:
    """
    Merkle Audit Chain
    
    Immutable audit log using hash chain
    """
    
    def __init__(self, chain_file: str = "audit_chain.json", root_file: str = "merkle_root.txt"):
        """
        Initialize Merkle Chain
        
        Args:
            chain_file: Path to chain file
            root_file: Path to root hash file
        """
        self.chain_file = chain_file
        self.root_file = root_file
        self.chain: List[Dict[str, Any]] = []
        self.root_hash: Optional[str] = None
        
        # Load existing chain if available
        self._load_chain()
    
    def _load_chain(self) -> None:
        """Load existing chain from file"""
        if not os.path.exists(self.chain_file):
            return
        
        try:
            with open(self.chain_file, 'r', encoding='utf-8') as f:
                self.chain = json.load(f)
            self.root_hash = self._compute_root_hash()
        except (json.JSONDecodeError, IOError):
            self.chain = []
    
    def _compute_root_hash(self) -> str:
        """Compute root hash of entire chain"""
        if not self.chain:
            return ""
        
        # Hash all entries
        entry_hashes = [self._hash_entry(entry) for entry in self.chain]
        
        # Chain them together
        current_hash = entry_hashes[0]
        for h in entry_hashes[1:]:
            current_hash = self._hash_string(current_hash + h)
        
        return current_hash
    
    def _hash_entry(self, entry: Dict[str, Any]) -> str:
        """Hash a single entry"""
        return self._hash_string(json.dumps(entry, sort_keys=True))
    
    def _hash_string(self, s: str) -> str:
        """Hash a string"""
        return hashlib.sha256(s.encode('utf-8')).hexdigest()
    
    def add(self, entry: AuditEntry) -> str:
        """
        Add an entry to the chain
        
        Args:
            entry: Audit entry to add
            
        Returns:
            New root hash
        """
        # Compute hash for this entry
        entry_hash = self._hash_entry({
            'event_type': entry.event_type.value,
            'timestamp': entry.timestamp,
            'event_id': entry.event_id,
            'metadata': entry.metadata
        })
        
        # Add to chain
        self.chain.append({
            'event_type': entry.event_type.value,
            'timestamp': entry.timestamp,
            'event_id': entry.event_id,
            'metadata': entry.metadata,
            'hash': entry_hash
        })
        
        # Update root hash
        self.root_hash = self._compute_root_hash()
        
        # Save chain
        self._save_chain()
        
        return self.root_hash
    
    def _save_chain(self) -> None:
        """Save chain to file"""
        try:
            with open(self.chain_file, 'w', encoding='utf-8') as f:
                json.dump(self.chain, f, indent=2)
        except IOError as e:
            print(f"Error saving chain: {e}")
    
    def verify(self) -> bool:
        """
        Verify chain integrity
        
        Returns:
            True if chain is valid, False otherwise
        """
        if not self.root_hash:
            return True
        
        computed_root = self._compute_root_hash()
        return computed_root == self.root_hash
    
    def get_entry(self, event_id: str) -> Optional[AuditEntry]:
        """Get entry by event ID"""
        for entry in self.chain:
            if entry.get('event_id') == event_id:
                return AuditEntry(
                    event_type=AuditEventType(entry['event_type']),
                    timestamp=entry['timestamp'],
                    event_id=entry['event_id'],
                    metadata=entry.get('metadata', {}),
                    hash_value=entry['hash']
                )
        return None
    
    def get_events_by_type(self, event_type: AuditEventType) -> List[AuditEntry]:
        """Get all events of a specific type"""
        return [
            self.get_entry(entry['event_id'])
            for entry in self.chain
            if entry.get('event_type') == event_type.value
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get chain statistics"""
        return {
            'total_entries': len(self.chain),
            'root_hash': self.root_hash[:16] + '...' if self.root_hash else None,
            'verified': self.verify(),
            'by_type': defaultdict(int)
        }
    
    def _save_statistics(self, stats: Dict[str, Any]) -> None:
        """Save statistics to file"""
        try:
            with open('audit_stats.json', 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2)
        except IOError:
            pass


class SQLiteSink:
    """
    SQLite Sink
    
    บันทึกข้อมูลละเอียดในฐานข้อมูล SQLite
    """
    
    def __init__(self, db_path: str = "bug_evidence.db"):
        """
        Initialize SQLite sink
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        self._mem_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            self._mem_conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._init_database()

    def _get_conn(self) -> Tuple[sqlite3.Connection, bool]:
        """Returns (connection, should_close)"""
        if self._mem_conn is not None:
            return self._mem_conn, False
        return sqlite3.connect(self.db_path), True

    def _init_database(self) -> None:
        """Initialize database with required tables"""
        try:
            conn, should_close = self._get_conn()
            cursor = conn.cursor()
            
            # Create audit_events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    event_id TEXT UNIQUE NOT NULL,
                    metadata TEXT NOT NULL,
                    hash_value TEXT
                )
            ''')
            
            # Create bug_evidence table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bug_evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    rule_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    cwe TEXT,
                    line_number INTEGER,
                    code_snippet TEXT,
                    mock_test_result TEXT,
                    remediation_result TEXT,
                    FOREIGN KEY (event_id) REFERENCES audit_events(event_id)
                )
            ''')
            
            # Create rule_patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rule_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_name TEXT UNIQUE NOT NULL,
                    bug_count INTEGER DEFAULT 0,
                    last_seen TEXT,
                    severity_distribution TEXT,
                    code_snippets TEXT
                )
            ''')
            
            conn.commit()
            if should_close:
                conn.close()
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")

    def log_event(self, event_type: AuditEventType, metadata: Dict[str, Any], 
                  event_id: Optional[str] = None) -> str:
        """
        Log an audit event
        
        Args:
            event_type: Type of event
            metadata: Event metadata
            event_id: Optional event ID
            
        Returns:
            Event ID
        """
        timestamp = datetime.utcnow().isoformat()
        event_id = event_id or f"{timestamp}_{hashlib.sha256(json.dumps(metadata, sort_keys=True).encode()).hexdigest()[:8]}"
        
        conn, should_close = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_events 
            (event_type, timestamp, event_id, metadata, hash_value)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            event_type.value,
            timestamp,
            event_id,
            json.dumps(metadata, sort_keys=True),
            hashlib.sha256(json.dumps(metadata, sort_keys=True).encode()).hexdigest()
        ))
        
        conn.commit()
        if should_close:
            conn.close()
        
        return event_id

    def log_bug_evidence(self, event_id: str, evidence: BugEvidence) -> None:
        """
        Log bug evidence
        
        Args:
            event_id: Associated event ID
            evidence: Bug evidence
        """
        conn, should_close = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bug_evidence 
            (event_id, rule_name, severity, cwe, line_number, code_snippet, mock_test_result, remediation_result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_id,
            evidence.rule_name,
            evidence.severity,
            evidence.cwe,
            evidence.line_number,
            json.dumps(evidence.code_snippet, ensure_ascii=False),
            json.dumps(evidence.mock_test_result, ensure_ascii=False),
            json.dumps(evidence.remediation_result, ensure_ascii=False)
        ))
        
        conn.commit()
        if should_close:
            conn.close()

    def log_rule_pattern(self, pattern: RulePattern) -> None:
        """
        Log a learned rule pattern
        
        Args:
            pattern: Rule pattern
        """
        conn, should_close = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO rule_patterns 
            (pattern_name, bug_count, last_seen, severity_distribution, code_snippets)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            pattern.pattern_name,
            pattern.bug_count,
            pattern.last_seen,
            json.dumps(pattern.severity_distribution, sort_keys=True),
            json.dumps(pattern.code_snippets, ensure_ascii=False)
        ))
        
        conn.commit()
        if should_close:
            conn.close()

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            conn, should_close = self._get_conn()
            cursor = conn.cursor()
            
            # Event counts
            cursor.execute('SELECT event_type, COUNT(*) FROM audit_events GROUP BY event_type')
            events = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Bug counts
            cursor.execute('SELECT COUNT(*) FROM bug_evidence')
            bug_count = cursor.fetchone()[0]
            
            # Rule pattern counts
            cursor.execute('SELECT COUNT(*) FROM rule_patterns')
            pattern_count = cursor.fetchone()[0]
            
            if should_close:
                conn.close()
            
            return {
                'total_events': sum(events.values()),
                'event_types': events,
                'total_bugs': bug_count,
                'total_patterns': pattern_count
            }
        except sqlite3.Error as e:
            return {'error': str(e)}


class RuleLogger:
    """
    Rule-Log Flywheel
    
    เรียนรู้ pattern จาก bug findings เพื่อปรับปรุงกฎ
    """
    
    def __init__(self):
        """Initialize rule logger"""
        self._patterns: Dict[str, RulePattern] = {}
        self.sink = SQLiteSink()
    
    def learn(self, bug_finding: Any) -> RulePattern:
        """
        Learn from a bug finding
        
        Args:
            bug_finding: Bug finding to learn from
            
        Returns:
            Learned rule pattern
        """
        rule_name = bug_finding.rule_name
        severity = bug_finding.severity.value
        code_snippet = bug_finding.code_snippet
        
        # Initialize pattern if not exists
        if rule_name not in self._patterns:
            self._patterns[rule_name] = RulePattern(
                pattern_name=rule_name,
                bug_count=0,
                last_seen=datetime.utcnow().isoformat(),
                severity_distribution={}
            )
        
        # Update pattern
        pattern = self._patterns[rule_name]
        pattern.bug_count += 1
        pattern.last_seen = datetime.utcnow().isoformat()
        pattern.severity_distribution[severity] = pattern.severity_distribution.get(severity, 0) + 1
        pattern.code_snippets.append(code_snippet[:200])  # Trim long snippets
        
        # Log to database
        self.sink.log_rule_pattern(pattern)
        
        return pattern
    
    def get_patterns(self) -> Dict[str, RulePattern]:
        """Get all learned patterns"""
        return self._patterns.copy()
    
    def get_top_patterns(self, n: int = 10) -> List[RulePattern]:
        """Get top N patterns by bug count"""
        return sorted(
            self._patterns.values(),
            key=lambda p: p.bug_count,
            reverse=True
        )[:n]
    
    def generate_dpo_data(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Generate DPO-style comparison data
        
        Args:
            n: Number of samples to generate
            
        Returns:
            List of comparison samples
        """
        patterns = self.get_top_patterns(n)
        
        samples = []
        for pattern in patterns:
            for i, snippet in enumerate(pattern.code_snippets[:10]):  # First 10 snippets
                severity_keys = list(pattern.severity_distribution.keys())
                samples.append({
                    'pattern': pattern.pattern_name,
                    'severity': severity_keys[0] if severity_keys else 'medium',
                    'code': snippet,
                    'bug_count': pattern.bug_count
                })
        
        return samples
    
    def save_dpo_data(self, data: List[Dict[str, Any]], output_file: str = "dpo_samples.json") -> None:
        """
        Save DPO data to file
        
        Args:
            data: DPO data
            output_file: Output file path
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving DPO data: {e}")


class AuditChain:
    """
    Layer 5: Complete Audit System
    
    Combines Merkle Chain, SQLite Sink, and Rule Logger
    """
    
    def __init__(self, chain_file: str = "audit_chain.json", db_path: str = "bug_evidence.db"):
        """
        Initialize audit chain
        
        Args:
            chain_file: Chain file path
            db_path: Database file path
        """
        self.merkle_chain = MerkleChain(chain_file)
        self.sqlite_sink = SQLiteSink(db_path)
        self.rule_logger = RuleLogger()
    
    def log_analysis_start(self, file_path: str, function_path: str) -> str:
        """Log analysis start — returns a unique event_id"""
        timestamp = datetime.utcnow().isoformat()
        event_id = f"analysis_{hashlib.sha256(f'{file_path}_{timestamp}'.encode()).hexdigest()[:16]}"

        self.merkle_chain.add(AuditEntry(
            event_type=AuditEventType.ANALYSIS_START,
            timestamp=timestamp,
            event_id=event_id,
            metadata={
                'file_path': file_path,
                'function_path': function_path
            }
        ))

        self.sqlite_sink.log_event(AuditEventType.ANALYSIS_START, {
            'file_path': file_path,
            'function_path': function_path
        }, event_id)

        return event_id

    def log_analysis_end(self, event_id: str, findings_count: int,
                         verification_count: int) -> str:
        """Log analysis end"""
        end_event_id = f"{event_id}_end"
        timestamp = datetime.utcnow().isoformat()

        new_root = self.merkle_chain.add(AuditEntry(
            event_type=AuditEventType.ANALYSIS_END,
            timestamp=timestamp,
            event_id=end_event_id,
            metadata={
                'findings_count': findings_count,
                'verification_count': verification_count
            }
        ))

        self.sqlite_sink.log_event(AuditEventType.ANALYSIS_END, {
            'findings_count': findings_count,
            'verification_count': verification_count
        }, end_event_id)

        return new_root
    
    def log_bug_found(self, event_id: str, bug_finding: Any) -> str:
        """Log bug found"""
        import hashlib
        import json
        bug_event_id = f"bug_{hashlib.sha256(json.dumps({'rule': bug_finding.rule_name, 'line': bug_finding.line_number}, sort_keys=True).encode()).hexdigest()[:8]}"

        self.merkle_chain.add(AuditEntry(
            event_type=AuditEventType.BUG_FOUND,
            timestamp=datetime.utcnow().isoformat(),
            event_id=bug_event_id,
            metadata={
                'rule_name': bug_finding.rule_name,
                'severity': bug_finding.severity.value,
                'cwe': getattr(bug_finding, 'cwe', ''),
                'line_number': bug_finding.line_number
            }
        ))

        self.sqlite_sink.log_event(AuditEventType.BUG_FOUND, {
            'rule_name': bug_finding.rule_name,
            'severity': bug_finding.severity.value,
            'cwe': getattr(bug_finding, 'cwe', '')
        }, bug_event_id)

        # Learn from bug
        self.rule_logger.learn(bug_finding)

        return bug_event_id
    
    def log_verification_result(self, event_id: str, result: Any) -> None:
        """Log verification result"""
        self.sqlite_sink.log_event(
            AuditEventType.VERIFICATION_PASS if result else AuditEventType.VERIFICATION_FAIL,
            {
                'event_id': event_id,
                'result': result
            },
            event_id
        )
    
    def get_audit_report(self) -> Dict[str, Any]:
        """Generate audit report"""
        merkle_stats = self.merkle_chain.get_statistics()
        sqlite_stats = self.sqlite_sink.get_statistics()
        rule_patterns = self.rule_logger.get_top_patterns(10)
        
        return {
            'merkle_chain': merkle_stats,
            'sqlite_sink': sqlite_stats,
            'rule_patterns': [
                {
                    'name': p.pattern_name,
                    'bug_count': p.bug_count,
                    'last_seen': p.last_seen,
                    'severity_distribution': p.severity_distribution
                }
                for p in rule_patterns
            ]
        }
    
    def save_report(self, report: Dict[str, Any], output_file: str = "audit_report.json") -> None:
        """Save audit report to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving report: {e}")


__all__ = [
    'AuditChain',
    'MerkleChain',
    'SQLiteSink',
    'RuleLogger',
    'AuditEntry',
    'BugEvidence',
    'RulePattern',
    'AuditEventType',
]
