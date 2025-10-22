#!/usr/bin/env python3
"""
PlateParity — solver for the license-plate equality game.

Rules (configurable below):
- Input: 4 digits D1 D2 D3 D4 (order fixed; NO concatenation).
- Place exactly ONE "=" somewhere between digits => splits into LHS and RHS.
- Insert binary operators between remaining digits from the set you allow.
- You may use parentheses freely.
- Unary operators allowed (configurable): factorial (!) and absolute value |x|.
- Allowed operators: +, -, *, %, ^ (exponent), ! (factorial), |x| (absolute value).
- No division (by design). Modulo by zero is forbidden. Exponent bounds configurable.
- Factorial only on nonnegative integers <= MAX_FACTORIAL_ARG.
"""

from __future__ import annotations
from dataclasses import dataclass
from math import factorial as math_factorial, isclose
from typing import List, Tuple, Iterable, Dict, Set

# ==========================
# RULES — tweak as you like
# ==========================
RULES: Dict = {
    "allow_plus": True,
    "allow_minus": True,
    "allow_times": True,
    "allow_mod": False,      # % remainder
    "allow_pow": True,      # ^ as exponent
    "allow_abs": True,      # |x|
    "allow_fact": True,     # !
    # Exponent constraints to avoid huge blow-ups
    "pow_require_int_exp": True,  # exponent must be integer
    "pow_min_exp": 0,             # disallow negative exponents by default
    "pow_max_exp": 6,             # cap exponent to keep search sane
    # Factorial constraints
    "max_factorial_arg": 8,       # cap n! (8! = 40320) — easy to change
    # Apply unary ops (abs, fact) at any node? (kept true; space still tiny for 4 digits)
    "enable_unary_wrapping": True,
    # Numeric comparison tolerance for floats (we try to keep ints when possible)
    "eq_tol": 1e-9,
}

# Pretty symbols for output
SYM_PLUS = "+"
SYM_MINUS = "-"
SYM_TIMES = "×"
SYM_MOD = "%"
SYM_POW = "^"
SYM_EQ = "="

# ==========================
# Core types
# ==========================
@dataclass(frozen=True)
class Expr:
    val: float | int
    text: str
    is_int: bool

    def maybe_abs(self) -> Iterable["Expr"]:
        if not RULES["allow_abs"]:
            return []
        v = abs(self.val)
        txt = f"|{self.text}|"
        return [Expr(as_int_if_possible(v), txt, is_integer(v))]

    def maybe_fact(self) -> Iterable["Expr"]:
        if not RULES["allow_fact"]:
            return []
        # only defined for nonnegative integers within bound
        if not self.is_int:
            return []
        n = int(self.val)
        if n < 0 or n > RULES["max_factorial_arg"]:
            return []
        v = math_factorial(n)
        txt = f"({self.text})!"
        return [Expr(as_int_if_possible(v), txt, True)]  # factorial result is int

# ==========================
# Utilities
# ==========================
def is_integer(x: float | int) -> bool:
    return isinstance(x, int) or (isinstance(x, float) and x.is_integer())

def as_int_if_possible(x: float | int) -> float | int:
    if is_integer(x):
        return int(x)
    return x

def safe_pow(a: float | int, b: float | int) -> Tuple[bool, float | int]:
    # power constraints
    if RULES["pow_require_int_exp"] and not is_integer(b):
        return False, 0
    b_int = int(b) if is_integer(b) else b
    if isinstance(b_int, int):
        if b_int < RULES["pow_min_exp"] or b_int > RULES["pow_max_exp"]:
            return False, 0
    try:
        v = a ** b_int
    except Exception:
        return False, 0
    return True, v

def combine_binary(L: Expr, R: Expr) -> Iterable[Expr]:
    """Generate binary combinations (L op R) following rules."""
    out: List[Expr] = []
    # +
    if RULES["allow_plus"]:
        v = L.val + R.val
        out.append(Expr(as_int_if_possible(v), f"({L.text} {SYM_PLUS} {R.text})", is_integer(v)))
    # -
    if RULES["allow_minus"]:
        v = L.val - R.val
        out.append(Expr(as_int_if_possible(v), f"({L.text} {SYM_MINUS} {R.text})", is_integer(v)))
    # *
    if RULES["allow_times"]:
        v = L.val * R.val
        out.append(Expr(as_int_if_possible(v), f"({L.text} {SYM_TIMES} {R.text})", is_integer(v)))
    # %
    if RULES["allow_mod"]:
        if L.is_int and R.is_int:
            r = int(R.val)
            if r != 0:
                v = int(L.val) % r
                out.append(Expr(int(v), f"({L.text} {SYM_MOD} {R.text})", True))
    # ^
    if RULES["allow_pow"]:
        ok, v = safe_pow(L.val, R.val)
        if ok:
            out.append(Expr(as_int_if_possible(v), f"({L.text} {SYM_POW} {R.text})", is_integer(v)))
    return out

