# ⚡Axiom Aegis v3.0 — Pure Deterministic Bug Hunter

<div align="center">

**100% Deterministic · Works offline · Scans any Python project**

<br>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-v3.0.0-emerald.svg)](https://github.com/xTanTHaix/Axiom-Deterministic-Bug-Hunter/releases)
[![AI-Free](https://img.shields.io/badge/AI-Zero%20AI%20%7C%20Deterministic-purple.svg)](#)
[![Tests](https://img.shields.io/badge/tests-pytest%20passing-brightgreen.svg)](#)

</div>

---
## ❓Why Deterministic Bug Hunting?

| 🎯 The Flaw of Random Fuzzing | 🧪 Engineered Predictability |
| :---: | :---: |
| <img src="https://github.com/user-attachments/assets/4d25af15-3418-4c13-9951-2fc0de360bdc" alt="Probabilistic Fuzzing" width="100%"> | <img src="https://github.com/user-attachments/assets/be29955a-06cc-49e7-997b-841cdd001413" alt="Axiom Predictability" width="100%"> |
| *Random inputs lack contextual memory* | *Capture, Sequence, and Reproduce 100%* |

---

## ❓What is Axiom Aegis?

Axiom Aegis is a static and dynamic bug-hunting and security auditing tool for Python codebases.  
It uses a 5-layer pipeline to detect bugs, verify vulnerabilities, and suggest fixes deterministically.

---

| 📊 The Hunting Ground Matrix | 🧰 The Hunter's Utility Belt |
| :---: | :---: |
| <img src="https://github.com/user-attachments/assets/46ce442e-1c75-4630-bfe6-b1df01d19935" alt="Hunting Matrix" width="100%"> | <img src="https://github.com/user-attachments/assets/b87403f4-7665-48d6-acec-ce54e01152ea" alt="Utility Belt" width="100%"> |
| *Comparing probabilistic vs. deterministic* | *State-Tracker, Replay Hook, and Seed Sequencer* |

---

## 🚀Quickstart

```bash

pip install git+https://github.com/xTanTHaix/Axiom-Deterministic-Bug-Hunter.git

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

| ⏱️ The Replay Blueprint | 📑 Anatomy of a Bug Report |
| :---: | :---: |
| <img src="https://github.com/user-attachments/assets/e881679f-d894-4520-a8de-54a816f08adf" alt="Replay Blueprint" width="100%"> | <img src="https://github.com/user-attachments/assets/c13a0719-debd-42cf-bb1f-e4f2b8e1e80a" alt="Bug Report Anatomy" width="100%"> |
| *Step-by-step frame inspection to crash* | *Actionable reports with exact replay commands* |

---

## 🔍5-Layer Architecture

| Layer | Component | Core Functionality |
| :---: | :--- | :--- |
| **L1** | **AST Sentinel** | Tree-sitter AST & Pre-Filter |
| **L2** | **Slicing Engine** | Compilation-Free Slicing & Call Graph |
| **L3** | **Static Rule Engine** | Micro/Macro Analyzers & CWE Mapping |
| **L4** | **Dynamic Verifier** | Auto-pytest & Deterministic Fixes |
| **L5** | **Audit Chain** | Merkle Audit Log & SQLite Sink |

---

| 📉 Frustration to Resolution | 🛡️ The Deterministic Guarantee |
| :---: | :---: |
| <img src="https://github.com/user-attachments/assets/180bc56f-e0c1-429b-8f07-08a5552ffafc" alt="Resolution Graph" width="100%"> | <img src="https://github.com/user-attachments/assets/eae208e8-1a0c-4dd2-bf52-bf9699923660" alt="Deterministic Guarantee" width="100%"> |
| *Eliminating "works on my machine" friction* | *Equip the framework. Hunt deterministically.* |

---

## 🏗️ Project Structure

<details>
<summary>📂 <b>Click to expand full project structure (All directories & files)</b></summary>

```text
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

</details>

---
 
## 💕 Public API

<details>
<summary><b>⚡ Click to expand CLI usage & execution examples</b></summary>

```bash
pip install git+[https://github.com/xTanThaix/Axiom-Deterministic-Bug-Hunter.git](https://github.com/xTanThaix/Axiom-Deterministic-Bug-Hunter.git)

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

</details>

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

| 📉 Replacing Frustration with Predictability | 🛡️ The Deterministic Guarantee |
| :---: | :---: |
| <img src="https://github.com/user-attachments/assets/79e32a43-077d-4301-bdd0-b78241ad5a92" alt="Replacing Frustration" width="100%"> | <img src="https://github.com/user-attachments/assets/1959990f-6e1e-4fcc-b52a-861d9d97259d" alt="The Deterministic Guarantee" width="100%"> |
| *Eliminating "works on my machine" friction* | *Equip the framework. Hunt deterministically.* |

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

## 🪢 Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt` / `pyproject.toml`

---

## 💖 Support & Donations

If this project helped improve your test coverage, save debugging time, and streamline your Python testing workflow, consider supporting development[cite: 1]:

<br>

<div align="center">

[![Ko-fi](https://img.shields.io/badge/Support_on_Ko--fi-FF5E5B?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/xtanthaix)

</div>

---

## 📄 License

MIT License. Free for open-source and commercial use. See [LICENSE](LICENSE) for details.
