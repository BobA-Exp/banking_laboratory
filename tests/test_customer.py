from datetime import date, datetime, timedelta

import pytest

from banking import BankAccount, Customer


def _years_ago(years):
    today = datetime.now().astimezone().date()
    try:
        return today.replace(year=today.year - years)
    except ValueError:
        return today.replace(year=today.year - years, day=28)


def test_adult_customer_is_created():
    customer = Customer("Ada Lovelace", _years_ago(36))

    assert customer.get_name() == "Ada Lovelace"
    assert customer.get_user_id() == 1
    assert customer.get_accounts() == []


def test_iso_birth_date_string_is_accepted():
    customer = Customer("Ada Lovelace", "1990-01-15")

    assert customer.get_birth_date() == date(1990, 1, 15)


def test_underage_customer_is_rejected():
    with pytest.raises(ValueError, match="at least 18"):
        Customer("Young Customer", _years_ago(10))


def test_invalid_birth_date_is_rejected():
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        Customer("Ada Lovelace", "15-01-1990")


def test_is_adult():
    assert Customer.is_adult(_years_ago(18)) is True
    assert Customer.is_adult(_years_ago(17)) is False
    assert Customer.is_adult(_years_ago(18) + timedelta(days=1)) is False


def test_user_ids_are_consecutive():
    first = Customer("Ada Lovelace", "1990-01-15")
    second = Customer("Alan Turing", "1985-06-23")

    assert first.get_user_id() == 1
    assert second.get_user_id() == 2
    assert Customer.user_count == 2


def test_add_account_appends_valid_account():
    customer = Customer("Ada Lovelace", "1990-01-15")
    account = BankAccount("1234567890", initial_balance=50.0)

    customer.add_account(account)

    assert customer.get_accounts() == [account]


def test_add_account_ignores_invalid_account_number():
    customer = Customer("Ada Lovelace", "1990-01-15")
    account = BankAccount("123", initial_balance=50.0)

    customer.add_account(account)

    assert customer.get_accounts() == []


def test_get_total_balance_sums_accounts():
    customer = Customer("Ada Lovelace", "1990-01-15")
    checking = BankAccount("1234567890", initial_balance=80.0)
    savings = BankAccount.create_savings("0987654321", initial_balance=120.0)
    customer.add_account(checking)
    customer.add_account(savings)

    assert customer.get_total_balance() == 200.0


def test_transfer_moves_funds_between_accounts():
    customer = Customer("Ada Lovelace", "1990-01-15")
    checking = BankAccount("1234567890", initial_balance=200.0)
    savings = BankAccount.create_savings("0987654321", initial_balance=100.0)
    customer.add_account(checking)
    customer.add_account(savings)

    customer.transfer(checking, savings, 50.0)

    assert checking.get_balance() == 150.0
    assert savings.get_balance() == 150.0
    assert customer.get_total_balance() == 300.0


def test_transfer_blocked_by_savings_minimum():
    customer = Customer("Ada Lovelace", "1990-01-15")
    checking = BankAccount("1234567890", initial_balance=50.0)
    savings = BankAccount.create_savings("0987654321", initial_balance=100.0)
    customer.add_account(checking)
    customer.add_account(savings)

    customer.transfer(savings, checking, 25.0)

    assert savings.get_balance() == 100.0
    assert checking.get_balance() == 50.0


def test_transfer_blocked_by_insufficient_funds():
    customer = Customer("Ada Lovelace", "1990-01-15")
    source = BankAccount("1234567890", initial_balance=20.0)
    target = BankAccount("0987654321", initial_balance=10.0)
    customer.add_account(source)
    customer.add_account(target)

    customer.transfer(source, target, 50.0)

    assert source.get_balance() == 20.0
    assert target.get_balance() == 10.0


def test_transfer_same_account_is_ignored():
    customer = Customer("Ada Lovelace", "1990-01-15")
    account = BankAccount("1234567890", initial_balance=80.0)
    customer.add_account(account)

    customer.transfer(account, account, 20.0)

    assert account.get_balance() == 80.0