def wrap_unaries(e: Expr) -> List[Expr]:
    """Optionally wrap with abs / factorial; include combos lightly to avoid blow-up."""
    variants = [e]
    if not RULES["enable_unary_wrapping"]:
        return variants
    # Apply abs
    for base in list(variants):
        variants += list(base.maybe_abs())
    # Apply factorial to both the base and abs-variant (if any)
    # (abs then fact is common; fact then abs is redundant because fact ≥ 0)
    more: List[Expr] = []
    for v in variants:
        more += list(v.maybe_fact())
    variants += more
    # Deduplicate by (val, text)
    uniq: Dict[Tuple[str, str], Expr] = {}
    for v in variants:
        key = (str(v.val), v.text)
        uniq[key] = v
    return list(uniq.values())

# ==========================
# Expression generator
# ==========================
def build_exprs(nums: List[int]) -> List[Expr]:
    """All expressions from an ordered list of digits using allowed binary ops and parentheses."""
    if len(nums) == 1:
        base = Expr(nums[0], str(nums[0]), True)
        return wrap_unaries(base)

    results: Dict[Tuple[str, str], Expr] = {}
    N = len(nums)
    for split in range(1, N):
        left_nums = nums[:split]
        right_nums = nums[split:]
        left_exprs = build_exprs(left_nums)
        right_exprs = build_exprs(right_nums)
        for L in left_exprs:
            for R in right_exprs:
                for comb in combine_binary(L, R):
                    for w in wrap_unaries(comb):
                        # key by value and text to prune duplicates
                        key = (str(w.val), w.text)
                        results[key] = w
    return list(results.values())

def values_equal(a: float | int, b: float | int) -> bool:
    if is_integer(a) and is_integer(b):
        return int(a) == int(b)
    return isclose(float(a), float(b), rel_tol=0, abs_tol=RULES["eq_tol"])

# ==========================
# Solver
# ==========================
def solve_plate(d1: int, d2: int, d3: int, d4: int) -> List[str]:
    """
    Try all "=" positions and report equations LHS = RHS that evaluate true.
    No digit concatenation; order fixed.
    """
    digits = [int(d1), int(d2), int(d3), int(d4)]
    solutions: Set[str] = set()

    # "=" can go after 1st, 2nd, or 3rd digit
    for eq_pos in (1, 2, 3):
        L_nums = digits[:eq_pos]
        R_nums = digits[eq_pos:]
        L_exprs = build_exprs(L_nums)
        R_exprs = build_exprs(R_nums)

        for L in L_exprs:
            for R in R_exprs:
                if values_equal(L.val, R.val):
                    eq = f"{L.text} {SYM_EQ} {R.text}"
                    # Normalize outer parentheses for prettiness
                    eq = prettify(eq)
                    solutions.add(eq)

    return sorted(solutions, key=len)  # short/cute first

def prettify(s: str) -> str:
    # Remove superfluous outer parentheses around single numbers like "(3)" → "3"
    # Gentle cleanup to keep output readable.
    changed = True
    while changed:
        changed = False
        if s.startswith("(") and s.endswith(")"):
            # Count paren balance to see if outermost pair encloses all
            bal = 0
            ok = True
            for i, ch in enumerate(s):
                if ch == "(":
                    bal += 1
                elif ch == ")":
                    bal -= 1
                if bal == 0 and i != len(s) - 1:
                    ok = False
                    break
            if ok:
                s = s[1:-1]
                changed = True
    # Replace "×" with * in code-like contexts? We keep the pretty symbol.
    return s

# ==========================
# CLI
# ==========================
def main():
    import argparse
    ap = argparse.ArgumentParser(description="Solve PlateEquals for 4 digits (order fixed).")
    ap.add_argument("digits", nargs=1, help="Four-digit sequence, e.g., 4312 (no spaces)")
    ap.add_argument("--limit", type=int, default=10, help="Max lines to print")
    args = ap.parse_args()

    dstr = args.digits[0].strip()
    if not (len(dstr) == 4 and dstr.isdigit()):
        raise SystemExit("Provide exactly four digits, e.g., 4312")

    d1, d2, d3, d4 = map(int, list(dstr))
    sols = solve_plate(d1, d2, d3, d4)
    if not sols:
        print("No solutions under current RULES.")
        return
    print(f"Found {len(sols)} solution(s):")
    for i, eq in enumerate(sols[:args.limit], 1):
        print(f"{i:3d}. {eq}")

if __name__ == "__main__":
    main()
