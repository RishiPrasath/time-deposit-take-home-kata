class TimeDeposit:
    def __init__(self, id, planType, balance, days):
        self.id = id
        self.planType = planType
        self.balance = balance
        self.days = days


class TimeDepositCalculator:

    def update_balance(self,xs):
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

