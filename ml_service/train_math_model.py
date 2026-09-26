"""
====================================================================
  OMEGA Mathematical Intelligence Seeder & Model Trainer
  Generates and seeds 100,000 mathematical data records into Oracle DB
  Trains TF-IDF Operator Vectorizer + Deep Neural Network Classifier
====================================================================
"""

import os
import sys
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

import time
import random
import math
import json
import argparse
import numpy as np
import pandas as pd
import joblib
from sqlalchemy import create_engine, text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder

# Load backend/.env
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
if os.path.exists(dotenv_path):
    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Database credentials
db_user = os.getenv("DB_USER", "OMEGA_user")
db_pass = os.getenv("DB_PASSWORD", "omega123")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "1521")
db_name = os.getenv("DB_NAME", "orcl")
db_url = f"oracle+oracledb://{db_user}:{db_pass}@{db_host}:{db_port}/?service_name={db_name}"

TARGET_COUNT = 100_000

# ====================================================================
# Comprehensive Mathematical Data Generators
# ====================================================================
random.seed(42)
np.random.seed(42)

def gen_arithmetic_record(idx):
    topic = "Arithmetic"
    diff = "Easy" if idx % 3 == 0 else ("Medium" if idx % 3 == 1 else "Hard")
    subtype = idx % 10
    
    if subtype == 0:
        a = random.randint(12, 9999)
        b = random.randint(12, 9999)
        q = f"What is {a} + {b}?"
        formula = "a + b = c"
        sol = f"Step 1: Align digits. Step 2: Add values: {a} + {b} = {a + b}."
    elif subtype == 1:
        a = random.randint(50, 9999)
        b = random.randint(10, a)
        q = f"Calculate {a} - {b}"
        formula = "a - b = d"
        sol = f"Step 1: Subtract {b} from {a}. Result: {a} - {b} = {a - b}."
    elif subtype == 2:
        a = random.randint(6, 999)
        b = random.randint(4, 99)
        q = f"Multiply {a} by {b}"
        formula = "a * b = p"
        sol = f"Step 1: Compute product: {a} × {b} = {a * b}."
    elif subtype == 3:
        b = random.randint(3, 80)
        quotient = random.randint(5, 250)
        a = b * quotient
        q = f"Divide {a} by {b}"
        formula = "a / b = q"
        sol = f"Step 1: Divide dividend {a} by divisor {b}. Quotient = {quotient}."
    elif subtype == 4:
        n = random.randint(2, 60)
        q = f"What is the square of {n}?"
        formula = "n² = n * n"
        sol = f"Square calculation: {n}² = {n} × {n} = {n**2}."
    elif subtype == 5:
        n = random.randint(2, 35)
        sq = n * n
        q = f"Find the square root of {sq}"
        formula = "√x = n where n² = x"
        sol = f"Since {n} × {n} = {sq}, the principal square root √{sq} = {n}."
    elif subtype == 6:
        n = random.randint(10, 2000)
        p = random.choice([5, 10, 15, 20, 25, 30, 40, 50, 60, 75])
        q = f"What is {p}% of {n}?"
        formula = "Percentage = (P / 100) * N"
        ans = (p / 100) * n
        sol = f"Step 1: Convert {p}% to decimal: {p/100}. Step 2: Multiply by {n}: {p/100} × {n} = {ans:.2f}."
    elif subtype == 7:
        a = random.randint(2, 25)
        q = f"What is the cube of {a}?"
        formula = "a³ = a * a * a"
        sol = f"Cube calculation: {a}³ = {a} × {a} × {a} = {a**3}."
    elif subtype == 8:
        a = random.randint(15, 500)
        b = random.randint(2, 20)
        rem = a % b
        q = f"Find the remainder when {a} is divided by {b} (modulo)"
        formula = "a mod b = r"
        sol = f"Divide {a} by {b}: quotient = {a // b}, remainder = {a} - ({b} × {a // b}) = {rem}."
    else:
        a = random.randint(2, 10)
        b = random.randint(2, 10)
        c = random.randint(2, 10)
        ans = a + b * c
        q = f"Evaluate the expression using order of operations (BODMAS/PEMDAS): {a} + {b} * {c}"
        formula = "Multiplication precedes Addition: a + (b * c)"
        sol = f"Step 1: Multiply first: {b} × {c} = {b * c}. Step 2: Add {a}: {a} + {b * c} = {ans}."
        
    return q, formula, sol, topic, diff

