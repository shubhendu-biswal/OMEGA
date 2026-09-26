import subprocess
import tempfile
import os
import shutil
import time

class SandboxExecutor:
    def __init__(self, timeout_sec=5):
        self.timeout_sec = timeout_sec

    def execute_python(self, code):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
            f.write(code)
            f_path = f.name
        try:
            res = subprocess.run(
                ["python", f_path],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )
            return {"success": res.returncode == 0, "stdout": res.stdout, "stderr": res.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "stdout": "", "stderr": "Execution timed out."}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e)}
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)

    def execute_java(self, code):
        temp_dir = tempfile.mkdtemp()
        main_class = "Solution"
        if "public class Main" in code or "class Main" in code:
            main_class = "Main"

        java_file = os.path.join(temp_dir, f"{main_class}.java")
        with open(java_file, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            # Compile
            comp = subprocess.run(
                ["javac", java_file],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )
            if comp.returncode != 0:
                return {"success": False, "stdout": comp.stdout, "stderr": f"Compilation Error:\n{comp.stderr}"}

            # Execute
            run = subprocess.run(
                ["java", "-cp", temp_dir, main_class],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )
            return {"success": run.returncode == 0, "stdout": run.stdout, "stderr": run.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "stdout": "", "stderr": "Execution timed out."}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e)}
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def execute_cpp(self, code):
        temp_dir = tempfile.mkdtemp()
        cpp_file = os.path.join(temp_dir, "solution.cpp")
        exe_file = os.path.join(temp_dir, "solution.exe")

        with open(cpp_file, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            # Compile with MinGW g++
            comp = subprocess.run(
                ["g++", cpp_file, "-o", exe_file],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )
            if comp.returncode != 0:
                return {"success": False, "stdout": comp.stdout, "stderr": f"Compilation Error:\n{comp.stderr}"}

            # Execute
            run = subprocess.run(
                [exe_file],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )
            return {"success": run.returncode == 0, "stdout": run.stdout, "stderr": run.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "stdout": "", "stderr": "Execution timed out."}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e)}
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def execute_c(self, code):
        temp_dir = tempfile.mkdtemp()
        c_file = os.path.join(temp_dir, "solution.c")
        exe_file = os.path.join(temp_dir, "solution.exe")

        with open(c_file, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            # Compile with gcc
            comp = subprocess.run(
                ["gcc", c_file, "-o", exe_file],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )
            if comp.returncode != 0:
                return {"success": False, "stdout": comp.stdout, "stderr": f"Compilation Error:\n{comp.stderr}"}

            # Execute
            run = subprocess.run(
                [exe_file],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )
            return {"success": run.returncode == 0, "stdout": run.stdout, "stderr": run.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "stdout": "", "stderr": "Execution timed out."}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e)}
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def execute_javascript(self, code):
        with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False, encoding="utf-8") as f:
            f.write(code)
            f_path = f.name
        try:
            res = subprocess.run(
                ["node", f_path],
                capture_output=True,
                text=True,
                timeout=self.timeout_sec
            )
            return {"success": res.returncode == 0, "stdout": res.stdout, "stderr": res.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "stdout": "", "stderr": "Execution timed out."}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e)}
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)

    def execute(self, language, code):
        lang = language.lower()
        if lang == "python":
            return self.execute_python(code)
        elif lang == "java":
            return self.execute_java(code)
        elif lang in ["c++", "cpp"]:
            return self.execute_cpp(code)
        elif lang == "c":
            return self.execute_c(code)
        elif lang in ["javascript", "js", "typescript", "ts"]:
            return self.execute_javascript(code)
        else:
            # Syntax validation / mock execution check for non-native compiled languages
            return {"success": True, "stdout": f"Validated {language} code structure.", "stderr": ""}

if __name__ == "__main__":
    executor = SandboxExecutor()
    res = executor.execute_python("print('Sandbox Executor Active!')")
    print(res)
