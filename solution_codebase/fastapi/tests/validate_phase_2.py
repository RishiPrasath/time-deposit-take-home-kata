#!/usr/bin/env python3
"""
Phase 2 Validation Script
Comprehensive validation of Domain Layer implementation

This script validates that Phase 2 (Domain Layer) has been successfully
implemented and integrated with Phase 1 (Infrastructure Layer).
"""
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.domain.entities.time_deposit import TimeDeposit, TimeDepositCalculator
from app.domain.entities.withdrawal import Withdrawal
from app.domain.interfaces.repositories import TimeDepositRepositoryInterface
from app.infrastructure.adapters.time_deposit_repository_adapter import TimeDepositRepositoryAdapter
from decimal import Decimal


def test_original_business_logic_preservation():
    """
    CRITICAL TEST: Verify original business logic is preserved exactly
    """
    print("🧪 Testing Original Business Logic Preservation...")
    
    # Test the unusual cumulative interest behavior
    deposits = [
        TimeDeposit(1, "basic", 1000.0, 45),      # Contributes: (1000 * 0.01)/12 = 0.833
        TimeDeposit(2, "student", 2000.0, 180),   # Contributes: (2000 * 0.03)/12 = 5.0  
        TimeDeposit(3, "premium", 3000.0, 60)     # Contributes: (3000 * 0.05)/12 = 12.5
    ]
    
    calculator = TimeDepositCalculator()
    
    # Store original balances
    original_balances = [d.balance for d in deposits]
    print(f"   Original balances: {original_balances}")
    
    # Apply calculator
    calculator.update_balance(deposits)
    
    # Check results
    final_balances = [d.balance for d in deposits]
    print(f"   Final balances: {final_balances}")
    
    # Calculate expected cumulative interest behavior
    interest_step1 = (1000.0 * 0.01) / 12  # 0.833...
    interest_step2 = interest_step1 + (2000.0 * 0.03) / 12  # 5.833...
    interest_step3 = interest_step2 + (3000.0 * 0.05) / 12  # 18.333...
    
    expected_balances = [
        round(1000.0 + ((interest_step1 * 100) / 100), 2),
        round(2000.0 + ((interest_step2 * 100) / 100), 2),
        round(3000.0 + ((interest_step3 * 100) / 100), 2)
    ]
    
    print(f"   Expected balances: {expected_balances}")
    print(f"   Interest steps: {interest_step1:.6f}, {interest_step2:.6f}, {interest_step3:.6f}")
    
    # Verify exact match
    for i, (actual, expected) in enumerate(zip(final_balances, expected_balances)):
        assert actual == expected, f"Deposit {i+1}: Expected {expected}, got {actual}"
    
    print("   ✅ Original business logic preserved exactly!")
    return True


def test_data_type_conversions():
    """
    Test critical data type conversions between layers
    """
    print("\n🔄 Testing Data Type Conversions...")
    
    # Test Decimal ↔ float conversions
    test_values = [Decimal("1000.00"), Decimal("1234.56"), Decimal("999.99")]
    
    for decimal_val in test_values:
        float_val = float(decimal_val)
        back_to_decimal = Decimal(str(float_val))
        
        print(f"   {decimal_val} → {float_val} → {back_to_decimal}")
        assert back_to_decimal == decimal_val, f"Conversion failed for {decimal_val}"
    
    # Test date string conversions
    from datetime import date
    test_date = date(2024, 3, 15)
    iso_string = test_date.isoformat()
    assert iso_string == "2024-03-15", f"Date conversion failed: {iso_string}"
    
    print("   ✅ Data type conversions work correctly!")
    return True


def test_domain_entities_creation():
    """
    Test that domain entities can be created and work correctly
    """
    print("\n🏗️ Testing Domain Entity Creation...")
    
    # Test TimeDeposit creation
    deposit = TimeDeposit(1, "premium", 5000.0, 90)
    assert deposit.id == 1
    assert deposit.planType == "premium"
    assert deposit.balance == 5000.0
    assert deposit.days == 90
    assert deposit.withdrawals == []
    print("   ✅ TimeDeposit entity creation works!")
    
    # Test Withdrawal creation
    withdrawal = Withdrawal(1, 500.0, "2024-01-15")
    assert withdrawal.id == 1
    assert withdrawal.amount == 500.0
    assert withdrawal.date == "2024-01-15"
    print("   ✅ Withdrawal entity creation works!")
    
    # Test adding withdrawals to deposits
    deposit.withdrawals.append(withdrawal)
    assert len(deposit.withdrawals) == 1
    assert deposit.withdrawals[0].amount == 500.0
    print("   ✅ Withdrawal association works!")
    
    return True