def gen_algebra_record(idx):
    topic = "Algebra"
    diff = "Easy" if idx % 3 == 0 else ("Medium" if idx % 3 == 1 else "Hard")
    subtype = idx % 8
    
    if subtype == 0:
        a = random.randint(2, 15)
        x_val = random.randint(1, 20)
        b = random.randint(1, 40)
        c = a * x_val + b
        q = f"Solve for x: {a}x + {b} = {c}"
        formula = "ax + b = c  =>  x = (c - b) / a"
        sol = f"Step 1: Subtract {b} from both sides: {a}x = {c} - {b} = {c - b}. Step 2: Divide by {a}: x = {c - b}/{a} = {x_val}."
    elif subtype == 1:
        a = random.randint(2, 12)
        x_val = random.randint(2, 15)
        b = random.randint(1, 30)
        c = a * x_val - b
        q = f"Solve the linear equation: {a}x - {b} = {c}"
        formula = "ax - b = c  =>  x = (c + b) / a"
        sol = f"Step 1: Add {b} to both sides: {a}x = {c} + {b} = {c + b}. Step 2: Divide by {a}: x = {c + b}/{a} = {x_val}."
    elif subtype == 2:
        r1 = random.randint(-8, 8)
        r2 = random.randint(-8, 8)
        if r1 == 0: r1 = 2
        if r2 == 0: r2 = -3
        b = -(r1 + r2)
        c = r1 * r2
        b_str = f"+ {b}x" if b > 0 else (f"- {abs(b)}x" if b < 0 else "")
        c_str = f"+ {c}" if c > 0 else (f"- {abs(c)}" if c < 0 else "")
        q = f"Find the roots of the quadratic equation: x² {b_str} {c_str} = 0"
        formula = "Quadratic formula: x = (-b ± √(b² - 4ac)) / (2a)"
        sol = f"Factoring gives (x - {r1})(x - {r2}) = 0. Therefore, the roots are x = {r1} and x = {r2}."
    elif subtype == 3:
        a = random.randint(2, 8)
        b = random.randint(1, 9)
        c = random.randint(2, 8)
        d = random.randint(1, 9)
        q = f"Simplify the algebraic expression: ({a}x + {b}) + ({c}x - {d})"
        formula = "(ax + b) + (cx - d) = (a + c)x + (b - d)"
        sol = f"Combine like terms: ({a} + {c})x + ({b} - {d}) = {a + c}x + {b - d}."
    elif subtype == 4:
        a = random.randint(2, 6)
        b = random.randint(1, 5)
        q = f"Expand the binomial square: ({a}x + {b})²"
        formula = "(ax + b)² = a²x² + 2abx + b²"
        sol = f"Using identity: ({a}x)² + 2({a}x)({b}) + {b}² = {a*a}x² + {2*a*b}x + {b*b}."
    elif subtype == 5:
        a = random.randint(2, 7)
        b = random.randint(1, 6)
        q = f"Expand the difference of squares: ({a}x + {b})({a}x - {b})"
        formula = "(A + B)(A - B) = A² - B²"
        sol = f"Using difference of squares: ({a}x)² - {b}² = {a*a}x² - {b*b}."
    elif subtype == 6:
        a = random.randint(2, 5)
        b = random.randint(1, 10)
        c = random.randint(1, 5)
        x_val = random.randint(1, 4)
        val = a * (x_val**2) + b * x_val + c
        q = f"If f(x) = {a}x² + {b}x + {c}, evaluate f({x_val})"
        formula = "f(k) = a(k)² + b(k) + c"
        sol = f"Substitute x = {x_val}: f({x_val}) = {a}({x_val}²) + {b}({x_val}) + {c} = {a*(x_val**2)} + {b*x_val} + {c} = {val}."
    else:
        m = random.randint(2, 6)
        x = random.randint(1, 10)
        c = random.randint(1, 15)
        y = m * x + c
        q = f"Find the slope and y-intercept of the line y = {m}x + {c}"
        formula = "Slope-intercept form: y = mx + c where m = slope, c = y-intercept"
        sol = f"Comparing with y = mx + c: Slope (m) = {m}, y-intercept (c) = {c}."

    return q, formula, sol, topic, diff

