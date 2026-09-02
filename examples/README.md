# Axiom Aegis v3.0 — Feature Examples & Samples

This directory contains standalone, runnable examples for all Axiom Aegis v3.0 features and analysis layers, as well as sample vulnerable files for testing.

---

## 📁 Directory Layout

```
examples/
├── README.md                   # This documentation
├── usage_examples.py           # Comprehensive multi-layer feature walkthrough
├── pattern_mining.py           # Layer 3: Code smell & anti-pattern discovery
├── cross_module_analysis.py    # Layer 3: Cross-module type & call-graph analysis
├── fix_generator.py            # Layer 4: Deterministic fix template suggestions
├── benchmark_analysis.py       # Layer 4: Time complexity O(n²) & resource analysis
├── interactive_mode.py         # CLI interactive review data models & feedback
├── full_integration.py         # End-to-end 5-layer pipeline execution
└── sample_bugs/                # Sample files with deterministic bugs for testing
    ├── dangerous_calls.py      # Layer 1 & 3: os.popen, eval, shell=True
    ├── sql_injection.py        # Layer 3: SQL injection & hardcoded secrets
    └── resource_leak.py        # Layer 3 & 4: Unmanaged file handle & off-by-one
```

---

## 🚀 How to Run Examples

### Prerequisites

```bash
# 1. Activate your virtual environment
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux

# 2. Ensure package is installed in editable mode
pip install -e .
```

### Running Individual Scripts

All scripts are standalone and executable directly:

```bash
# 1. Run all core layer examples in one script
python examples/usage_examples.py

# 2. Run Pattern Mining example
python examples/pattern_mining.py

# 3. Run Cross-Module Context Analyzer
python examples/cross_module_analysis.py

# 4. Run Fix Generator example
python examples/fix_generator.py

# 5. Run Benchmark & Complexity Analyzer
python examples/benchmark_analysis.py

# 6. Run Interactive Mode example
python examples/interactive_mode.py

# 7. Run Full 5-Layer Integration Pipeline
python examples/full_integration.py
```

---

## 📖 Feature Breakdown

### 1. Pattern Mining Engine ([pattern_mining.py](file:///D:/axiom-aegis/examples/pattern_mining.py))
Discovers deep architectural smells, deep block nesting (>4 levels), long functions (>50 lines), and nested loop performance bottlenecks O(n²):

```python
import axiom
from axiom.layer3.pattern_miner import PatternMiner

sentinel = axiom.ASTSentinel()
ast_root, _ = sentinel.parse_code(source_code, "sample.py")

miner = PatternMiner(ast_root, "sample.py")
matches = miner.mine_patterns()
```

### 2. Cross-Module Context Analyzer ([cross_module_analysis.py](file:///D:/axiom-aegis/examples/cross_module_analysis.py))
Scans multiple Python files simultaneously to detect cross-module type mismatches, missing error paths in call graphs, and unsynchronized global state mutations:

```python
from pathlib import Path
import axiom

files = list(Path("examples/sample_bugs").glob("*.py"))
analyzer = axiom.CrossModuleAnalyzer(files)
findings = analyzer.analyze()
```

### 3. Fix Generator ([fix_generator.py](file:///D:/axiom-aegis/examples/fix_generator.py))
Provides deterministic, template-based code replacement suggestions for common defects (off-by-one errors, unmanaged resources, bare exceptions):

```python
import axiom

fixer = axiom.FixGenerator()
fixes = fixer.generate_fixes(source_code)
for fix in fixes:
    print(f"Bug Type: {fix.template.bug_type}")
    print(f"Confidence: {fix.confidence * 100:.0f}%")
    print(f"Fixed Code:\n{fix.fixed}")
```

### 4. Benchmark Analyzer ([benchmark_analysis.py](file:///D:/axiom-aegis/examples/benchmark_analysis.py))
Detects quadratic loop complexities O(n²), linear search in loops, and unmanaged file handle operations:

```python
import axiom
from axiom.layer4.benchmark import BenchmarkAnalyzer

sentinel = axiom.ASTSentinel()
ast_root, _ = sentinel.parse_code(source_code, "matrix.py")

benchmark = BenchmarkAnalyzer(ast_root, "matrix.py")
summary = benchmark.analyze()
```

### 5. Full 5-Layer Integration ([full_integration.py](file:///D:/axiom-aegis/examples/full_integration.py))
Executes the full pipeline sequentially: AST Sentinel (L1) ➔ Compilation-Free Slicing (L2) ➔ Static Rules & Context (L3) ➔ Fix Generation (L4) ➔ Merkle Audit Chain (L5).

---

## 🎯 Testing with Sample Bugs Suite

You can test the CLI scanner directly against the `sample_bugs/` directory:

```bash
# Scan all sample bugs
axiom analyze examples/sample_bugs/

# Fast dry-run mode (AST + static rules only)
axiom analyze examples/sample_bugs/ --dry-run

# Save findings to JSON report
axiom analyze examples/sample_bugs/ -o sample_results.json
```