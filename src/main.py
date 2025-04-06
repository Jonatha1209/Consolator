
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from decimal import Decimal, getcontext
from sympy import *
import types
import math
import os
import sympy

getcontext().prec = 30

def wrap_math_func(f):
    def inner(x):
        if isinstance(x, Decimal):
            x = int(x) if x == int(x) else float(x)
        return f(x)
    return inner

vars_ = {}
svars = {}
hist = []

mfuncs = {
    name: wrap_math_func(getattr(math, name))
    for name in dir(math)
    if isinstance(getattr(math, name), types.BuiltinFunctionType)
}

sfuncs = {
    name: wrap_math_func(getattr(sympy, name))
    for name in dir(sympy)
    if isinstance(getattr(sympy, name), types.BuiltinFunctionType)
}

style = Style.from_dict({
    "prompt": "ansicyan bold",
})

def eval_expr(exp: str):
    try:
        if "=" in exp and not exp.strip().startswith(":"):
            name, val = map(str.strip, exp.split("=", 1))
            val_eval = eval(val, {**mfuncs, **sfuncs, **svars})
            dec_val = Decimal(str(val_eval))
            vars_[name] = dec_val
            svars[name] = dec_val
            return dec_val

        if exp.startswith(":sympy "):
            sexp = exp.replace(":sympy ", "")
            return eval(sexp, {**globals(), **svars})

        val = eval(exp, {**mfuncs, **sfuncs, **svars})
        if isinstance(val, (int, float)):
            return Decimal(str(val))
        elif isinstance(val, (Float, Integer)):
            return Decimal(str(val.evalf()))
        else:
            return val

    except Exception as e:
        return f"Error: {e}"

def make_completer():
    words = list(mfuncs.keys()) + list(sfuncs.keys()) + list(vars_.keys()) + [":sympy"]
    return WordCompleter(words, ignore_case=True)

def main():
    hist_file = os.path.expanduser("~/.calc_history.txt")
    sess = PromptSession(history=FileHistory(hist_file), completer=make_completer())
    print("Knens calculator based on sympy, math \n Exit command is exit or quit.")

    while True:
        try:
            sess.completer = make_completer()
            exp = sess.prompt([('class:prompt', '수식 > ')], style=style)

            if exp.strip().lower() in ["exit", "quit"]:
                print("👋 Bye Bye")
                break

            res = eval_expr(exp)
            print("Result :", res)

            if not str(res).startswith("⚠️"):
                hist.append({"exp": exp, "res": res})

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()
