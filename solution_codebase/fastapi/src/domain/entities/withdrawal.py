"""
Withdrawal entity for API requirements
"""


class Withdrawal:
    """
    Withdrawal entity for managing withdrawal data

    Used for API response formatting but not part of original business logic
    """
    def __init__(self, id: int, amount: float, date: str):
        self.id = id
        self.amount = amount
        self.date = date

    def __repr__(self):
        return f"Withdrawal(id={self.id}, amount={self.amount}, date='{self.date}')"