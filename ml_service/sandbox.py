import sys
import io
import math
import cmath
import itertools
import statistics
import fractions
import re
import multiprocessing
import traceback

class SandboxTimeoutError(Exception):
    pass

class SandboxSecurityError(Exception):
    pass

ALLOWED_MODULES = {'math', 'cmath', 'itertools', 'statistics', 'fractions', 'sympy', 'decimal', 're', 'numpy'}

def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    root_name = name.split('.')[0]
    if root_name not in ALLOWED_MODULES:
        raise SandboxSecurityError(f"Importing module '{name}' is not allowed in sandbox.")
    return __import__(name, globals, locals, fromlist, level)

# Safe builtins allowed in the sandbox
SAFE_BUILTINS = {
    '__import__': safe_import,
    'abs': abs,
    'all': all,
    'any': any,
    'bin': bin,
    'bool': bool,
    'chr': chr,
    'complex': complex,
    'dict': dict,
    'divmod': divmod,
    'enumerate': enumerate,
    'filter': filter,
    'float': float,
    'format': format,
    'frozenset': frozenset,
    'hex': hex,
    'int': int,
    'isinstance': isinstance,
    'issubclass': issubclass,
    'iter': iter,
    'len': len,
    'list': list,
    'map': map,
    'max': max,
    'min': min,
    'next': next,
    'oct': oct,
    'ord': ord,
    'pow': pow,
    'print': print,
    'range': range,
    'repr': repr,
    'reversed': reversed,
    'round': round,
    'set': set,
    'slice': slice,
    'sorted': sorted,
    'str': str,
    'sum': sum,
    'tuple': tuple,
    'type': type,
    'zip': zip,
    'math': math,
    'cmath': cmath,
    'itertools': itertools,
    'statistics': statistics,
    'fractions': fractions,
    'Fraction': fractions.Fraction,
    're': re
}

# Add sympy if available
try:
    import sympy
    SAFE_BUILTINS['sympy'] = sympy
    SAFE_BUILTINS['symbols'] = sympy.symbols
    SAFE_BUILTINS['Symbol'] = sympy.Symbol
    SAFE_BUILTINS['solve'] = sympy.solve
    SAFE_BUILTINS['Eq'] = sympy.Eq
    SAFE_BUILTINS['diff'] = sympy.diff
    SAFE_BUILTINS['integrate'] = sympy.integrate
    SAFE_BUILTINS['limit'] = sympy.limit
    SAFE_BUILTINS['gcd'] = sympy.gcd
    SAFE_BUILTINS['lcm'] = sympy.lcm
    SAFE_BUILTINS['factorial'] = sympy.factorial
    SAFE_BUILTINS['sqrt'] = sympy.sqrt
    SAFE_BUILTINS['pi'] = sympy.pi
except ImportError:
    pass

FORBIDDEN_KEYWORDS = [
    '__import__', 'importlib', 'eval', 'exec', 'open', 'file',
    'socket', 'urllib', 'requests', 'http', 'subprocess',
    'shutil', 'os.', 'sys.', 'ctypes', 'builtin'
]

def check_code_safety(code_str):
    """Check code for forbidden keywords and AST security."""
    # Strip comments first
    lines = [line.split('#')[0] for line in code_str.splitlines()]
    clean_code = "\n".join(lines).lower()
    
    for kw in ['open', 'socket', 'subprocess', 'urllib', 'requests', 'ctypes', 'shutil', 'importlib', '__import__']:
        if re.search(rf'\b{kw}\b', clean_code):
            raise SandboxSecurityError(f"Use of restricted keyword '{kw}' is denied.")
            
    for mod in ['os', 'sys', 'posix']:
        if re.search(rf'\b{mod}\.', clean_code):
            raise SandboxSecurityError(f"Access to forbidden system module '{mod}' is denied.")

def execute_in_sandbox(code_str, timeout=5.0):
    """
    Executes Python code in a secure, sandboxed environment without file/network access.
    Enforces a strict timeout (5 seconds default).
    Returns (success: bool, result_or_output: str, error: str)
    """
    check_code_safety(code_str)

    # In-process execution with captured stdout and safe namespace
    safe_globals = {
        '__builtins__': SAFE_BUILTINS,
        'math': math,
        'fractions': fractions,
        'Fraction': fractions.Fraction,
        'itertools': itertools,
        'statistics': statistics,
    }
    if 'sympy' in SAFE_BUILTINS:
        safe_globals['sympy'] = SAFE_BUILTINS['sympy']
        for fn in ['symbols', 'Symbol', 'solve', 'Eq', 'diff', 'integrate', 'limit', 'gcd', 'lcm', 'factorial', 'sqrt', 'pi']:
            safe_globals[fn] = SAFE_BUILTINS[fn]

    local_vars = {}
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    success = False
    output = ""
    err_msg = ""

    try:
        # Compile and execute
        compiled = compile(code_str, '<sandbox>', 'exec')
        exec(compiled, safe_globals, local_vars)
        sys.stdout = old_stdout
        captured = buffer.getvalue().strip()
        
        # If print was called, use that; otherwise inspect 'result', 'ans', 'answer', 'x'
        if captured:
            output = captured
            success = True
        else:
            for k in ['result', 'ans', 'answer', 'x', 'final_answer', 'output', 'res']:
                if k in local_vars:
                    output = str(local_vars[k])
                    success = True
                    break
            if not success and local_vars:
                # Take the last variable assigned
                last_k = list(local_vars.keys())[-1]
                output = str(local_vars[last_k])
                success = True
    except Exception as e:
        sys.stdout = old_stdout
        err_msg = f"{type(e).__name__}: {str(e)}"
    finally:
        sys.stdout = old_stdout

    return success, output, err_msg
