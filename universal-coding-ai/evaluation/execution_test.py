import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sandbox.executor import SandboxExecutor

def test_execution(language, code):
    executor = SandboxExecutor(timeout_sec=5)
    res = executor.execute(language, code)
    return res["success"], res.get("stdout", ""), res.get("stderr", "")

if __name__ == "__main__":
    success, out, err = test_execution("Java", "public class Solution { public static void main(String[] args) { System.out.println(\"Java Sandbox Execution Test Passed\"); } }")
    print("Execution Test:", success, out.strip())
