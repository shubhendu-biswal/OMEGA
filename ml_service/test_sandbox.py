from sandbox import execute_in_sandbox

s1, o1, e1 = execute_in_sandbox("result = 35 * 42")
print("Test 1 (arithmetic):", s1, "Output:", o1, "Error:", e1)

s2, o2, e2 = execute_in_sandbox("""
x = symbols('x')
ans = solve(Eq(5*x - 25, 20), x)[0]
print(ans)
""")
print("Test 2 (sympy algebra):", s2, "Output:", o2, "Error:", e2)

try:
    s3, o3, e3 = execute_in_sandbox("open('test.txt', 'w')")
    print("Test 3 (security blocked):", s3, o3, e3)
except Exception as ex:
    print("Test 3 (security blocked): True Exception caught:", type(ex).__name__, ex)
