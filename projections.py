import pandas as pd
from utils import calculate_churned_users, calculate_new_users

class Projections:
    def __init__(self, starting_users, growth_rate, churn_rate, arpu):
        self.starting_users = starting_users
        self.growth_rate = growth_rate / 100  # percent to decimal
        self.churn_rate = churn_rate / 100
        self.arpu = arpu

        # Initialize DataFrame to store projections
        self.df = pd.DataFrame(columns=["Month", "Users", "Revenue"])
        self.df.loc[0] = [0, starting_users, starting_users * arpu]

    def step(self, month):
        """Compute one month projection."""
        last_users = self.df["Users"].iloc[-1]
        new_users = calculate_new_users(last_users, self.growth_rate)
        churned = calculate_churned_users(last_users, self.churn_rate)
        next_users = last_users + new_users - churned
        next_revenue = next_users * self.arpu

        self.df.loc[month] = [month, next_users, next_revenue]

    def project_months(self, months=12):
        """Project multiple months."""
        for month in range(1, months + 1):
            self.step(month)
        return self.df

    def export_excel(self, filepath):
        """Export the projections to an Excel file."""
        self.df.to_excel(filepath, index=False)
