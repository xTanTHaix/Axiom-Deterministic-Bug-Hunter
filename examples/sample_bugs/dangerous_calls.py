"""
Sample Python file with dangerous function calls (for testing Layer 1 & Layer 3)
"""

import os
import subprocess


def execute_user_command(user_input: str):
    # Dangerous: os.popen allows command injection
    result = os.popen(user_input).read()
    return result


def dynamic_calculation(expression: str):
    # Dangerous: eval allows arbitrary code execution
    return eval(expression)


def run_shell(cmd: str):
    # Dangerous: subprocess with shell=True
    subprocess.call(cmd, shell=True)
