import pytest

from banking import BankAccount, InsufficientFundsError


def test_constructor_defaults():
    account = BankAccount("1234567890")

    assert account.get_account_number() == "1234567890"
    assert account.get_currency() == "USD"
    assert account.get_account_type() == "checking"
    assert account.get_balance() == 0.0


def test_constructor_custom_values():
    account = BankAccount("1234567890", "CRC", "checking", 250.0)

    assert account.get_currency() == "CRC"
    assert account.get_account_type() == "checking"
    assert account.get_balance() == 250.0


def test_balance_setter_rejects_negative_value():
    account = BankAccount("1234567890")

    with pytest.raises(ValueError, match="cannot be negative"):
        account.balance = -1.0

    assert account.get_balance() == 0.0


def test_deposit_increases_balance():
    account = BankAccount("1234567890", initial_balance=100.0)

    account.deposit(50.0)

    assert account.get_balance() == 150.0


def test_deposit_rejects_negative_amount():
    account = BankAccount("1234567890", initial_balance=100.0)

    with pytest.raises(ValueError, match="cannot be negative"):
        account.deposit(-10.0)

    assert account.get_balance() == 100.0


def test_withdraw_decreases_balance():
    account = BankAccount("1234567890", initial_balance=100.0)

    account.withdraw(40.0)

    assert account.get_balance() == 60.0


def test_withdraw_rejects_negative_amount():
    account = BankAccount("1234567890", initial_balance=100.0)

    with pytest.raises(ValueError, match="cannot be negative"):
        account.withdraw(-10.0)

    assert account.get_balance() == 100.0


def test_withdraw_insufficient_funds_raises_and_stores_amount():
    account = BankAccount("1234567890", initial_balance=25.0)

    with pytest.raises(InsufficientFundsError) as exc_info:
        account.withdraw(50.0)

    assert exc_info.value.attempted_withdrawal == 50.0
    assert account.get_balance() == 25.0


def test_savings_withdraw_cannot_fall_below_minimum():
    account = BankAccount.create_savings("0987654321", initial_balance=150.0)

    with pytest.raises(InsufficientFundsError) as exc_info:
        account.withdraw(60.0)

    assert exc_info.value.attempted_withdrawal == 60.0
    assert account.get_balance() == 150.0


def test_create_savings_sets_account_type_and_balance():
    account = BankAccount.create_savings("0987654321", initial_balance=200.0)

    assert account.get_account_type() == "savings"
    assert account.get_balance() == 200.0


def test_create_savings_rejects_balance_below_minimum():
    with pytest.raises(ValueError, match="at least \\$100"):
        BankAccount.create_savings("0987654321", initial_balance=99.0)


def test_is_valid_account_number():
    assert BankAccount.is_valid_account_number("1234567890") is True
    assert BankAccount.is_valid_account_number("123456789") is False
    assert BankAccount.is_valid_account_number("12345678901") is False
    assert BankAccount.is_valid_account_number("123456789a") is False
    assert BankAccount.is_valid_account_number(1234567890) is False


def test_convert_currency_prints_converted_balance(capsys):
    account = BankAccount("1234567890", initial_balance=100.0)

    account.convert_currency("CRC", 520.0)

    assert capsys.readouterr().out.strip() == "52000.00 CRC"


def test_convert_currency_rejects_non_positive_rate():
    account = BankAccount("1234567890", initial_balance=100.0)

    with pytest.raises(ValueError, match="greater than zero"):
        account.convert_currency("CRC", 0)

    with pytest.raises(ValueError, match="greater than zero"):
        account.convert_currency("CRC", -2.0)
