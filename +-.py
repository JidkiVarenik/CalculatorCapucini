import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def open_calculator():
    calc_window = tk.Toplevel(root)
    calc_window.title("Калькулятор")
    calc_window.geometry("300x400")

    entry = tk.Entry(calc_window, width=25, font=("Arial", 18), justify='right')
    entry.grid(row=0, column=0, columnspan=4, pady=10)

    def click(symbol):
        entry.insert(tk.END, symbol)

    def clear():
        entry.delete(0, tk.END)

    def calculate():
        try:
            expr = entry.get().replace("^", "**")
            names = {
                "sin": np.sin,
                "cos": np.cos,
                "log": np.log,
                "sqrt": np.sqrt,
                "exp": np.exp,
                "x": None
            }
            result = eval(expr, names)
            entry.delete(0, tk.END)
            entry.insert(tk.END, str(result))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Некорректный ввод: {e}")

    buttons = [
        "7", "8", "9", "+",
        "4", "5", "6", "-",
        "1", "2", "3", "*",
        "0", ".", "/", "="
    ]

    for idx, symbol in enumerate(buttons):
        def make_lambda(s=symbol):
            return lambda: calculate() if s == "=" else click(s)
        btn = tk.Button(calc_window, text=symbol, width=5, height=2, font=("Arial", 14), command=make_lambda())
        btn.grid(row=1 + idx // 4, column=idx % 4)

    tk.Button(calc_window, text="C", width=5, height=2, font=("Arial", 14), command=clear).grid(row=5, column=0)


def open_equation_solver():
    solver_window = tk.Toplevel(root)
    solver_window.title("Решение уравнений")
    solver_window.geometry("300x300")

    tk.Label(solver_window, text="Выберите тип уравнения:").pack(pady=10)

    def solve_linear():
        a = simple_input("Введите коэффициент a:")
        b = simple_input("Введите коэффициент b:")
        if a is not None and b is not None:
            result = "Уравнение имеет беск. множество решений" if a == 0 and b == 0 else \
                     "Уравнение не имеет решений" if a == 0 else \
                     f"Решение линейного уравнения: x = {-b / a}"
            messagebox.showinfo("Результат", result)

    def solve_quadratic():
        a = simple_input("Введите коэффициент a:")
        b = simple_input("Введите коэффициент b:")
        c = simple_input("Введите коэффициент c:")
        if None not in (a, b, c):
            D = b**2 - 4*a*c
            if a == 0:
                solve_linear()
            elif D > 0:
                x1 = (-b + D**0.5) / (2*a)
                x2 = (-b - D**0.5) / (2*a)
                messagebox.showinfo("Результат", f"Два решения: x1 = {x1}, x2 = {x2}")
            elif D == 0:
                x = -b / (2*a)
                messagebox.showinfo("Результат", f"Одно решение: x = {x}")
            else:
                messagebox.showinfo("Результат", "Нет действительных решений")

    tk.Button(solver_window, text="Линейное уравнение", font=("Arial", 12), command=solve_linear).pack(pady=5)
    tk.Button(solver_window, text="Квадратное уравнение", font=("Arial", 12), command=solve_quadratic).pack(pady=5)

def simple_input(prompt):
    input_window = tk.Toplevel(root)
    input_window.title("Ввод числа")
    input_window.geometry("250x100")
    tk.Label(input_window, text=prompt).pack(pady=5)
    entry = tk.Entry(input_window)
    entry.pack(pady=5)

    result = tk.DoubleVar()

    def submit():
        try:
            result.set(float(entry.get()))
            input_window.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число!")

    tk.Button(input_window, text="OK", command=submit).pack()
    input_window.wait_window()
    return result.get() if result.get() != 0.0 or entry.get() == "0" else None


def open_graph_plotter():
    plot_window = tk.Toplevel(root)
    plot_window.title("Построение графика")
    plot_window.geometry("400x400")

    func_entry = tk.Entry(plot_window, font=("Arial", 12))
    func_entry.pack(pady=10)
    func_entry.insert(0, "x^2 + sin(x)")

    fig, ax = plt.subplots(figsize=(4, 3))
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.get_tk_widget().pack()

    def plot_function():
        arg = func_entry.get().replace("^", "**")
        names = {
            "x": None,
            "sin": np.sin,
            "cos": np.cos,
            "log": np.log,
            "sqrt": np.sqrt,
            "exp": np.exp
        }
        try:
            def f1(x):
                names["x"] = x
                return eval(arg, names)

            x = np.linspace(-10, 10, 400)
            y = f1(x)

            ax.clear()
            ax.plot(x, y)
            ax.set_xlabel("x")
            ax.set_ylabel("f(x)")
            ax.grid(True)
            ax.set_title("График функции")
            canvas.draw()
        except Exception as e:
            ax.clear()
            ax.text(0.5, 0.5, f"Ошибка: {e}", ha='center', va='center', fontsize=10)
            canvas.draw()

    tk.Button(plot_window, text="Построить график", font=("Arial", 12), command=plot_function).pack(pady=5)


root = tk.Tk()
root.title("Многофункциональный калькулятор")
root.geometry("300x250")

tk.Label(root, text="Выберите действие:", font=("Arial", 14)).pack(pady=15)

tk.Button(root, text="Калькулятор", width=20, font=("Arial", 12), command=open_calculator).pack(pady=5)
tk.Button(root, text="Решение уравнений", width=20, font=("Arial", 12), command=open_equation_solver).pack(pady=5)
tk.Button(root, text="Построение графиков", width=20, font=("Arial", 12), command=open_graph_plotter).pack(pady=5)
tk.Button(root, text="Выход", width=20, font=("Arial", 12), command=root.destroy).pack(pady=20)

root.mainloop()
