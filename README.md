# ⚡Axiom Aegis v3.0 — Pure Deterministic Bug Hunter

> **100% Deterministic · No AI required · Works offline · Scans any Python project**

---

## ❓What is Axiom Aegis?

Axiom Aegis is a static and dynamic bug-hunting and security auditing tool for Python codebases.  
It uses a 5-layer pipeline to detect bugs, verify vulnerabilities, and suggest fixes deterministically.

---

## 🚀Quickstart

```bash

pip install git+https://github.com/xTanTHaix/-Axiom-Aegis-The-Deterministic-Code-Analyzer.git

# 1. Analyze a single file
axiom analyze path/to/file.py

# 2. Analyze an entire project directory recursively
axiom analyze path/to/project/

# 3. Fast dry-run mode (AST + static rules only)
axiom analyze path/to/file.py --dry-run

# 4. Save analysis results to a JSON file
axiom analyze path/to/project/ -o audit_results.json

# 5. Launch interactive GUI Dashboard
axiom ui
axiom ui path/to/project/

# 6. Start Live Watch Mode (auto-scan upon file changes)
axiom watch
axiom watch path/to/project/

# 7. Print tamper-evident audit report
axiom report

# 8. Show version and help
axiom --version
axiom --help
axiom analyze --help
```

---

## 🔍5-Layer Architecture

```
Layer 1: AST Sentinel & Pre-Filter
  └─ Tree-sitter AST parsing & syntax validation
  └─ Dangerous call detection (eval, exec, os.popen, subprocess shell=True)
  └─ Output: ASTNode tree, BugFinding list

Layer 2: Compilation-Free Slicing & Call Graph
  └─ Function-level code slicing without compilation
  └─ Heuristic type inference
  └─ Call graph construction
  └─ Output: SlicingContext, CallGraph

Layer 3: Static Rule Engine & Flow Analyzer
  └─ MicroAnalyzer: line-level regex rules (unchecked unpacking, type coercion, bare except)
  └─ MacroAnalyzer: structural patterns (SQL injection, hardcoded secrets, resource leaks, lock scopes)
  └─ CriticConsensusResolver: multi-analyzer deduplication & conflict resolution
  └─ PatternMiner: code smell and control-flow anomaly detection
  └─ CrossModuleAnalyzer: cross-module type and contract consistency
  └─ Output: Verified BugFinding list with CWE references

Layer 4: Dynamic Verification & Fix Generator
  └─ MockGenerator: auto-generates pytest test cases for detected bugs
  └─ DynamicVerifier: executes generated test cases safely
  └─ RemediationLoop: retry loop for test failures
  └─ FixGenerator: template-based deterministic fix suggestions
  └─ BenchmarkAnalyzer: complexity, memory, and resource usage analysis
  └─ Output: VerificationResult list, FixSuggestion list

Layer 5: Audit Chain & Telemetry
  └─ MerkleChain: cryptographic tamper-evident audit log
  └─ SQLiteSink: persistent event storage (bug_evidence.db)
  └─ RuleLogger: pattern learning and statistics reporting
  └─ AuditChain: top-level audit event coordinator
  └─ Output: Audit report JSON, bug_evidence.db
```

---

## 🏗️Project Structure

