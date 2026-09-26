import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from sandbox.executor import SandboxExecutor
from training.inference import UniversalCodingInferenceEngine

class SelfCorrectionEngine:
    def __init__(self, max_attempts=3):
        self.max_attempts = max_attempts
        self.executor = SandboxExecutor(timeout_sec=5)
        self.inference = UniversalCodingInferenceEngine()

    def solve_with_self_correction(self, problem: str, language: str) -> dict:
        attempts = 0
        solution_res = self.inference.solve(problem, language)
        code = solution_res.get("code", "")

        history = []

        while attempts < self.max_attempts:
            attempts += 1
            exec_res = self.executor.execute(language, code)

            if exec_res["success"]:
                solution_res["attempts"] = attempts
                solution_res["validated"] = True
                solution_res["correction_history"] = history
                return solution_res

            # Feedback error loop
            error_msg = exec_res.get("stderr", "Execution failed.")
            history.append({"attempt": attempts, "code": code, "error": error_msg})

            print(f"Self-Correction Attempt {attempts}/{self.max_attempts} Failed ({language}): {error_msg[:80]}")

            # Feedback correction prompt formulation
            correction_prompt = f"{problem}\n\nPrevious attempt failed with error:\n{error_msg}\n\nPlease fix the code."
            corrected_res = self.inference.solve(correction_prompt, language)
            code = corrected_res.get("code", "")
            solution_res = corrected_res

        solution_res["attempts"] = attempts
        solution_res["validated"] = False
        solution_res["correction_history"] = history
        return solution_res

if __name__ == "__main__":
    corrector = SelfCorrectionEngine(max_attempts=3)
    res = corrector.solve_with_self_correction("Write a function that calculates total array sum", "Python")
    print(f"Self-Correction Result: Validated={res['validated']}, Attempts={res['attempts']}")