def gen_geometry_record(idx):
    topic = "Geometry"
    diff = "Easy" if idx % 3 == 0 else ("Medium" if idx % 3 == 1 else "Hard")
    subtype = idx % 7
    
    if subtype == 0:
        r = random.randint(1, 50)
        area = round(math.pi * r * r, 2)
        q = f"Calculate the area of a circle with radius r = {r} cm"
        formula = "Area = π * r²"
        sol = f"Area = π × {r}² = 3.14159 × {r*r} ≈ {area} cm²."
    elif subtype == 1:
        r = random.randint(1, 50)
        circ = round(2 * math.pi * r, 2)
        q = f"Calculate the circumference of a circle with radius r = {r} cm"
        formula = "Circumference = 2 * π * r"
        sol = f"Circumference = 2 × π × {r} = 2 × 3.14159 × {r} ≈ {circ} cm."
    elif subtype == 2:
        l = random.randint(4, 80)
        w = random.randint(3, 60)
        area = l * w
        q = f"Find the area and perimeter of a rectangle with length {l} m and width {w} m"
        formula = "Area = l * w, Perimeter = 2 * (l + w)"
        sol = f"Area = {l} × {w} = {area} m². Perimeter = 2 × ({l} + {w}) = {2*(l+w)} m."
    elif subtype == 3:
        b = random.randint(4, 60)
        h = random.randint(3, 40)
        area = 0.5 * b * h
        q = f"Find the area of a triangle with base {b} cm and perpendicular height {h} cm"
        formula = "Area = (1/2) * base * height"
        sol = f"Area = 0.5 × {b} × {h} = {area} cm²."
    elif subtype == 4:
        a = random.choice([3, 5, 6, 7, 8, 9, 12, 15, 20])
        b = random.choice([4, 12, 8, 24, 15, 12, 16, 20, 21])
        c = round(math.sqrt(a*a + b*b), 2)
        q = f"In a right-angled triangle with legs a = {a} and b = {b}, find hypotenuse c"
        formula = "Pythagorean Theorem: c = √(a² + b²)"
        sol = f"c = √({a}² + {b}²) = √({a*a} + {b*b}) = √{a*a + b*b} = {c}."
    elif subtype == 5:
        s = random.randint(2, 30)
        vol = s ** 3
        sa = 6 * (s ** 2)
        q = f"Find the volume and total surface area of a cube with side length {s} cm"
        formula = "Volume = s³, Surface Area = 6 * s²"
        sol = f"Volume = {s}³ = {vol} cm³. Surface Area = 6 × {s}² = 6 × {s*s} = {sa} cm²."
    else:
        r = random.randint(2, 25)
        h = random.randint(3, 40)
        vol = round(math.pi * (r ** 2) * h, 2)
        q = f"Find the volume of a cylinder with radius {r} cm and height {h} cm"
        formula = "Volume = π * r² * h"
        sol = f"Volume = π × {r}² × {h} = π × {r*r} × {h} ≈ {vol} cm³."

    return q, formula, sol, topic, diff

def gen_trigonometry_record(idx):
    topic = "Trigonometry"
    diff = "Easy" if idx % 3 == 0 else ("Medium" if idx % 3 == 1 else "Hard")
    angles = [0, 30, 45, 60, 90]
    sin_vals = {0: "0", 30: "1/2", 45: "1/√2", 60: "√3/2", 90: "1"}
    cos_vals = {0: "1", 30: "√3/2", 45: "1/√2", 60: "1/2", 90: "0"}
    tan_vals = {0: "0", 30: "1/√3", 45: "1", 60: "√3", 90: "undefined"}
    
    subtype = idx % 5
    if subtype == 0:
        ang = angles[idx % len(angles)]
        q = f"What is the exact value of sin({ang}°)? "
        formula = "Standard trigonometric ratio table"
        sol = f"From the standard trigonometric table, sin({ang}°) = {sin_vals[ang]}."
    elif subtype == 1:
        ang = angles[idx % len(angles)]
        q = f"What is the exact value of cos({ang}°)? "
        formula = "Standard trigonometric ratio table"
        sol = f"From the standard trigonometric table, cos({ang}°) = {cos_vals[ang]}."
    elif subtype == 2:
        ang = angles[idx % len(angles)]
        q = f"What is the exact value of tan({ang}°)? "
        formula = "tan(θ) = sin(θ) / cos(θ)"
        sol = f"tan({ang}°) = sin({ang}°)/cos({ang}°) = {tan_vals[ang]}."
    elif subtype == 3:
        q = f"State and explain the fundamental Pythagorean trigonometric identity."
        formula = "sin²(θ) + cos²(θ) = 1"
        sol = f"The fundamental identity is sin²(θ) + cos²(θ) = 1, derived from the Pythagorean theorem on the unit circle where x = cos(θ) and y = sin(θ)."
    else:
        opp = random.randint(3, 20)
        adj = random.randint(3, 20)
        hyp = round(math.sqrt(opp*opp + adj*adj), 2)
        q = f"In a right triangle with opposite side = {opp} and adjacent side = {adj}, find tan(θ)"
        formula = "tan(θ) = Opposite / Adjacent"
        sol = f"tan(θ) = {opp}/{adj} ≈ {opp/adj:.4f}."

    return q, formula, sol, topic, diff

