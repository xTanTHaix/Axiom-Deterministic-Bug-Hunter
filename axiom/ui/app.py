"""
Axiom Aegis GUI Dashboard — CustomTkinter UI for Multi-Target Bug Hunting & Inspection
"""

import threading
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set
from tkinter import filedialog

try:
    import customtkinter as ctk
    HAS_CTK = True
except ImportError:
    HAS_CTK = False

from axiom.layer1.ast_sentinel import ASTSentinel
from axiom.layer2.slicer import CompilationFreeSlicer
from axiom.layer3.analyzer import StaticRuleEngine
from axiom.layer3.pattern_miner.pattern_miner import PatternMiner
from axiom.layer3.context_analyzer.context_analyzer import CrossModuleAnalyzer
from axiom.layer4.mock_verifier import DynamicVerifier
from axiom.layer4.fix_generator.fix_generator import FixGenerator
from axiom.layer4.benchmark.benchmark import BenchmarkAnalyzer
from axiom.layer5.audit import AuditChain
from axiom.layer4.delta import run_delta_mutation, MutationReport, Mutant
from axiom.watcher import CodeWatcher

if HAS_CTK:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


@dataclass
class UIItem:
    category: str  # 'BUG', 'PATTERN', 'CONTEXT', 'FIX', 'BENCHMARK', 'TEST', 'MUTATION'
    title: str
    subtitle: str
    status: str
    details: str
    severity: str = "medium"


