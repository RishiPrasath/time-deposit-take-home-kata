using System;
using System.Collections.Generic;

namespace time_deposit_kata_net
{
    public class TimeDepositCalculator
    {
        public void UpdateBalance(List<TimeDeposit> temps)
        {
            for (int i = 0; i < temps.Count; i++)
            {
                double interest = 0;

                if (temps[i].Days > 30)
                {
                    if (temps[i].PlanType == "student")
                    {
                        if (temps[i].Days < 366)
                        {
                            interest += temps[i].Balance * 0.03 / 12;
                        }
                    }
                    else if (temps[i].PlanType == "premium")
                    {
                        if (temps[i].Days > 45)
                        {
                            interest += temps[i].Balance * 0.05 / 12;
                        }
                    }
                    else if (temps[i].PlanType == "basic")
                    {
                        interest += temps[i].Balance * 0.01 / 12;
                    }
                }

                temps[i].Balance += Math.Round(interest, 2);
            }
        }
    }
}