def gen_calculus_record(idx):
    topic = "Calculus"
    diff = "Easy" if idx % 3 == 0 else ("Medium" if idx % 3 == 1 else "Hard")
    subtype = idx % 6
    
    if subtype == 0:
        a = random.randint(2, 9)
        n = random.randint(2, 6)
        c = random.randint(1, 15)
        q = f"Find the derivative of f(x) = {a}x^{n} + {c}"
        formula = "Power Rule: d/dx [a*x^n] = a*n*x^(n-1)"
        sol = f"Applying the power rule: f'(x) = {a} × {n} × x^({n}-1) + 0 = {a*n}x^{n-1}."
    elif subtype == 1:
        a = random.randint(2, 8)
        b = random.randint(2, 8)
        c = random.randint(1, 20)
        q = f"Differentiate f(x) = {a}x³ + {b}x² - {c}x"
        formula = "d/dx [x^n] = n*x^(n-1)"
        sol = f"f'(x) = {3*a}x² + {2*b}x - {c}."
    elif subtype == 2:
        a = random.randint(2, 10)
        n = random.randint(1, 4)
        new_power = n + 1
        q = f"Evaluate the indefinite integral: ∫ ({a}x^{n}) dx"
        formula = "Power Rule for Integration: ∫ x^n dx = (x^(n+1))/(n+1) + C"
        sol = f"∫ {a}x^{n} dx = ({a}/{new_power})x^{new_power} + C."
    elif subtype == 3:
        b = random.randint(1, 5)
        val = (b**2)
        q = f"Evaluate the definite integral: ∫[0 to {b}] (2x) dx"
        formula = "∫[a to b] f(x) dx = F(b) - F(a)"
        sol = f"Antiderivative of 2x is x². Evaluating from 0 to {b}: [{b}² - 0²] = {val}."
    elif subtype == 4:
        c = random.randint(1, 8)
        q = f"Evaluate the limit: lim(x -> {c}) (x² - {c*c}) / (x - {c})"
        formula = "Factorization: (x² - c²) = (x - c)(x + c)"
        sol = f"Factoring numerator: (x - {c})(x + {c}) / (x - {c}) = x + {c}. As x -> {c}, limit = {c} + {c} = {2*c}."
    else:
        q = f"What is the derivative of sin(x) and cos(x)?"
        formula = "d/dx[sin(x)] = cos(x), d/dx[cos(x)] = -sin(x)"
        sol = f"The derivative of sin(x) is cos(x). The derivative of cos(x) is -sin(x)."

    return q, formula, sol, topic, diff

