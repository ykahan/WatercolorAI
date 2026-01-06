# gui.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from projections import Projections
from utils import compute_effective_arpu


class FinancialApp:
    def __init__(self, master):
        self.master = master
        master.title("Financial Projections")

        # ================= INPUT FRAME =================
        self.frame = ttk.Frame(master, padding=10)
        self.frame.grid(row=0, column=0, sticky="W")

        # Users / growth / churn / months
        self.starting_users_var = tk.StringVar(value="50")
        self.months_var = tk.StringVar(value="60")
        self.growth_var = tk.StringVar(value="8")
        self.churn_var = tk.StringVar(value="2")
        self.growth_type_var = tk.StringVar(value="percentage")
        self.churn_type_var = tk.StringVar(value="percentage")

        # Labels and entries
        entries = [
            ("Starting Users", self.starting_users_var),
            ("Months", self.months_var),
            ("Monthly Growth", self.growth_var),
            ("Monthly Churn", self.churn_var)
        ]
        for i, (label, var) in enumerate(entries):
            ttk.Label(self.frame, text=label).grid(row=i, column=0, sticky="W", pady=2)
            ttk.Entry(self.frame, textvariable=var, width=10).grid(row=i, column=1, pady=2)

        # Radio buttons for absolute vs percentage
        ttk.Label(self.frame, text="Growth Type").grid(row=2, column=2)
        ttk.Radiobutton(self.frame, text="Percentage", variable=self.growth_type_var, value="percentage").grid(row=2, column=3)
        ttk.Radiobutton(self.frame, text="Absolute", variable=self.growth_type_var, value="absolute").grid(row=2, column=4)

        ttk.Label(self.frame, text="Churn Type").grid(row=3, column=2)
        ttk.Radiobutton(self.frame, text="Percentage", variable=self.churn_type_var, value="percentage").grid(row=3, column=3)
        ttk.Radiobutton(self.frame, text="Absolute", variable=self.churn_type_var, value="absolute").grid(row=3, column=4)

        # Payment tiers
        self.tiers = []
        self.tiers_frame = ttk.LabelFrame(self.frame, text="Payment Tiers")
        self.tiers_frame.grid(row=4, column=0, columnspan=5, pady=10, sticky="W")
        ttk.Button(self.frame, text="Add Tier", command=self.add_tier_row).grid(row=5, column=0, columnspan=2, pady=5)

        # Effective ARPU display
        self.arpu_var = tk.StringVar(value="0.00")
        ttk.Label(self.frame, text="Effective ARPU ($/month)").grid(row=6, column=0)
        ttk.Label(self.frame, textvariable=self.arpu_var).grid(row=6, column=1)

        # Buttons
        ttk.Button(self.frame, text="Run Projection", command=self.run_projection).grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(self.frame, text="Export CSV", command=self.export_csv).grid(row=8, column=0, columnspan=2, pady=5)
        ttk.Button(self.frame, text="Exit", command=master.quit).grid(row=9, column=0, columnspan=2, pady=5)

        # Chart frame
        self.chart_frame = ttk.Frame(master)
        self.chart_frame.grid(row=0, column=1, padx=20, sticky="N")

        self.current_proj = None

    # ---------------- PAYMENT TIER UI ----------------
    def add_tier_row(self):
        tier = {
            "price_var": tk.StringVar(value="0"),
            "percent_var": tk.StringVar(value="0"),
            "type_var": tk.StringVar(value="single"),
            "uses_var": tk.StringVar(value="1"),
            "frame_widgets": []  # Store widgets for easy removal/reorder
        }
        row_index = len(self.tiers)

        lbl_price = ttk.Label(self.tiers_frame, text="Price")
        ent_price = ttk.Entry(self.tiers_frame, textvariable=tier["price_var"], width=8)
        lbl_pct = ttk.Label(self.tiers_frame, text="Percentage")
        ent_pct = ttk.Entry(self.tiers_frame, textvariable=tier["percent_var"], width=6)
        lbl_type = ttk.Label(self.tiers_frame, text="Type")
        cmb_type = ttk.Combobox(self.tiers_frame, values=["single", "month", "year"], textvariable=tier["type_var"], width=8)
        lbl_uses = ttk.Label(self.tiers_frame, text="Uses")
        ent_uses = ttk.Entry(self.tiers_frame, textvariable=tier["uses_var"], width=4)
        btn_remove = ttk.Button(self.tiers_frame, text="Remove", command=lambda idx=row_index: self.remove_tier(idx))
        btn_up = ttk.Button(self.tiers_frame, text="↑", command=lambda idx=row_index: self.move_tier_up(idx))
        btn_down = ttk.Button(self.tiers_frame, text="↓", command=lambda idx=row_index: self.move_tier_down(idx))

        widgets = [lbl_price, ent_price, lbl_pct, ent_pct, lbl_type, cmb_type, lbl_uses, ent_uses, btn_remove, btn_up, btn_down]
        tier["frame_widgets"] = widgets
        self.tiers.append(tier)
        self.redraw_tiers()

    def redraw_tiers(self):
        # Clear all widgets first
        for widget in self.tiers_frame.winfo_children():
            widget.grid_forget()

        # Draw header
        headers = ["Price","Price Entry","Pct","Pct Entry","Type","Type Combobox","Uses","Uses Entry","Remove","Up","Down"]
        for col, text in enumerate(headers):
            ttk.Label(self.tiers_frame, text=text).grid(row=0, column=col)

        # Draw each tier
        for row_idx, tier in enumerate(self.tiers):
            for col_idx, widget in enumerate(tier["frame_widgets"]):
                widget.grid(row=row_idx+1, column=col_idx, padx=2, pady=2)

    def remove_tier(self, idx):
        if 0 <= idx < len(self.tiers):
            self.tiers.pop(idx)
            self.redraw_tiers()

    def move_tier_up(self, idx):
        if idx > 0:
            self.tiers[idx], self.tiers[idx-1] = self.tiers[idx-1], self.tiers[idx]
            self.redraw_tiers()

    def move_tier_down(self, idx):
        if idx < len(self.tiers)-1:
            self.tiers[idx], self.tiers[idx+1] = self.tiers[idx+1], self.tiers[idx]
            self.redraw_tiers()

    def get_tier_data(self):
        tier_data = []
        for t in self.tiers:
            try:
                price = float(t["price_var"].get())
                pct = float(t["percent_var"].get())
                type_ = t["type_var"].get()
                uses = int(t["uses_var"].get()) if type_=="single" else 1
                tier_data.append({"price": price, "percentage": pct, "type": type_, "uses": uses})
            except ValueError:
                continue
        return tier_data

    # ---------------- PROJECTIONS ----------------
    def run_projection(self):
        try:
            starting_users = int(self.starting_users_var.get())
            months = int(self.months_var.get())
            growth = float(self.growth_var.get())
            churn = float(self.churn_var.get())
            growth_abs = self.growth_type_var.get() == "absolute"
            churn_abs = self.churn_type_var.get() == "absolute"
        except ValueError:
            messagebox.showerror("Input Error", "Invalid numeric input")
            return

        tiers = self.get_tier_data()
        if not tiers:
            messagebox.showerror("No Tiers", "Add at least one payment tier.")
            return

        self.arpu_var.set(f"{compute_effective_arpu(tiers):.2f}")

        proj = Projections(
            starting_users=starting_users,
            growth_rate=growth,
            churn_rate=churn,
            months=months,
            growth_absolute=growth_abs,
            churn_absolute=churn_abs,
            tiers=tiers
        )
        self.current_proj = proj.project_months()
        self.plot_results(self.current_proj)

    # ---------------- PLOTTING ----------------
    def plot_results(self, df):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig, ax_users = plt.subplots(figsize=(7,4))
        months = df["Month"].values
        users = df["Users"].values
        revenue = df["Revenue"].values

        ax_users.plot(months, users, "b-o", label="Users")
        ax_users.set_xlabel("Month")
        ax_users.set_ylabel("Users", color="b")
        ax_users.tick_params(axis="y", labelcolor="b")

        ax_revenue = ax_users.twinx()
        ax_revenue.plot(months, revenue, "r-s", label="Revenue")
        ax_revenue.set_ylabel("Revenue ($)", color="r")
        ax_revenue.tick_params(axis="y", labelcolor="r")

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---------------- EXPORT ----------------
    def export_csv(self):
        if self.current_proj is None:
            messagebox.showerror("No Data", "Run a projection first.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if filepath:
            self.current_proj.to_csv(filepath, index=False)
            messagebox.showinfo("Export Complete", f"CSV saved to {filepath}")
