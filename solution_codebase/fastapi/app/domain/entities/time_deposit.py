"""
CRITICAL: EXACT COPY from original codebase - NO MODIFICATIONS
Source: Original time_deposit.py file

Original TimeDeposit entity and calculator - PRESERVED EXACTLY

⚠️ ZERO CHANGES ALLOWED - This must match original behavior exactly
"""


class TimeDeposit:
    """
    Original TimeDeposit entity - PRESERVED EXACTLY

    ⚠️ ZERO CHANGES ALLOWED - This must match original behavior exactly
    """
    def __init__(self, id, planType, balance, days):
        self.id = id
        self.planType = planType
        self.balance = balance
        self.days = days
        # Note: Original doesn't have withdrawals property!
        # We'll add it for API requirements but keep constructor unchanged
        self.withdrawals = []


class TimeDepositCalculator:
    """
    Original business logic - PRESERVED EXACTLY

    ⚠️ CRITICAL: This has unusual cumulative interest behavior that MUST be preserved
    - Interest accumulates across ALL deposits
    - Same cumulative interest applied to EACH deposit
    - Monthly rates (annual rate / 12)
    - Specific day thresholds and conditions
    """

    def update_balance(self, xs):
        """
        EXACT COPY - NO MODIFICATIONS WHATSOEVER

        Unusual behavior (but must be preserved):
        1. Calculates cumulative interest across ALL deposits
        2. Applies same cumulative interest to EACH individual deposit
        3. Uses monthly rates (annual / 12)
        4. Specific conditions for each plan type

        Args:
            xs: List of TimeDeposit objects to update
        """
        interest = 0
        for td in xs:
            if td.days > 30:
                if td.planType == 'student':
                    if td.days < 366:
                        interest += (td.balance * 0.03)/12
                elif td.planType == 'premium':
                    if td.days > 45:
                        interest += (td.balance * 0.05)/12
                elif td.planType == 'basic':
                    interest += (td.balance * 0.01) / 12
            td.balance = round(td.balance + ((interest * 100) / 100), 2)