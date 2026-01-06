import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from projections import Projections
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class FinancialApp:
    def __init__(self, master):
        self.master = master
        master.title("Financial Projections")

        frame = ttk.Frame(master, padding=10)
        frame.grid(row=0, column=0, sticky="W")

        self.starting_users_var = tk.StringVar(value="0")
        self.growth_rate_var = tk.StringVar(value="0.4")
        self.churn_rate_var = tk.StringVar(value="5")
        self.arpu_var = tk.StringVar(value="50")
        self.months_var = tk.StringVar(value="12")

        labels = ["Starting Users", "Monthly Growth %", "Monthly Churn %", "ARPU ($)", "Months"]
        variables = [self.starting_users_var, self.growth_rate_var, self.churn_rate_var, self.arpu_var, self.months_var]

        for i, (label, var) in enumerate(zip(labels, variables)):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky="W", pady=2)
            ttk.Entry(frame, textvariable=var, width=10).grid(row=i, column=1, pady=2)

        ttk.Button(frame, text="Run Projection", command=self.run_projection).grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Export to Excel", command=self.export_excel).grid(row=7, column=0, columnspan=2, pady=5)
        ttk.Button(frame, text="Exit", command=master.quit).grid(row=8, column=0, columnspan=2, pady=5)

        self.chart_frame = ttk.Frame(master)
        self.chart_frame.grid(row=0, column=1, padx=20)

        self.current_proj = None

    def run_projection(self):
        try:
            starting_users = int(self.starting_users_var.get())
            growth_rate = float(self.growth_rate_var.get())
            churn_rate = float(self.churn_rate_var.get())
            arpu = float(self.arpu_var.get())
            months = int(self.months_var.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers.")
            return

        proj = Projections(starting_users, growth_rate, churn_rate, arpu)
        self.current_proj = proj.project_months(months)

        self.plot_results(self.current_proj)

    def plot_results(self, df):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig, ax1 = plt.subplots(figsize=(6, 4))
        months = df["Month"]
        ax1.plot(months, df["Users"], "b-o", label="Users")
        ax1.set_xlabel("Month")
        ax1.set_ylabel("Users", color="b")
        ax1.tick_params(axis="y", labelcolor="b")

        ax2 = ax1.twinx()
        ax2.plot(months, df["Revenue"], "r-s", label="Revenue")
        ax2.set_ylabel("Revenue ($)", color="r")
        ax2.tick_params(axis="y", labelcolor="r")

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def export_excel(self):
        if self.current_proj is None:
            messagebox.showerror("No Data", "Run a projection first.")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                filetypes=[("Excel files", "*.xlsx")])
        if filepath:
            self.current_proj.to_excel(filepath, index=False)
            messagebox.showinfo("Export Complete", f"Projections saved to {filepath}")
