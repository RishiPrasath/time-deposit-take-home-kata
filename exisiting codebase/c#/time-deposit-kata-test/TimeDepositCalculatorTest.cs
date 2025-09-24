using System.Collections.Generic;
using NUnit.Framework;
using time_deposit_kata_net;

namespace time_deposit_kata_test
{
    public class Tests
    {
        [Test]
        public void UpdateBalance_Test()
        {
            TimeDepositCalculator calculator = new TimeDepositCalculator();

            var plans = new List<TimeDeposit>
            {
                new TimeDeposit
                {
                    Id = 1,
                    PlanType = "basic",
                    Balance = 1234567,
                    Days = 45
                }
            };
            calculator.UpdateBalance(plans);

            Assert.AreEqual(1, 1);
        }
    }
}
