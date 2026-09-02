import ast
import subprocess
import copy
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import pytest

IGNORE_DIRS = {
    ".git", ".venv", "venv", "myenv", "env", "__pycache__",
    ".pytest_cache", ".hypothesis", "build", "dist", "axiom"
}


@dataclass
class Mutant:
    file_path: str
    line_number: int
    original_op: str
    mutated_op: str
    status: str = "PENDING"


@dataclass
class MutationReport:
    total_mutants: int = 0
    killed: int = 0
    survived: int = 0
    score: float = 0.0
    mutants: List[Mutant] = field(default_factory=list)


class ASTMutator(ast.NodeTransformer):
    OP_MAP = {
        ast.Add: ast.Sub,
        ast.Sub: ast.Add,
        ast.Mult: ast.FloorDiv,
        ast.Eq: ast.NotEq,
        ast.NotEq: ast.Eq,
        ast.Lt: ast.GtE,
        ast.Gt: ast.LtE,
        ast.LtE: ast.Gt,
        ast.GtE: ast.Lt,
    }

    def __init__(self, target_index: int):
        super().__init__()
        self.target_index = target_index
        self.current_index = 0
        self.applied_mutation: Optional[Tuple[int, str, str]] = None

    def visit_BinOp(self, node):
        self.generic_visit(node)
        op_type = type(node.op)
        if op_type in self.OP_MAP:
            if self.current_index == self.target_index:
                new_op = self.OP_MAP[op_type]()
                self.applied_mutation = (
                    node.lineno,
                    op_type.__name__,
                    type(new_op).__name__,
                )
                node.op = new_op
            self.current_index += 1
        return node

    def visit_Compare(self, node):
        self.generic_visit(node)
        if node.ops:
            op_type = type(node.ops[0])
            if op_type in self.OP_MAP:
                if self.current_index == self.target_index:
                    new_op = self.OP_MAP[op_type]()
                    self.applied_mutation = (
                        node.lineno,
                        op_type.__name__,
                        type(new_op).__name__,
                    )
                    node.ops[0] = new_op
                self.current_index += 1
        return node


def scan_all_project_files() -> List[str]:
    """สแกนหาไฟล์ .py ทั้งหมดใน Workspace ที่ไม่ใช่ไฟล์ Test หรือ Virtualenv"""
    target_files = []
    for path in Path(".").rglob("*.py"):
        parts = set(path.parts)
        if not parts.intersection(IGNORE_DIRS):
            if not path.name.startswith("test_") and not path.name.endswith("_test.py"):
                target_files.append(str(path))
    return target_files


def get_git_changed_files() -> List[str]:
    """ดึงไฟล์เฉพาะที่มีการแก้ไขใน Git"""
    try:
        cmd = ["git", "diff", "--name-only", "HEAD"]
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        files = [
            f for f in output.splitlines()
            if f.endswith(".py") and not f.startswith("tests/") and not Path(f).name.startswith("test_")
        ]
        if files:
            return files
    except Exception:
        pass
    return []


def run_delta_mutation(target_files: Optional[List[str]] = None) -> MutationReport:
    report = MutationReport()
    files_to_mutate = target_files or get_git_changed_files() or scan_all_project_files()

    for file_path in files_to_mutate[:10]:  # จำกัดไฟล์เพื่อความเร็ว
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
        except Exception:
            continue

        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            continue

        mutator_counter = ASTMutator(target_index=-1)
        mutator_counter.visit(copy.deepcopy(tree))
        total_mutation_points = mutator_counter.current_index

        for idx in range(min(total_mutation_points, 5)):  # ทำ sampling ต่อไฟล์
            mutator = ASTMutator(target_index=idx)
            mutated_tree = mutator.visit(copy.deepcopy(tree))
            ast.fix_missing_locations(mutated_tree)

            if not mutator.applied_mutation:
                continue

            lineno, orig_op, mut_op = mutator.applied_mutation
            mutant = Mutant(
                file_path=file_path,
                line_number=lineno,
                original_op=orig_op,
                mutated_op=mut_op,
            )

            mutated_code = ast.unparse(mutated_tree)
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(mutated_code)

                exit_code = pytest.main(["-q", "."], plugins=[])
                if exit_code != 0:
                    mutant.status = "KILLED"
                    report.killed += 1
                else:
                    mutant.status = "SURVIVED"
                    report.survived += 1
            finally:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(source_code)

            report.total_mutants += 1
            report.mutants.append(mutant)

    if report.total_mutants > 0:
        report.score = (report.killed / report.total_mutants) * 100.0

    return report