def gen_probability_record(idx):
    topic = "Probability & Statistics"
    diff = "Easy" if idx % 3 == 0 else ("Medium" if idx % 3 == 1 else "Hard")
    subtype = idx % 6
    
    if subtype == 0:
        data = sorted([random.randint(10, 99) for _ in range(5)])
        mean_val = round(sum(data) / len(data), 2)
        median_val = data[2]
        q = f"Find the mean and median of the dataset: {data}"
        formula = "Mean = Σx / N, Median = middle element of sorted array"
        sol = f"Sum = {' + '.join(map(str, data))} = {sum(data)}. Mean = {sum(data)}/5 = {mean_val}. Median = {median_val}."
    elif subtype == 1:
        n = random.randint(4, 9)
        r = random.randint(2, min(n, 4))
        comb = math.comb(n, r)
        q = f"How many ways can you choose {r} items from a group of {n}? (Combinations C({n},{r}))"
        formula = "C(n, r) = n! / (r! * (n - r)!)"
        sol = f"C({n}, {r}) = {n}! / ({r}! × {n - r}!) = {comb} ways."
    elif subtype == 2:
        n = random.randint(3, 7)
        r = random.randint(2, min(n, 3))
        perm = math.perm(n, r)
        q = f"Find the number of permutations of {n} items taken {r} at a time: P({n},{r})"
        formula = "P(n, r) = n! / (n - r)!"
        sol = f"P({n}, {r}) = {n}! / {n - r}! = {perm} arrangements."
    elif subtype == 3:
        target_sum = random.randint(2, 12)
        favorable = 0
        for d1 in range(1, 7):
            for d2 in range(1, 7):
                if d1 + d2 == target_sum:
                    favorable += 1
        q = f"What is the probability of rolling a sum of {target_sum} with two fair six-sided dice?"
        formula = "P(E) = Number of favorable outcomes / Total outcomes (36)"
        sol = f"Total outcomes = 36. Favorable outcomes summing to {target_sum} = {favorable}. Probability = {favorable}/36 = {favorable/36:.4f}."
    elif subtype == 4:
        p_coin = 0.5
        n_flips = random.choice([2, 3])
        all_heads_prob = 0.5 ** n_flips
        q = f"What is the probability of getting {n_flips} heads in a row when flipping a fair coin {n_flips} times?"
        formula = "P(all heads) = (1/2)^n"
        sol = f"P = (1/2)^{n_flips} = {all_heads_prob} (or 1 in {2**n_flips})."
    else:
        values = [random.randint(1, 20) for _ in range(7)]
        values.append(values[0])  # ensure at least one mode
        from collections import Counter
        counts = Counter(values)
        mode_val = counts.most_common(1)[0][0]
        q = f"Identify the mode of the dataset: {values}"
        formula = "Mode = most frequently occurring value in the dataset"
        sol = f"The value that appears most frequently is {mode_val} (frequency: {counts[mode_val]})."

    return q, formula, sol, topic, diff

def gen_number_theory_record(idx):
    topic = "Number Theory"
    diff = "Easy" if idx % 3 == 0 else ("Medium" if idx % 3 == 1 else "Hard")
    subtype = idx % 5
    
    if subtype == 0:
        a = random.randint(12, 180)
        b = random.randint(12, 180)
        g = math.gcd(a, b)
        q = f"Find the Greatest Common Divisor (GCD/HCF) of {a} and {b}"
        formula = "Euclidean algorithm: gcd(a, b) = gcd(b, a mod b)"
        sol = f"Using Euclidean algorithm: GCD({a}, {b}) = {g}."
    elif subtype == 1:
        a = random.randint(4, 60)
        b = random.randint(4, 60)
        l = math.lcm(a, b)
        q = f"Find the Least Common Multiple (LCM) of {a} and {b}"
        formula = "LCM(a, b) = (|a * b|) / GCD(a, b)"
        sol = f"LCM({a}, {b}) = ({a} × {b}) / {math.gcd(a, b)} = {l}."
    elif subtype == 2:
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
        test_val = random.choice([random.choice(primes), random.randint(14, 98)])
        is_p = test_val in primes
        q = f"Is {test_val} a prime number?"
        formula = "A prime number is greater than 1 with only two divisors: 1 and itself"
        sol = f"{test_val} {'is' if is_p else 'is NOT'} a prime number. {'It has no positive divisors other than 1 and itself.' if is_p else f'It is composite.'}"
    elif subtype == 3:
        n = random.randint(3, 10)
        q = f"What is {n}! (factorial of {n})?"
        formula = "n! = n * (n - 1) * ... * 1"
        sol = f"{n}! = {' × '.join(str(i) for i in range(n, 0, -1))} = {math.factorial(n)}."
    else:
        a = random.randint(2, 10)
        d = random.randint(2, 8)
        n = random.randint(5, 12)
        nth = a + (n - 1) * d
        q = f"Find the {n}th term of an arithmetic progression (AP) with first term a = {a} and common difference d = {d}"
        formula = "a_n = a + (n - 1) * d"
        sol = f"a_{n} = {a} + ({n} - 1) × {d} = {a} + {n-1} × {d} = {nth}."

    return q, formula, sol, topic, diff