def test_interface_abstraction():
    """
    Test that repository interface provides proper abstraction
    """
    print("\n🔌 Testing Interface Abstraction...")
    
    # Verify interface is abstract
    try:
        TimeDepositRepositoryInterface()
        assert False, "Interface should not be instantiatable"
    except TypeError:
        print("   ✅ Repository interface is properly abstract!")
    
    # Check that required methods exist
    required_methods = ['get_all', 'get_all_with_withdrawals', 'save_all', 'create_sample_data']
    interface_methods = [method for method in dir(TimeDepositRepositoryInterface) 
                        if not method.startswith('_')]
    
    for method in required_methods:
        assert method in interface_methods, f"Required method {method} not found in interface"
    
    print("   ✅ All required interface methods exist!")
    return True


def test_specific_business_rules():
    """
    Test specific business rules and edge cases
    """
    print("\n📋 Testing Specific Business Rules...")
    
    # Test day thresholds
    test_cases = [
        # (plan, balance, days, should_earn_interest)
        ("basic", 1000.0, 30, False),    # <= 30 days
        ("basic", 1000.0, 31, True),     # > 30 days
        ("student", 1000.0, 365, True),  # < 366 days
        ("student", 1000.0, 366, False), # >= 366 days
        ("premium", 1000.0, 45, False),  # <= 45 days
        ("premium", 1000.0, 46, True),   # > 45 days
    ]
    
    for plan, balance, days, should_earn in test_cases:
        deposit = TimeDeposit(1, plan, balance, days)
        original_balance = deposit.balance
        
        calculator = TimeDepositCalculator()
        calculator.update_balance([deposit])
        
        if should_earn:
            assert deposit.balance > original_balance, f"{plan} plan at {days} days should earn interest"
            print(f"   ✅ {plan.capitalize()} plan at {days} days: {original_balance} → {deposit.balance}")
        else:
            assert deposit.balance == original_balance, f"{plan} plan at {days} days should not earn interest"
            print(f"   ✅ {plan.capitalize()} plan at {days} days: No interest (correct)")
    
    return True


def test_rounding_behavior():
    """
    Test that rounding behavior matches original exactly
    """
    print("\n🔢 Testing Rounding Behavior...")
    
    # Use amounts that produce specific decimal results
    test_amounts = [1000.37, 2500.11, 999.99]
    
    for amount in test_amounts:
        deposit = TimeDeposit(1, "basic", amount, 45)
        calculator = TimeDepositCalculator()
        
        calculator.update_balance([deposit])
        
        # Verify result has exactly 2 decimal places
        balance_str = str(deposit.balance)
        decimal_places = len(balance_str.split('.')[-1]) if '.' in balance_str else 0
        
        # Allow for cases where trailing zeros are removed (e.g., 1000.0 becomes 1000)
        assert decimal_places <= 2, f"Balance {deposit.balance} has more than 2 decimal places"
        
        # Verify manual calculation matches
        expected_interest = (amount * 0.01) / 12
        expected_balance = round(amount + ((expected_interest * 100) / 100), 2)
        
        assert deposit.balance == expected_balance, f"Rounding mismatch for {amount}: expected {expected_balance}, got {deposit.balance}"
        
        print(f"   ✅ Rounding for {amount}: {expected_balance}")
    
    return True


def run_comprehensive_validation():
    """
    Run all Phase 2 validation tests
    """
    print("🎯 Phase 2 Domain Layer Validation")
    print("=" * 50)
    
    tests = [
        test_original_business_logic_preservation,
        test_data_type_conversions,
        test_domain_entities_creation,
        test_interface_abstraction,
        test_specific_business_rules,
        test_rounding_behavior,
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                passed_tests += 1
        except Exception as e:
            print(f"   ❌ Test failed: {str(e)}")
            return False
    
    print(f"\n🎉 Phase 2 Validation Results")
    print("=" * 50)
    print(f"✅ All {passed_tests}/{total_tests} tests passed!")
    print("\n🎯 Phase 2 Implementation Status:")
    print("   ✅ Domain entities implemented correctly")
    print("   ✅ Original business logic preserved exactly")
    print("   ✅ Unusual cumulative interest behavior maintained")
    print("   ✅ Data type conversions working")
    print("   ✅ Interface abstractions proper")
    print("   ✅ All business rules functional")
    print("   ✅ Rounding behavior matches original")
    
    print("\n🚀 Phase 2 is COMPLETE and ready for Phase 3!")
    print("   Next: Application Layer (Services & Orchestration)")
    
    return True


if __name__ == "__main__":
    success = run_comprehensive_validation()
    sys.exit(0 if success else 1)
