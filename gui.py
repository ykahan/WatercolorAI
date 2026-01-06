import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors

from projections import Projections


class FinancialApp:
    def __init__(self, master):
        self.master = master
        master.title("Financial Projections")

        # ===================== INPUT FRAME =====================
        frame = ttk.Frame(master, padding=10)
        frame.grid(row=0, column=0, sticky="W")

        self.starting_users_var = tk.StringVar(value="50")
        self.growth_rate_var = tk.StringVar(value="8")
        self.churn_rate_var = tk.StringVar(value="2")
        self.arpu_var = tk.StringVar(value="50")
        self.months_var = tk.StringVar(value="60")

        labels = [
            "Starting Users",
            "Monthly Growth %",
            "Monthly Churn %",
            "ARPU ($)",
            "Months"
        ]

        variables = [
            self.starting_users_var,
            self.growth_rate_var,
            self.churn_rate_var,
            self.arpu_var,
            self.months_var
        ]

        for i, (label, var) in enumerate(zip(labels, variables)):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky="W", pady=2)
            ttk.Entry(frame, textvariable=var, width=12).grid(row=i, column=1, pady=2)

        ttk.Button(frame, text="Run Projection", command=self.run_projection).grid(
            row=6, column=0, columnspan=2, pady=10
        )

        ttk.Button(frame, text="Export to Excel", command=self.export_excel).grid(
            row=7, column=0, columnspan=2, pady=5
        )

        ttk.Button(frame, text="Exit", command=master.quit).grid(
            row=8, column=0, columnspan=2, pady=5
        )

        # ===================== CHART FRAME =====================
        self.chart_frame = ttk.Frame(master)
        self.chart_frame.grid(row=0, column=1, padx=20, sticky="N")

        self.current_proj = None

    # ==========================================================
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

        proj = Projections(
            starting_users=starting_users,
            growth_rate=growth_rate,
            churn_rate=churn_rate,
            arpu=arpu
        )

        self.current_proj = proj.project_months(months)
        self.plot_results(self.current_proj)

    # ==========================================================
    def plot_results(self, df):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig, ax_users = plt.subplots(figsize=(7, 4))

        months = df["Month"].values
        users = df["Users"].values
        revenue = df["Revenue"].values

        # Users axis
        users_line, = ax_users.plot(
            months, users, "b-o", label="Users"
        )
        ax_users.set_xlabel("Month")
        ax_users.set_ylabel("Users", color="b")
        ax_users.tick_params(axis="y", labelcolor="b")

        # Revenue axis
        ax_revenue = ax_users.twinx()
        revenue_line, = ax_revenue.plot(
            months, revenue, "r-s", label="Revenue"
        )
        ax_revenue.set_ylabel("Revenue ($)", color="r")
        ax_revenue.tick_params(axis="y", labelcolor="r")

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # ===================== HOVER TOOLTIP =====================
        cursor = mplcursors.cursor(
            [users_line, revenue_line],
            hover=True
        )

        @cursor.connect("add")
        def on_add(sel):
            idx = sel.index

            month = int(df.iloc[idx]["Month"])
            users_val = int(df.iloc[idx]["Users"])
            revenue_val = df.iloc[idx]["Revenue"]

            sel.annotation.set_text(
                f"Month: {month}\n"
                f"Users: {users_val:,}\n"
                f"Revenue: ${revenue_val:,.2f}"
            )

    # ==========================================================
    def export_excel(self):
        if self.current_proj is None:
            messagebox.showerror("No Data", "Run a projection first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )

        if filepath:
            self.current_proj.to_excel(filepath, index=False)
            messagebox.showinfo(
                "Export Complete",
                f"Projections saved to {filepath}"
            )


# ===================== APP ENTRY POINT =====================
if __name__ == "__main__":
    root = tk.Tk()
    app = FinancialApp(root)
    root.mainloop()