```
axiom-aegis/
├── axiom/                          # Main package
│   ├── __init__.py                 # Public API exports
│   ├── __main__.py                 # Package executable (python -m axiom)
│   ├── watcher.py                  # Live filesystem watcher (watchdog + polling fallback)
│   ├── cli/
│   │   ├── __init__.py             # CLI command router & analyze_file implementation
│   │   └── interactive/
│   │       ├── __init__.py
│   │       └── interactive.py      # Interactive Mode TUI
│   ├── config/
│   │   └── __init__.py             # Config management (.env)
│   ├── layer1/
│   │   ├── __init__.py
│   │   ├── ast_sentinel.py         # ASTSentinel, ASTNode, BugFinding, Severity
│   │   ├── fuzzer.py               # Hypothesis fuzz testing strategies
│   │   ├── load.py                 # Concurrency & micro load simulation
│   │   └── mock_proxy.py           # MockHttp proxy responses
│   ├── layer2/
│   │   ├── __init__.py
│   │   └── slicer.py               # CompilationFreeSlicer, CallGraph, SlicingContext
│   ├── layer3/
│   │   ├── __init__.py
│   │   ├── analyzer.py             # StaticRuleEngine, MicroAnalyzer, MacroAnalyzer, CriticConsensusResolver
│   │   ├── context_analyzer/
│   │   │   ├── __init__.py
│   │   │   └── context_analyzer.py # CrossModuleAnalyzer, GlobalTypeSystem
│   │   └── pattern_miner/
│   │       ├── __init__.py
│   │       └── pattern_miner.py    # PatternMiner, PatternMatch, PatternCategory
│   ├── layer4/
│   │   ├── __init__.py
│   │   ├── mock_verifier.py        # DynamicVerifier, MockGenerator, RemediationLoop
│   │   ├── orchestrator.py         # Multi-file analysis runner for directory scans
│   │   ├── delta.py                # AST delta mutation analyzer
│   │   ├── fix_generator/
│   │   │   ├── __init__.py
│   │   │   └── fix_generator.py    # FixGenerator, FixTemplate, FixSuggestion
│   │   └── benchmark/
│   │       ├── __init__.py
│   │       └── benchmark.py        # BenchmarkAnalyzer, ComplexityAnalyzer, MemoryAnalyzer
│   ├── layer5/
│   │   ├── __init__.py
│   │   └── audit.py                # AuditChain, MerkleChain, SQLiteSink, RuleLogger
│   └── ui/
│       ├── __init__.py
│       └── app.py                  # CustomTkinter GUI Dashboard & Live Inspector
├── tests/
│   ├── __init__.py
│   ├── test_imports.py             # Package and layer import tests
│   ├── test_layer1.py              # Layer 1 AST Sentinel unit tests
│   ├── test_layer2.py              # Layer 2 Slicer unit tests
│   ├── test_layer3.py              # Layer 3 Rule Engine unit tests
│   ├── test_layer4.py              # Layer 4 Verifier & Fix Generator unit tests
│   ├── test_layer5.py              # Layer 5 Audit Chain unit tests
│   └── test_fuzz_demo.py           # Property-based fuzzing tests
├── examples/
│   ├── README.md
│   ├── usage_examples.py           # Runnable feature walkthrough
│   └── sample_bugs/
│       ├── dangerous_calls.py      # Sample for os.popen & eval detection
│       ├── sql_injection.py        # Sample for SQL injection & secret leak
│       └── resource_leak.py        # Sample for unmanaged open & bare except
├── handoff.md                      # Audit log & task tracker
├── README.md                       # Documentation
├── CHANGELOG.md                    # Release history
├── pyproject.toml                  # Package configuration
├── requirements.txt                # Dependency list
└── .env.example                    # Sample environment settings
```

---

## 💕Public API

```python
import axiom

# Layer 1 — AST Sentinel
sentinel = axiom.ASTSentinel()
root, findings = sentinel.parse_file("path/to/file.py")

# Layer 2 — Compilation-Free Slicing
slicer = axiom.CompilationFreeSlicer()
context = slicer.build(code, "file.py")

# Layer 3 — Static Rule Engine
engine = axiom.StaticRuleEngine()
result = engine.analyze_file("path/to/file.py")
# result is a dict with keys: 'findings', 'critical_count', 'high_count', etc.

# Layer 3 — Pattern Miner
miner = axiom.PatternMiner(root, "file.py")
patterns = miner.mine_patterns()

# Layer 4 — Dynamic Verification
verifier = axiom.DynamicVerifier()
vresults = verifier.verify_all(result['findings'], code, "file.py")

# Layer 4 — Fix Suggestions
fixer = axiom.FixGenerator()
suggestions = fixer.generate_fixes(code)

# Layer 5 — Audit Chain
audit = axiom.AuditChain()
event_id = audit.log_analysis_start("file.py", "")
```

---

## 🍥CLI Commands

| Command | Description |
|---------|-------------|
| `axiom analyze <target>` | Analyze file or directory |
| `axiom analyze <target> --dry-run` | Run AST & static rules only (fast) |
| `axiom analyze <target> -o report.json` | Export findings to JSON report |
| `axiom ui [target]` | Launch GUI Dashboard & Live Inspector |
| `axiom watch [target]` | Start Live Watch mode on target folder |
| `axiom report` | Output tamper-evident audit report from SQLite |
| `axiom --version` | Display version number |
| `axiom --help` | Display general help |

---

## ❗Scanning Other Projects

Axiom Aegis requires zero setup to scan external Python repositories:

```bash
# Scan any directory
axiom analyze D:\other-project\

# Scan and export findings
axiom analyze D:\other-project\ -o D:\other-project\audit.json
```

---

## 👾Running Tests

```bash
# Run entire test suite
pytest tests/ -v

# Run specific layer tests
pytest tests/test_layer3.py -v

# Run examples script
python examples/usage_examples.py
```

---

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt` / `pyproject.toml`

---

## 💖 Support & Donations

If this project helped improve your test coverage, save debugging time, and streamline your Python testing workflow, consider supporting development:

- **Ko-fi**: [https://ko-fi.com/xtanthaix](https://ko-fi.com/xtanthaix)

---

## 📄 License

MIT License. Free for open-source and commercial use. See [LICENSE](LICENSE) for details.
