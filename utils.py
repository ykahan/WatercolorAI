# utils.py

def calculate_churned_users(current_users, churn_rate, is_percentage=True):
    """Calculate churned users for the month."""
    if is_percentage:
        return int(current_users * churn_rate / 100)
    else:
        return int(churn_rate)


def calculate_new_users(current_users, growth_rate, is_percentage=True):
    """Calculate new users for the month."""
    if is_percentage:
        return int(current_users * growth_rate / 100)
    else:
        return int(growth_rate)


def compute_effective_arpu(tiers):
    """
    Compute blended ARPU from tiers.
    tiers: list of dicts with keys:
        - 'price'
        - 'percentage'
        - 'type': 'single', 'month', 'year'
        - 'uses': for single-use tiers
    Returns: effective ARPU per month
    """
    arpu = 0
    for tier in tiers:
        pct = tier['percentage'] / 100
        if tier['type'] == 'year':
            monthly_price = tier['price'] / 12
        else:
            monthly_price = tier['price']
        if tier['type'] == 'single':
            monthly_price = monthly_price / max(tier.get('uses', 1), 1)
        arpu += pct * monthly_price
    return arpu
