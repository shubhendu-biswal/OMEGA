import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sandbox.executor import SandboxExecutor

def test_compilation(language, code):
    executor = SandboxExecutor(timeout_sec=5)
    res = executor.execute(language, code)
    return res["success"], res.get("stderr", "")

if __name__ == "__main__":
    success, err = test_compilation("Python", "print('Compile test passed')")
    print("Compilation Test:", success, err)