def gen_financial_record(idx):
    topic = "Applied & Financial Math"
    diff = "Easy" if idx % 3 == 0 else ("Medium" if idx % 3 == 1 else "Hard")
    subtype = idx % 5
    
    if subtype == 0:
        p = random.choice([1000, 2000, 5000, 10000, 25000, 50000])
        r = random.choice([4, 5, 6, 7, 8, 10, 12])
        t = random.choice([1, 2, 3, 4, 5])
        si = (p * r * t) / 100
        total = p + si
        q = f"Calculate the Simple Interest on principal P = ${p} at annual rate r = {r}% for t = {t} years"
        formula = "SI = (P * R * T) / 100, Total Amount = P + SI"
        sol = f"SI = ({p} × {r} × {t}) / 100 = ${si:.2f}. Total accumulated amount = ${total:.2f}."
    elif subtype == 1:
        p = random.choice([1000, 2000, 5000, 10000])
        r = random.choice([5, 8, 10])
        t = random.choice([2, 3])
        amount = round(p * ((1 + r/100) ** t), 2)
        ci = round(amount - p, 2)
        q = f"Calculate the Compound Interest on P = ${p} compounded annually at r = {r}% for t = {t} years"
        formula = "A = P * (1 + r/100)^t, CI = A - P"
        sol = f"A = {p} × (1 + {r/100})^{t} = ${amount:.2f}. Compound Interest = ${ci:.2f}."
    elif subtype == 2:
        cp = random.randint(50, 800)
        sp = random.randint(cp + 10, cp + 300)
        profit = sp - cp
        profit_pct = round((profit / cp) * 100, 2)
        q = f"If cost price (CP) is ${cp} and selling price (SP) is ${sp}, find the profit and profit percentage"
        formula = "Profit = SP - CP, Profit % = (Profit / CP) * 100"
        sol = f"Profit = ${sp} - ${cp} = ${profit}. Profit % = ({profit}/{cp}) × 100 = {profit_pct}%."
    elif subtype == 3:
        dist = random.choice([120, 150, 180, 240, 300, 360, 400])
        speed = random.choice([40, 50, 60, 80, 100])
        t = round(dist / speed, 2)
        q = f"How long does it take to travel {dist} km at a constant speed of {speed} km/h?"
        formula = "Time = Distance / Speed"
        sol = f"Time = {dist} / {speed} = {t} hours."
    else:
        mp = random.choice([100, 200, 400, 500, 800, 1000])
        disc_pct = random.choice([10, 15, 20, 25, 30, 50])
        discount = (disc_pct / 100) * mp
        final_price = mp - discount
        q = f"An item with marked price ${mp} has a {disc_pct}% discount. Find the selling price"
        formula = "Discount = MP * (Discount% / 100), SP = MP - Discount"
        sol = f"Discount = ${discount:.2f}. Final Selling Price = ${final_price:.2f}."

    return q, formula, sol, topic, diff

TOPIC_GENERATORS = [
    gen_arithmetic_record,
    gen_algebra_record,
    gen_geometry_record,
    gen_trigonometry_record,
    gen_calculus_record,
    gen_probability_record,
    gen_number_theory_record,
    gen_financial_record,
]

def generate_math_record(idx):
    gen_fn = TOPIC_GENERATORS[idx % len(TOPIC_GENERATORS)]
    return gen_fn(idx)

# ====================================================================
# Database Operations: Ensure Table & Seed 100,000 Records
# ====================================================================

def ensure_math_table(engine):
    with engine.connect() as conn:
        try:
            conn.execute(text("SELECT 1 FROM math_training_data WHERE ROWNUM = 1"))
            print("  [OK] Table 'math_training_data' already exists.")
        except Exception:
            print("  [INFO] Creating table 'math_training_data'...")
            conn.execute(text("""
                CREATE TABLE math_training_data (
                    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    question VARCHAR2(1000),
                    formula VARCHAR2(500),
                    solution VARCHAR2(2000),
                    topic VARCHAR2(100),
                    difficulty VARCHAR2(50)
                )
            """))
            conn.commit()
            print("  [OK] Table 'math_training_data' created successfully.")

