# projections.py

import pandas as pd
from utils import calculate_churned_users, calculate_new_users, compute_effective_arpu

class Projections:
    def __init__(self, starting_users, growth_rate, churn_rate, months,
                 growth_absolute=False, churn_absolute=False, tiers=None):
        """
        tiers: list of dicts, same as in compute_effective_arpu
        """
        self.starting_users = starting_users
        self.growth_rate = growth_rate
        self.churn_rate = churn_rate
        self.months = months
        self.growth_absolute = growth_absolute
        self.churn_absolute = churn_absolute
        self.tiers = tiers or []

        self.arpu = compute_effective_arpu(self.tiers)

        self.df = pd.DataFrame(columns=["Month", "Users", "Revenue"])
        self.df.loc[0] = [0, starting_users, starting_users * self.arpu]

    def step(self, month):
        last_users = self.df["Users"].iloc[-1]
        new_users = calculate_new_users(last_users, self.growth_rate, not self.growth_absolute)
        churned = calculate_churned_users(last_users, self.churn_rate, not self.churn_absolute)
        next_users = last_users + new_users - churned
        next_revenue = next_users * self.arpu
        self.df.loc[month] = [month, next_users, next_revenue]

    def project_months(self):
        for month in range(1, self.months + 1):
            self.step(month)
        return self.df

    def export_csv(self, filepath):
        self.df.to_csv(filepath, index=False)
