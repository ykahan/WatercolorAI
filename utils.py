def calculate_new_users(current_users: float, growth_rate: float) -> float:
    """Calculate new users this month."""
    return current_users * growth_rate

def calculate_churned_users(current_users: float, churn_rate: float) -> float:
    """Calculate churned users this month."""
    return current_users * churn_rate