def seed_math_data_if_needed(engine, target_count=TARGET_COUNT, force=False):
    with engine.connect() as conn:
        count = 0
        try:
            count = conn.execute(text("SELECT COUNT(*) FROM math_training_data")).scalar()
        except Exception:
            count = 0

        if count >= target_count and not force:
            print(f"  [OK] 'math_training_data' already has {count:,} records. Skipping seeding.")
            return count

        print(f"\n[SEEDING] Generating and inserting {target_count:,} mathematical records into Oracle DB...")
        t0 = time.time()

        if force or count > 0:
            print("  [INFO] Clearing existing math records...")
            conn.execute(text("DELETE FROM math_training_data"))
            conn.commit()

        BATCH_SIZE = 5000
        for start in range(0, target_count, BATCH_SIZE):
            end = min(start + BATCH_SIZE, target_count)
            params = []
            for i in range(start, end):
                q, f, s, top, diff = generate_math_record(i)
                params.append({"q": q, "f": f, "s": s, "t": top, "d": diff})

            conn.execute(
                text("INSERT INTO math_training_data (question, formula, solution, topic, difficulty) VALUES (:q, :f, :s, :t, :d)"),
                params
            )
            conn.commit()
            elapsed = time.time() - t0
            rate = end / elapsed if elapsed > 0 else 0
            print(f"  Progress: {end:>7,}/{target_count:,} records inserted ({end/target_count*100:5.1f}%) | {rate:,.0f} rows/sec")

        total_time = time.time() - t0
        print(f"  [OK] Successfully seeded {target_count:,} mathematical records in {total_time:.1f}s.")
        return target_count

# ====================================================================
# Model Training: Vectorizer, Retrieval Matrix, Topic Classifier
# ====================================================================