class AxiomDashboard(ctk.CTk if HAS_CTK else object):
    """Modern Dark-Themed GUI Dashboard for Axiom Aegis (Multi-Target & Multi-Layer)"""

    def __init__(self, target_dir: str = "."):
        if not HAS_CTK:
            raise RuntimeError("customtkinter is required to launch the GUI dashboard.")
        super().__init__()

        self.title("⚡ AXIOM AEGIS v3.0 — Pure Deterministic Bug Hunter")
        self.geometry("1180x740")
        self.minsize(960, 600)

        # Selected targets (files and folders)
        self.selected_targets: List[str] = [target_dir] if target_dir and target_dir != "." else []
        self.items: List[UIItem] = []
        self.is_executing = False
        self.watcher = CodeWatcher(target_dir=target_dir or ".", callback=self._on_file_changed)

        self._init_layout()
        self._run_scan_async()

    def _init_layout(self):
        # 1. Top Bar
        self.top_bar = ctk.CTkFrame(self, corner_radius=8, height=60)
        self.top_bar.pack(fill="x", padx=16, pady=(16, 6))

        self.lbl_title = ctk.CTkLabel(
            self.top_bar,
            text="⚡ AXIOM AEGIS",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00D2FF",
        )
        self.lbl_title.pack(side="left", padx=16, pady=12)

        self.lbl_stats = ctk.CTkLabel(
            self.top_bar,
            text="⏳ Initializing multi-layer engine...",
            font=ctk.CTkFont(size=13),
        )
        self.lbl_stats.pack(side="left", padx=12)

        self.btn_rerun = ctk.CTkButton(
            self.top_bar,
            text="🔄 Re-run All Layers",
            width=130,
            command=self._run_scan_async,
            fg_color="#1f538d",
            hover_color="#14375e",
        )
        self.btn_rerun.pack(side="right", padx=16, pady=12)

        self.switch_watch = ctk.CTkSwitch(
            self.top_bar,
            text="Live Watch",
            font=ctk.CTkFont(size=13),
            command=self._toggle_watch,
        )
        self.switch_watch.pack(side="right", padx=10)

        # 2. Target Selection Toolbar
        self.target_bar = ctk.CTkFrame(self, corner_radius=6, height=44)
        self.target_bar.pack(fill="x", padx=16, pady=(0, 6))

        self.btn_add_folder = ctk.CTkButton(
            self.target_bar,
            text="📁 Add Folder...",
            width=110,
            height=30,
            fg_color="#2b2b2b",
            hover_color="#3e3e3e",
            command=self._on_add_folder,
        )
        self.btn_add_folder.pack(side="left", padx=(10, 6), pady=6)

        self.btn_add_files = ctk.CTkButton(
            self.target_bar,
            text="📄 Add File(s)...",
            width=110,
            height=30,
            fg_color="#2b2b2b",
            hover_color="#3e3e3e",
            command=self._on_add_files,
        )
        self.btn_add_files.pack(side="left", padx=6, pady=6)

        self.btn_clear_targets = ctk.CTkButton(
            self.target_bar,
            text="🗑️ Reset Workspace",
            width=120,
            height=30,
            fg_color="#3a2525",
            hover_color="#523232",
            command=self._on_clear_targets,
        )
        self.btn_clear_targets.pack(side="left", padx=6, pady=6)

        self.lbl_target_info = ctk.CTkLabel(
            self.target_bar,
            text="🎯 Target: Workspace (.)",
            font=ctk.CTkFont(size=12),
            text_color="#B0B0B0",
            anchor="w",
        )
        self.lbl_target_info.pack(side="left", fill="x", expand=True, padx=12, pady=6)

        # 3. Main Content Split
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=16, pady=(0, 6))

        # Left Column: Findings / Layers + Search Filter
        self.left_frame = ctk.CTkFrame(self.content_frame, width=480)
        self.left_frame.pack(side="left", fill="both", padx=(0, 8), pady=0)
        self.left_frame.pack_propagate(False)

        self.lbl_list_header = ctk.CTkLabel(
            self.left_frame,
            text="📋 Layer Findings & Executions",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.lbl_list_header.pack(anchor="w", padx=12, pady=(8, 4))

        self.search_entry = ctk.CTkEntry(
            self.left_frame,
            placeholder_text="🔍 Filter bugs, patterns, fixes, tests...",
            height=32,
        )
        self.search_entry.pack(fill="x", padx=10, pady=(0, 6))
        self.search_entry.bind("<KeyRelease>", lambda e: self._render_list_items())

        self.scroll_list = ctk.CTkScrollableFrame(self.left_frame)
        self.scroll_list.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Right Column: Inspector Details
        self.right_frame = ctk.CTkFrame(self.content_frame)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(8, 0), pady=0)

        self.lbl_inspector_header = ctk.CTkLabel(
            self.right_frame,
            text="🔍 Inspector & Multi-Layer Evidence",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.lbl_inspector_header.pack(anchor="w", padx=12, pady=(8, 4))

        self.txt_details = ctk.CTkTextbox(
            self.right_frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="none",
        )
        self.txt_details.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        # 4. Bottom Bar
        self.bottom_bar = ctk.CTkFrame(self, height=36, fg_color="transparent")
        self.bottom_bar.pack(side="bottom", fill="x", padx=16, pady=(0, 8))

        self.btn_close = ctk.CTkButton(
            self.bottom_bar,
            text="❌ Close",
            width=90,
            height=28,
            fg_color="#3a3a3a",
            hover_color="#555555",
            command=self._on_close,
        )
        self.btn_close.pack(side="right")

    def _on_add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder to Scan")
        if folder:
            if folder not in self.selected_targets:
                self.selected_targets.append(folder)
            self._update_target_label()
            self._run_scan_async()

    def _on_add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Python Files to Scan",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if files:
            for f in files:
                if f not in self.selected_targets:
                    self.selected_targets.append(f)
            self._update_target_label()
            self._run_scan_async()

    def _on_clear_targets(self):
        self.selected_targets = []
        self._update_target_label()
        self._run_scan_async()

    def _update_target_label(self):
        if not self.selected_targets:
            self.lbl_target_info.configure(text="🎯 Target: Workspace (.)")
        else:
            names = [Path(t).name or t for t in self.selected_targets]
            text = f"🎯 Targets ({len(self.selected_targets)}): " + ", ".join(names[:4])
            if len(names) > 4:
                text += f" (+{len(names)-4} more)"
            self.lbl_target_info.configure(text=text)

    def _toggle_watch(self):
        if self.switch_watch.get() == 1:
            watch_target = self.selected_targets[0] if self.selected_targets else "."
            self.watcher.target_dir = watch_target
            self.watcher.start()
            self.lbl_stats.configure(text="👁️ Live Watch Active — Listening for changes...")
        else:
            self.watcher.stop()
            self.lbl_stats.configure(text="⏸️ Live Watch Disabled")

    def _on_file_changed(self):
        if not self.is_executing:
            self.after(0, self._run_scan_async)

    def _run_scan_async(self):
        if self.is_executing:
            return
        self.is_executing = True
        self.btn_rerun.configure(state="disabled")
        self.btn_add_folder.configure(state="disabled")
        self.btn_add_files.configure(state="disabled")
        self.lbl_stats.configure(text="⏳ Running Layers 1-5 & Engine...", text_color="#E0E0E0")

        threading.Thread(target=self._worker_scan, daemon=True).start()

    def _collect_target_files(self) -> List[Path]:
        ignore_dirs = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".hypothesis", "build", "dist"}
        collected: Set[Path] = set()

        targets = self.selected_targets if self.selected_targets else ["."]

        for t in targets:
            p = Path(t)
            if p.is_file() and p.suffix == ".py":
                collected.add(p)
            elif p.is_dir():
                for sub in p.rglob("*.py"):
                    if not set(sub.parts).intersection(ignore_dirs):
                        collected.add(sub)

        return sorted(list(collected))

    def _worker_scan(self):
        self.watcher.pause()
        items: List[UIItem] = []
        critical_count = 0
        high_count = 0

        try:
            py_files = self._collect_target_files()

            # Initialize all Layer engines
            ast_sentinel = ASTSentinel()
            slicer = CompilationFreeSlicer()
            rule_engine = StaticRuleEngine()
            fix_generator = FixGenerator()
            verifier = DynamicVerifier()
            audit_chain = AuditChain(db_path=":memory:")

            # Layer 3: Cross-Module Context Analyzer (across all collected files)
            if py_files:
                try:
                    context_analyzer = CrossModuleAnalyzer(py_files[:30])
                    context_findings = context_analyzer.analyze()
                    for cf in context_findings:
                        items.append(UIItem(
                            category="CONTEXT",
                            title=f"[CONTEXT] {cf.description}",
                            subtitle=f"{', '.join(cf.function_paths[:2])}",
                            status="ANALYZED",
                            details=f"Layer 3: Cross-Module Context Finding\n\nType: {cf.finding_type.value}\nConfidence: {cf.confidence * 100:.0f}%\nDescription: {cf.description}\nFunctions: {', '.join(cf.function_paths)}\n\nEvidence:\n{json.dumps(cf.evidence, indent=2)}",
                            severity="medium"
                        ))
                except Exception as ex:
                    pass

            # Per-file processing across Layers 1, 2, 3, 4, 5
            for fpath in py_files[:60]:
                str_path = str(fpath)
                try:
                    with open(str_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                except Exception:
                    continue

                # Audit Start
                event_id = audit_chain.log_analysis_start(str_path, "main")

                # Layer 1: AST Sentinel
                try:
                    ast_root, ast_findings = ast_sentinel.parse_file(str_path)
                    for f in ast_findings:
                        sev = f.severity.value if hasattr(f.severity, 'value') else str(f.severity)
                        if sev.lower() == "critical":
                            critical_count += 1
                        elif sev.lower() == "high":
                            high_count += 1
                        items.append(UIItem(
                            category="BUG",
                            title=f"[{sev.upper()}] {f.message}",
                            subtitle=f"{fpath.name}:{f.line_number}",
                            status=sev.upper(),
                            details=f"Layer 1: AST Sentinel Finding\n\nFile: {str_path}:{f.line_number}\nRule: {f.bug_type}\nSeverity: {sev}\n\nEvidence:\n{f.message}\n\nCode Snippet:\n{f.code_snippet}",
                            severity=sev.lower()
                        ))
                except Exception:
                    ast_root = None

                # Layer 2: Compilation-Free Slicing
                try:
                    slicing_ctx = slicer.build(code, str_path)
                except Exception:
                    pass

                # Layer 3: Static Rule Engine (Micro & Macro)
                try:
                    static_res = rule_engine.analyze_file(str_path)
                    findings_list = static_res.get('findings', [])
                    for f in findings_list:
                        sev = f.severity.value if hasattr(f.severity, 'value') else str(f.severity)
                        if sev.lower() == "critical":
                            critical_count += 1
                        elif sev.lower() == "high":
                            high_count += 1
                        items.append(UIItem(
                            category="BUG",
                            title=f"[{sev.upper()}] {f.rule_name}: {f.message}",
                            subtitle=f"{fpath.name}:{f.line_number}",
                            status=sev.upper(),
                            details=f"Layer 3: Static Rule Finding\n\nFile: {str_path}:{f.line_number}\nRule: {f.rule_name} (CWE: {getattr(f, 'cwe', 'N/A')})\nSeverity: {sev}\nDescription: {f.message}\nFix Suggestion: {getattr(f, 'fix_suggestion', 'N/A')}\n\nCode:\n{f.code_snippet}",
                            severity=sev.lower()
                        ))
                except Exception:
                    findings_list = []

                # Layer 3: Pattern Mining
                if ast_root:
                    try:
                        miner = PatternMiner(ast_root, str_path)
                        p_matches = miner.mine_patterns()
                        for pm in p_matches:
                            items.append(UIItem(
                                category="PATTERN",
                                title=f"[PATTERN] {pm.pattern_type.value}: {pm.description}",
                                subtitle=f"{fpath.name}:{pm.line_number}",
                                status="MINED",
                                details=f"Layer 3: Pattern Mining Engine\n\nFile: {str_path}:{pm.line_number}\nCategory: {pm.category.value}\nPattern: {pm.pattern_type.value}\nSeverity: {pm.severity}\nDescription: {pm.description}\n\nCode Snippet:\n{pm.code_snippet}",
                                severity=pm.severity.lower() if hasattr(pm.severity, 'lower') else "low"
                            ))
                    except Exception:
                        pass

                # Layer 4: Fix Generator
                try:
                    fixes = fix_generator.generate_fixes(code)
                    for fix in fixes:
                        items.append(UIItem(
                            category="FIX",
                            title=f"[AUTO-FIX] {fix.template.bug_type} ({fix.confidence * 100:.0f}% confidence)",
                            subtitle=f"{fpath.name}",
                            status="SUGGESTED",
                            details=f"Layer 4: Deterministic Fix Suggestion\n\nFile: {str_path}\nBug Type: {fix.template.bug_type}\nDescription: {fix.template.description}\nConfidence: {fix.confidence * 100:.0f}%\n\nSuggested Code Replacement:\n{fix.fixed}",
                            severity="medium"
                        ))
                except Exception:
                    pass

                # Layer 4: Benchmark Analyzer
                if ast_root:
                    try:
                        bench = BenchmarkAnalyzer(ast_root, str_path)
                        b_summary = bench.analyze()
                        for cf in b_summary.get('complexity_issues', []):
                            items.append(UIItem(
                                category="BENCHMARK",
                                title=f"[PERF] {cf.description}",
                                subtitle=f"{fpath.name}:{cf.line_number}",
                                status="COMPLEXITY",
                                details=f"Layer 4: Benchmark Performance Issue\n\nFile: {str_path}:{cf.line_number}\nType: {cf.complexity_type.value}\nEstimated Complexity: {cf.estimated_complexity}\nDescription: {cf.description}\nRecommendation: {cf.recommendation}",
                                severity="medium"
                            ))
                    except Exception:
                        pass

                # Layer 5: Audit End
                audit_chain.log_analysis_end(event_id, len(findings_list), 0)

            # Pytest Smoke Run
            try:
                proc = subprocess.run(["pytest", "-q", "--tb=short", "tests/"], capture_output=True, text=True, timeout=10)
                status_text = "PASSED" if proc.returncode == 0 else "FAILED"
                items.append(UIItem(
                    category="TEST",
                    title=f"Pytest Test Suite ({status_text})",
                    subtitle="tests/",
                    status=status_text,
                    details=f"Pytest Execution Results\n\nExit Code: {proc.returncode}\n\nSTDOUT:\n{proc.stdout}\n\nSTDERR:\n{proc.stderr}",
                    severity="critical" if proc.returncode != 0 else "low"
                ))
            except Exception as e:
                pass

            self.items = items
            self.scan_stats = {
                'files': len(py_files),
                'bugs': len([i for i in items if i.category in ("BUG", "PATTERN")]),
                'critical': critical_count,
                'high': high_count,
                'fixes': len([i for i in items if i.category == "FIX"])
            }
        finally:
            self.watcher.resume()
            self.after(0, self._update_ui_results)

    def _update_ui_results(self):
        self.is_executing = False
        self.btn_rerun.configure(state="normal")
        self.btn_add_folder.configure(state="normal")
        self.btn_add_files.configure(state="normal")
        stats = getattr(self, "scan_stats", {'files': 0, 'bugs': 0, 'critical': 0, 'high': 0, 'fixes': 0})

        stats_text = (
            f"📁 {stats['files']} Files | 🐛 {stats['bugs']} Issues | "
            f"🔴 {stats['critical']} Critical | 🟠 {stats['high']} High | 💡 {stats.get('fixes', 0)} Fixes"
        )
        self.lbl_stats.configure(text=stats_text)
        self._render_list_items()

        if self.items:
            self._show_detail(self.items[0])

    def _render_list_items(self):
        query = self.search_entry.get().strip().lower()

        for widget in self.scroll_list.winfo_children():
            widget.destroy()

        for item in self.items:
            if query and query not in item.title.lower() and query not in item.subtitle.lower() and query not in item.details.lower():
                continue

            if item.category == "BUG":
                icon = "🔴" if item.severity == "critical" else "🟠" if item.severity == "high" else "🟡"
                fg = "#4a1c1c" if item.severity in ("critical", "high") else "#3a3a1c"
                hover = "#6e2525" if item.severity in ("critical", "high") else "#525227"
            elif item.category == "FIX":
                icon = "💡"
                fg = "#1f3b4d"
                hover = "#2a4f66"
            elif item.category == "PATTERN":
                icon = "🧬"
                fg = "#38294a"
                hover = "#4d3966"
            elif item.category == "CONTEXT":
                icon = "🌐"
                fg = "#253b3b"
                hover = "#345252"
            elif item.category == "BENCHMARK":
                icon = "⚡"
                fg = "#3d331f"
                hover = "#52452a"
            else:
                icon = "✅" if item.status == "PASSED" else "❌"
                fg = "#1c3a28" if item.status == "PASSED" else "#4a1c1c"
                hover = "#255238" if item.status == "PASSED" else "#6e2525"

            btn_text = f"{icon} {item.title}\n   └─ {item.subtitle}"

            btn = ctk.CTkButton(
                self.scroll_list,
                text=btn_text,
                anchor="w",
                font=ctk.CTkFont(size=12),
                fg_color=fg,
                hover_color=hover,
                command=lambda it=item: self._show_detail(it),
            )
            btn.pack(fill="x", padx=4, pady=3)

    def _show_detail(self, item: UIItem):
        self.txt_details.delete("1.0", "end")
        header = f"[{item.category}] {item.title}\nTarget: {item.subtitle}\nStatus: {item.status}\n"
        header += "=" * 70 + "\n\n"
        self.txt_details.insert("end", header + item.details)

    def _on_close(self):
        self.watcher.stop()
        self.destroy()


def launch_ui(target_dir: str = "."):
    """Launch the Axiom Aegis GUI Dashboard"""
    if not HAS_CTK:
        print("❌ Error: customtkinter is not installed.")
        print("   Install it using: pip install customtkinter")
        return
    app = AxiomDashboard(target_dir=target_dir)
    app.mainloop()


if __name__ == "__main__":
    launch_ui()
