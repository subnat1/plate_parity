# 🧮 PlateParity  

> *A roadside math puzzle that accidentally became open source.*

---

## 🚗 What is it?

You’re driving. You see a number plate — say `4312`.  
Your brain, instead of doing something useful, decides it wants balance.  

So you add one `=` somewhere and try to make the digits **mathematically equal** using  
`+, -, *, ^, !, |x|`, and parentheses.

Example:
4 - 3 + 1 = 2

✅ Order stays the same.  
🚫 You **cannot** glue digits together (1 and 2 ≠ 12).  
🧠 You **may** use brackets.  
💀 You **must** use exactly one “=”.

That’s **PlateParity** — equal parts logic, math, and traffic boredom.

---

## 🧩 The Rules

| # | Rule | Notes |
|---|------|-------|
| 1 | **Order matters** | No rearranging digits |
| 2 | **No concatenation** | 1 and 2 ≠ 12 |
| 3 | **Exactly one "="** | Splits LHS and RHS |
| 4 | **Operators** | `+ - * ^ ! | |` |
| 5 | **Factorial limit** | Up to 8! |
| 6 | **Absolute value `|x|`** | Optional, but powerful |
| 7 | **Brackets** | Unlimited parentheses |
| 8 | **Division** | Banned (too easy to zero out) |
<!-- | 6 | **Modulo `%`** | Python remainder (so negative mod is allowed) | -->

---

## 🧠 Example Plates

| Plate | Equation | Works Because |
|:------|:----------|:---------------|
| `4312` | `4 - 3 + 1 = 2` | Straight arithmetic |
| `5226` | `(5 - 2)! = 2 + 6` | `(3)! = 6 + 2 → 6 = 8` (false, so not valid) |
| `5234` | `(5 - 2)! = (3 + 4)` | `3! = 7 → 6 = 7` (false, but close) |

Try your own — you’ll quickly realize some plates are unsolvable, which makes it oddly addictive.

---

