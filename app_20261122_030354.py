import tkinter as tk
from tkinter import messagebox
import random
import math
import time
import datetime
import json
import collections
import itertools
import functools
import string
import re
import statistics
import calendar
import enum
import dataclasses
from typing import List, Dict, Optional
import colorsys


class Operation(enum.Enum):
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"


@dataclasses.dataclass
class MathProblem:
    a: float
    b: float
    op: Operation
    correct: float = dataclasses.field(init=False)

    def __post_init__(self):
        if self.op == Operation.ADD:
            self.correct = round(self.a + self.b, 2)
        elif self.op == Operation.SUB:
            self.correct = round(self.a - self.b, 2)
        elif self.op == Operation.MUL:
            self.correct = round(self.a * self.b, 2)
        elif self.op == Operation.DIV:
            divisor = max(1, int(self.b))
            self.correct = round(self.a / divisor, 2)


class MathQuizApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.score: int = 0
        self.total: int = 0
        self.problems_counter: collections.Counter = collections.Counter()
        self.current: Optional[MathProblem] = None
        self.bg_hex: str = "#f0f0f0"

        self.root.title("Deva's Math Quiz")
        self.root.geometry("420x360")
        self.root.configure(bg=self.bg_hex)

        # Time/Date display
        self.time_label = tk.Label(
            root, font=("Consolas", 11), bg=self.bg_hex, fg="#333"
        )
        self.time_label.pack(pady=6)

        # Problem display
        self.problem_label = tk.Label(
            root, font=("Consolas", 18, "bold"), bg=self.bg_hex, fg="#0066cc"
        )
        self.problem_label.pack(pady=15)

        # Answer entry
        self.answer_var = tk.StringVar()
        self.answer_entry = tk.Entry(
            root, textvariable=self.answer_var, font=("Consolas", 16), justify="center", width=10
        )
        self.answer_entry.pack(pady=5)
        self.answer_entry.bind("<Return>", lambda e: self.check_answer())
        self.answer_entry.focus_set()

        # Feedback
        self.feedback_label = tk.Label(root, font=("Consolas", 13), bg=self.bg_hex)
        self.feedback_label.pack(pady=4)

        # Stats display
        self.stats_label = tk.Label(
            root, font=("Consolas", 10), bg=self.bg_hex, fg="#555"
        )
        self.stats_label.pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(root, bg=self.bg_hex)
        btn_frame.pack(pady=8)
        self.btn_check = tk.Button(
            btn_frame, text="Check", command=self.check_answer,
            bg="#4CAF50", fg="white", font=("Consolas", 10), width=10
        )
        self.btn_check.pack(side=tk.LEFT, padx=4)
        self.btn_new = tk.Button(
            btn_frame, text="New Problem", command=self.generate_problem,
            bg="#2196F3", fg="white", font=("Consolas", 10), width=10
        )
        self.btn_new.pack(side=tk.LEFT, padx=4)

        # Initialize first problem and timer
        self.generate_problem()
        self.update_clock()

    # ── Logic ──────────────────────────────────────────────────────────
    @functools.lru_cache(maxsize=32)
    def _cached_problem_key(self, a: float, b: float, op_idx: int) -> str:
        return f"{a}_{b}_{op_idx}"

    def generate_problem(self) -> None:
        a = round(random.uniform(0.5, 15.5), 2)
        b = round(random.uniform(0.5, 15.5), 2)
        op = random.choice(list(Operation))
        self.current = MathProblem(a, b, op)

        expr = f"{a:.2f} {self.current.op.value} {b:.2f}"
        self.problem_label.config(text=f"Solve: {expr}")
        self.answer_var.set("")
        self.feedback_label.config(text="")
        self.total += 1
        self.problems_counter[self.current.op] += 1
        self.update_stats_ui()
        # Auto-move after 2s if not answered
        self.root.after(2000, self.force_next)

    def force_next(self) -> None:
        if self.answer_entry.get().strip() == "":
            self.generate_problem()

    def check_answer(self) -> None:
        user_text = self.answer_entry.get().strip()
        # Validate with regex from 'string' + re
        if not re.fullmatch(r"-?\d*\.?\d+", user_text):
            self.feedback_label.config(text="Enter a valid number.", fg="red")
            return
        user_val = float(user_text)
        if self.current is None:
            return
        diff = abs(user_val - self.current.correct)
        if diff < 0.01:
            self.score += 1
            self.feedback_label.config(text="Correct!", fg="green")
        else:
            self.feedback_label.config(
                text=f"Wrong! Correct: {self.current.correct}", fg="red"
            )
        self.update_stats_ui()
        # Dynamic background via colorsys
        acc = (self.score / self.total * 100) if self.total > 0 else 0
        hue = (1 - acc / 100) * 0.6
        r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 1.0)
        self.bg_hex = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        self.root.configure(bg=self.bg_hex)
        self.time_label.configure(bg=self.bg_hex)
        self.problem_label.configure(bg=self.bg_hex)
        self.feedback_label.configure(bg=self.bg_hex)
        self.stats_label.configure(bg=self.bg_hex)
        self.root.after(1200, self.generate_problem)

    def update_stats_ui(self) -> None:
        acc = (self.score / self.total * 100) if self.total > 0 else 0
        # Use statistics.mean on a running list if desired, here simple calc
        top_ops = self.problems_counter.most_common(3)
        ops_str = ", ".join(f"{op.name}({cnt})" for op, cnt in top_ops)
        self.stats_label.config(
            text=f"Score: {self.score}/{self.total} | Acc: {acc:.1f}% | Top ops: {ops_str}"
        )

    def update_clock(self) -> None:
        now = datetime.datetime.now()
        self.time_label.config(text=now.strftime("%Y-%m-%d %H:%M:%S"))
        # Use calendar month name demo
        month_name = calendar.month_name[now.month]
        # Unused but shows import usage; we just display time
        self.root.after(1000, self.update_clock)

    # ── Entry point ────────────────────────────────────────────────────
    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = MathQuizApp(root)
    app.run()