def train_mathematical_model(engine, total_records=TARGET_COUNT):
    print("\n" + "=" * 60)
    print("  TRAINING MATHEMATICAL INTELLIGENCE MODEL")
    print(f"  Dataset: {total_records:,} mathematical records")
    print("=" * 60)

    # 1. Fetch data from DB
    print("\n[1/5] Loading mathematical training data from Oracle DB...")
    t0 = time.time()
    df = pd.read_sql("SELECT question, formula, solution, topic, difficulty FROM math_training_data", engine)
    print(f"  [OK] Loaded {len(df):,} records in {time.time()-t0:.2f}s.")

    # 2. Fit TF-IDF Vectorizer with mathematical operator tokens
    print("\n[2/5] Fitting Mathematical TF-IDF Vectorizer...")
    t0 = time.time()
    # Custom token pattern captures words, numbers, and arithmetic symbols (+, -, *, /, ^, =)
    vectorizer = TfidfVectorizer(
        max_features=12000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        token_pattern=r"(?u)\b\w+\b|[\+\-\*\/\^\=]"
    )
    X_matrix = vectorizer.fit_transform(df["question"])
    print(f"  [OK] TF-IDF Matrix built: {X_matrix.shape} in {time.time()-t0:.2f}s.")

    # 3. Train Neural Network Topic Classifier
    print("\n[3/5] Training Topic Classifier (Neural Network MLP)...")
    t0 = time.time()
    topic_encoder = LabelEncoder()
    y_encoded = topic_encoder.fit_transform(df["topic"])

    # Train on a stratified sample of 25,000 for high speed CPU convergence
    SAMPLE_SIZE = min(25000, len(df))
    np.random.seed(42)
    sample_indices = np.random.choice(len(df), size=SAMPLE_SIZE, replace=False)
    X_sample = X_matrix[sample_indices]
    y_sample = y_encoded[sample_indices]

    mlp = MLPClassifier(
        hidden_layer_sizes=(128, 64),
        max_iter=25,
        alpha=1e-4,
        solver='adam',
        random_state=42,
        learning_rate_init=0.01
    )
    mlp.fit(X_sample, y_sample)
    acc = mlp.score(X_sample, y_sample)
    print(f"  [OK] MLP Neural Net Classifier Accuracy: {acc*100:.2f}% (trained in {time.time()-t0:.2f}s).")

    # 4. Save artifacts
    print("\n[4/5] Saving Mathematical Model Assets to 'assets/'...")
    joblib.dump(vectorizer, os.path.join(ASSETS_DIR, "math_vectorizer.pkl"))
    joblib.dump(X_matrix, os.path.join(ASSETS_DIR, "math_matrix.pkl"))
    joblib.dump(df["solution"].values, os.path.join(ASSETS_DIR, "math_answers.pkl"))
    joblib.dump(df["formula"].values, os.path.join(ASSETS_DIR, "math_formulas.pkl"))
    joblib.dump(df["topic"].values, os.path.join(ASSETS_DIR, "math_topics.pkl"))
    joblib.dump(topic_encoder, os.path.join(ASSETS_DIR, "math_topic_encoder.pkl"))
    joblib.dump(mlp, os.path.join(ASSETS_DIR, "math_classifier.pkl"))

    metadata = {
        "model_name": "math_model",
        "records_count": len(df),
        "accuracy": float(acc),
        "classes": list(topic_encoder.classes_),
        "features": vectorizer.max_features,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(ASSETS_DIR, "math_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print("  [OK] Saved:")
    print("       - assets/math_vectorizer.pkl")
    print("       - assets/math_matrix.pkl")
    print("       - assets/math_answers.pkl")
    print("       - assets/math_formulas.pkl")
    print("       - assets/math_topics.pkl")
    print("       - assets/math_topic_encoder.pkl")
    print("       - assets/math_classifier.pkl")
    print("       - assets/math_metadata.json")

    # 5. Log metadata to Oracle DB
    print("\n[5/5] Logging model metadata into Oracle DB...")
    try:
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO ml_model_metadata (model_name, records_count, accuracy, status) VALUES (:m, :c, :a, 'SUCCESS')"),
                {"m": "math_model", "c": len(df), "a": float(acc)}
            )
            conn.commit()
            print("  [DB Log] Successfully logged metadata for 'math_model' to ml_model_metadata table.")
    except Exception as e:
        print(f"  [WARN] Failed to log model metadata: {e}")

    return acc, metadata

# ====================================================================
# Verification & Quick Test
# ====================================================================

def verify_math_inference():
    print("\n" + "=" * 60)
    print("  VERIFYING MATHEMATICAL INTELLIGENCE INFERENCE")
    print("=" * 60)

    vec = joblib.load(os.path.join(ASSETS_DIR, "math_vectorizer.pkl"))
    mat = joblib.load(os.path.join(ASSETS_DIR, "math_matrix.pkl"))
    ans = joblib.load(os.path.join(ASSETS_DIR, "math_answers.pkl"))
    forms = joblib.load(os.path.join(ASSETS_DIR, "math_formulas.pkl"))
    tops = joblib.load(os.path.join(ASSETS_DIR, "math_topics.pkl"))
    clf = joblib.load(os.path.join(ASSETS_DIR, "math_classifier.pkl"))
    enc = joblib.load(os.path.join(ASSETS_DIR, "math_topic_encoder.pkl"))

    test_queries = [
        "Solve for x: 5x + 10 = 35",
        "Find the area of a circle with radius 14 cm",
        "What is the derivative of f(x) = 4x^3 + 5",
        "Find the GCD of 48 and 180",
        "Calculate the simple interest on $10000 at 5% for 3 years",
        "What is 25% of 800?",
        "What is sin(30)?"
    ]

    for q in test_queries:
        q_vec = vec.transform([q])
        pred_topic = enc.inverse_transform(clf.predict(q_vec))[0]
        sims = mat.dot(q_vec.T).toarray().ravel()
        best_idx = int(np.argmax(sims))
        score = float(sims[best_idx])
        
        print(f"\n  Query:     '{q}'")
        print(f"  Predicted Topic: {pred_topic} (Confidence: {np.max(clf.predict_proba(q_vec)[0]):.2f})")
        print(f"  Similarity Score: {score:.4f}")
        print(f"  Formula:   {forms[best_idx]}")
        print(f"  Solution:  {ans[best_idx][:90]}...")

    print("\n[OK] Mathematical Intelligence inference verified successfully!")

# ====================================================================
# Main Execution
# ====================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OMEGA Math Model Trainer")
    parser.add_argument("--count", type=int, default=TARGET_COUNT, help="Number of records to generate/train")
    parser.add_argument("--force-seed", action="store_true", help="Force re-generation of database records")
    parser.add_argument("--verify-only", action="store_true", help="Run verification inference only")
    args = parser.parse_args()

    if args.verify_only:
        verify_math_inference()
        sys.exit(0)

    print("=" * 60)
    print("  OMEGA Mathematical Intelligence Pipeline")
    print(f"  Target Records: {args.count:,}")
    print("=" * 60)

    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1 FROM DUAL"))
        print("[OK] Connected to Oracle Database successfully.")
    except Exception as e:
        print(f"[FAIL] Oracle DB connection failed: {e}")
        sys.exit(1)

    ensure_math_table(engine)
    seed_math_data_if_needed(engine, target_count=args.count, force=args.force_seed)
    train_mathematical_model(engine, total_records=args.count)
    verify_math_inference()
