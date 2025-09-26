"""
CRITICAL TESTS: Verify no breaking changes to original business logic

These tests ensure that the domain layer preserves the EXACT behavior
of the original TimeDepositCalculator, including the unusual cumulative interest behavior.
"""
import pytest
from src.domain.entities.time_deposit import TimeDeposit, TimeDepositCalculator


def test_exact_original_behavior_basic():
    """Test basic plan matches original logic exactly"""
    deposits = [TimeDeposit(1, "basic", 1000.0, 45)]
    calculator = TimeDepositCalculator()

    calculator.update_balance(deposits)

    # Expected: interest = (1000.0 * 0.01) / 12 = 0.8333...
    # balance = round(1000.0 + ((0.8333... * 100) / 100), 2)
    expected_interest = (1000.0 * 0.01) / 12
    expected_balance = round(1000.0 + ((expected_interest * 100) / 100), 2)

    assert deposits[0].balance == expected_balance
    print(f"Basic plan: {1000.0} -> {deposits[0].balance}")


def test_exact_original_behavior_student():
    """Test student plan matches original logic exactly"""
    deposits = [TimeDeposit(2, "student", 2000.0, 180)]  # Less than 366 days
    calculator = TimeDepositCalculator()

    calculator.update_balance(deposits)

    # Expected: interest = (2000.0 * 0.03) / 12 = 5.0
    # balance = round(2000.0 + ((5.0 * 100) / 100), 2)
    expected_interest = (2000.0 * 0.03) / 12
    expected_balance = round(2000.0 + ((expected_interest * 100) / 100), 2)

    assert deposits[0].balance == expected_balance
    print(f"Student plan: {2000.0} -> {deposits[0].balance}")


def test_exact_original_behavior_premium():
    """Test premium plan matches original logic exactly"""
    deposits = [TimeDeposit(3, "premium", 3000.0, 60)]  # Greater than 45 days
    calculator = TimeDepositCalculator()

    calculator.update_balance(deposits)

    # Expected: interest = (3000.0 * 0.05) / 12 = 12.5
    # balance = round(3000.0 + ((12.5 * 100) / 100), 2)
    expected_interest = (3000.0 * 0.05) / 12
    expected_balance = round(3000.0 + ((expected_interest * 100) / 100), 2)

    assert deposits[0].balance == expected_balance
    print(f"Premium plan: {3000.0} -> {deposits[0].balance}")


def test_cumulative_interest_behavior():
    """
    Test the unusual cumulative interest behavior is preserved

    This is the CRITICAL test that verifies the unusual behavior where:
    - Interest accumulates as the loop progresses
    - Each deposit gets the cumulative interest calculated UP TO THAT POINT in the loop
    """
    deposits = [
        TimeDeposit(1, "basic", 1000.0, 45),      # Gets: (1000*0.01)/12 = 0.833...
        TimeDeposit(2, "student", 2000.0, 180),   # Gets: 0.833... + (2000*0.03)/12 = 5.833...
        TimeDeposit(3, "premium", 3000.0, 60)     # Gets: 5.833... + (3000*0.05)/12 = 18.333...
    ]
    calculator = TimeDepositCalculator()

    calculator.update_balance(deposits)

    # Calculate expected values step by step as the original algorithm does
    interest_step1 = (1000.0 * 0.01) / 12  # 0.833...
    interest_step2 = interest_step1 + (2000.0 * 0.03) / 12  # 5.833...
    interest_step3 = interest_step2 + (3000.0 * 0.05) / 12  # 18.333...

    # Each deposit gets the cumulative interest at its step in the loop
    assert deposits[0].balance == round(1000.0 + ((interest_step1 * 100) / 100), 2)
    assert deposits[1].balance == round(2000.0 + ((interest_step2 * 100) / 100), 2)
    assert deposits[2].balance == round(3000.0 + ((interest_step3 * 100) / 100), 2)

    print(f"Cumulative interest behavior preserved correctly")
    print(f"Final balances: {[d.balance for d in deposits]}")
    print(f"Interest steps: {interest_step1:.6f}, {interest_step2:.6f}, {interest_step3:.6f}")


def test_day_thresholds():
    """Test specific day threshold conditions"""
    # Test basic plan with days <= 30 (should not earn interest)
    basic_no_interest = TimeDeposit(1, "basic", 1000.0, 30)

    # Test student plan with days >= 366 (should not earn interest)
    student_no_interest = TimeDeposit(2, "student", 2000.0, 366)

    # Test premium plan with days <= 45 (should not earn interest)
    premium_no_interest = TimeDeposit(3, "premium", 3000.0, 45)

    deposits = [basic_no_interest, student_no_interest, premium_no_interest]
    calculator = TimeDepositCalculator()

    original_balances = [d.balance for d in deposits]
    calculator.update_balance(deposits)

    # None should have earned interest due to day thresholds
    # But they all get the cumulative interest of 0 (which is 0)
    for i, deposit in enumerate(deposits):
        assert deposit.balance == original_balances[i]

    print("Day thresholds preserved correctly")


def test_edge_case_student_365_days():
    """Test student plan at exactly 365 days (should earn interest)"""
    deposits = [TimeDeposit(1, "student", 1000.0, 365)]
    calculator = TimeDepositCalculator()

    calculator.update_balance(deposits)

    # Should earn interest since days < 366
    expected_interest = (1000.0 * 0.03) / 12
    expected_balance = round(1000.0 + ((expected_interest * 100) / 100), 2)

    assert deposits[0].balance == expected_balance
    print(f"Student 365 days: {1000.0} -> {deposits[0].balance}")


def test_premium_exactly_46_days():
    """Test premium plan at exactly 46 days (should earn interest)"""
    deposits = [TimeDeposit(1, "premium", 1000.0, 46)]
    calculator = TimeDepositCalculator()

    calculator.update_balance(deposits)

    # Should earn interest since days > 45
    expected_interest = (1000.0 * 0.05) / 12
    expected_balance = round(1000.0 + ((expected_interest * 100) / 100), 2)

    assert deposits[0].balance == expected_balance
    print(f"Premium 46 days: {1000.0} -> {deposits[0].balance}")


def test_rounding_behavior():
    """Test that rounding behavior matches original exactly"""
    # Use amounts that will produce specific decimal places
    deposits = [TimeDeposit(1, "basic", 1000.37, 45)]
    calculator = TimeDepositCalculator()

    calculator.update_balance(deposits)

    # Manual calculation to verify rounding
    interest = (1000.37 * 0.01) / 12
    expected_balance = round(1000.37 + ((interest * 100) / 100), 2)

    assert deposits[0].balance == expected_balance
    print(f"Rounding behavior preserved: {1000.37} -> {deposits[0].balance}")


if __name__ == "__main__":
    """Run tests manually for verification"""
    print("Running Critical Business Logic Tests...")

    test_exact_original_behavior_basic()
    test_exact_original_behavior_student()
    test_exact_original_behavior_premium()
    test_cumulative_interest_behavior()
    test_day_thresholds()
    test_edge_case_student_365_days()
    test_premium_exactly_46_days()
    test_rounding_behavior()

    print("\nAll business logic tests passed! Original behavior preserved exactly.")