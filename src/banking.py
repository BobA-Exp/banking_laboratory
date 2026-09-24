import logging
from datetime import date, datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class InsufficientFundsError(Exception):
    def __init__(self, message, attempted_withdrawal):
        super().__init__(message)
        self.attempted_withdrawal = attempted_withdrawal


class BankAccount:
    MINIMUM_SAVINGS_BALANCE = 100.0

    def __init__(
        self,
        account_number,
        currency="USD",
        _account_type="checking",
        initial_balance=0.0,
    ):
        self.account_number = account_number
        self.currency = currency
        self._account_type = _account_type  # Protected, so one prepended underscore
        self.__balance = 0.0  # Private, so double prepended underscore

        if (
            self._account_type == "savings"
            and initial_balance < self.MINIMUM_SAVINGS_BALANCE
        ):
            logger.error("Savings accounts require at least $100.00.")
            raise ValueError("Savings accounts require at least $100.00.")

        self.balance = initial_balance

    # Getters
    def get_account_number(self):
        return self.account_number

    def get_currency(self):
        return self.currency

    def get_account_type(self):
        return self._account_type

    def get_balance(self):
        return self.__balance

    # Getter and setter for the private balance
    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, new_balance):
        if new_balance < 0:
            logger.error("The balance cannot be negative.")
            raise ValueError("The balance cannot be negative.")

        self.__balance = new_balance

    def deposit(self, amount):
        if amount < 0:
            logger.error("Deposit amount cannot be negative.")
            raise ValueError("Deposit amount cannot be negative.")

        self.__balance += amount
        logger.info("Deposit completed. Balance: %.2f", self.__balance)

    def withdraw(self, amount):
        if amount < 0:
            logger.error("Withdrawal amount cannot be negative.")
            raise ValueError("Withdrawal amount cannot be negative.")

        if amount > self.__balance:
            logger.error("Insufficient funds for withdrawal of %.2f.", amount)
            raise InsufficientFundsError(
                "Insufficient funds for this withdrawal.",
                amount,
            )

        new_balance = self.__balance - amount

        if (
            self._account_type == "savings"
            and new_balance < self.MINIMUM_SAVINGS_BALANCE
        ):
            logger.error("Savings accounts cannot fall below $100.00.")
            raise InsufficientFundsError(
                "Savings accounts cannot fall below $100.00.",
                amount,
            )

        self.__balance = new_balance
        logger.info("Withdrawal completed. Balance: %.2f", self.__balance)

    def convert_currency(self, target_currency, exchange_rate):
        if exchange_rate <= 0:
            logger.error("Exchange rate must be greater than zero.")
            raise ValueError("Exchange rate must be greater than zero.")

        converted_balance = self.__balance * exchange_rate
        print(f"{converted_balance:.2f} {target_currency}")

    @classmethod
    def create_savings(cls, account_number, currency="USD", initial_balance=100.0):
        return cls(
            account_number,
            currency,
            "savings",
            initial_balance,
        )

    @staticmethod
    def is_valid_account_number(account_number):
        return (
            isinstance(account_number, str)
            and len(account_number) == 10
            and account_number.isdigit()
        )


class Customer:
    user_count = 0

    def __init__(self, name, birth_date):
        parsed_birth_date = self._parse_birth_date(birth_date)
        if not self.is_adult(parsed_birth_date):
            logger.error("Customer must be at least 18 years old.")
            raise ValueError("Customer must be at least 18 years old.")

        self._name = name  # Protected, so one prepended underscore
        self._birth_date = parsed_birth_date  # Protected, so one prepended underscore
        self._user_id = self._next_user_id()  # Protected, so one prepended underscore
        self.__accounts = []  # Private, so double prepended underscore

    @staticmethod
    def _parse_birth_date(birth_date):
        if isinstance(birth_date, datetime):
            return birth_date.date()
        if isinstance(birth_date, date):
            return birth_date
        if isinstance(birth_date, str):
            try:
                return date.fromisoformat(birth_date)
            except ValueError:
                logger.error("Invalid birth date format: %s", birth_date)
                raise ValueError("Birth date must be YYYY-MM-DD.") from None

        logger.error("Invalid birth date type: %s", type(birth_date).__name__)
        raise ValueError("Birth date must be a date or YYYY-MM-DD string.")

    @staticmethod
    def is_adult(birth_date):
        today = datetime.now().astimezone().date()
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )
        return age >= 18

    @classmethod
    def _next_user_id(cls):
        cls.user_count += 1
        return cls.user_count

    @property
    def name(self):
        return self._name

    @property
    def birth_date(self):
        return self._birth_date

    @property
    def user_id(self):
        return self._user_id

    @property
    def accounts(self):
        return list(self.__accounts)

    def get_name(self):
        return self.name

    def get_birth_date(self):
        return self.birth_date

    def get_user_id(self):
        return self._user_id

    def get_accounts(self):
        return list(self.__accounts)

    def add_account(self, account):
        if not BankAccount.is_valid_account_number(account.get_account_number()):
            logger.error("Invalid account number: %s", account.get_account_number())
            return

        self.__accounts.append(account)

    def get_total_balance(self):
        return sum(account.get_balance() for account in self.__accounts)

    def transfer(self, source_account, target_account, amount):
        if source_account is target_account:
            logger.error("Source and target accounts must be different.")
            return

        if (
            source_account not in self.__accounts
            or target_account not in self.__accounts
        ):
            logger.error("Both accounts must belong to this customer.")
            return

        try:
            source_account.withdraw(amount)
            target_account.deposit(amount)
        except (InsufficientFundsError, ValueError) as exc:
            logger.error("Transfer failed: %s", exc)


def _find_customer(customers, user_id):
    for customer in customers:
        if customer.get_user_id() == user_id:
            return customer
    return None


def _find_account(customer, account_number):
    for account in customer.get_accounts():
        if account.get_account_number() == account_number:
            return account
    return None


def _prompt_int(message):
    try:
        return int(input(message))
    except ValueError:
        print("Please enter a valid integer.")
        return None


def _prompt_float(message):
    try:
        return float(input(message))
    except ValueError:
        print("Please enter a valid number.")
        return None


def _add_customer(customers):
    name = input("Customer name: ").strip()
    birth_date = input("Birth date (YYYY-MM-DD): ").strip()
    try:
        customer = Customer(name, birth_date)
    except ValueError as exc:
        print(f"Could not add customer: {exc}")
        return

    customers.append(customer)
    print(f"Customer added. User ID: {customer.get_user_id()}")


def _add_account(customers):
    user_id = _prompt_int("Customer user ID: ")
    if user_id is None:
        return

    customer = _find_customer(customers, user_id)
    if customer is None:
        print(f"No customer found with user ID {user_id}.")
        return

    account_type = input("Account type (checking/savings): ").strip().lower()
    account_number = input("Account number (10 digits): ").strip()
    currency = input("Currency [USD]: ").strip() or "USD"
    initial_balance = _prompt_float("Initial balance: ")
    if initial_balance is None:
        return

    try:
        if account_type == "savings":
            account = BankAccount.create_savings(
                account_number,
                currency,
                initial_balance,
            )
        elif account_type == "checking":
            account = BankAccount(
                account_number,
                currency,
                "checking",
                initial_balance,
            )
        else:
            print("Account type must be checking or savings.")
            return
    except ValueError as exc:
        print(f"Could not create account: {exc}")
        return

    customer.add_account(account)
    if account in customer.get_accounts():
        print(f"Account {account.get_account_number()} added to user {user_id}.")
    else:
        print("Account was not added. Check the account number.")


def _select_customer(customers):
    user_id = _prompt_int("Customer user ID: ")
    if user_id is None:
        return None

    customer = _find_customer(customers, user_id)
    if customer is None:
        print(f"No customer found with user ID {user_id}.")
    return customer


def _select_account(customer, label="Account number"):
    account_number = input(f"{label}: ").strip()
    account = _find_account(customer, account_number)
    if account is None:
        print(f"No account found with number {account_number}.")
    return account


def _handle_deposit(customers):
    customer = _select_customer(customers)
    if customer is None:
        return

    account = _select_account(customer)
    if account is None:
        return

    amount = _prompt_float("Amount: ")
    if amount is None:
        return

    try:
        account.deposit(amount)
    except ValueError as exc:
        print(f"Deposit failed: {exc}")


def _handle_withdraw(customers):
    customer = _select_customer(customers)
    if customer is None:
        return

    account = _select_account(customer)
    if account is None:
        return

    amount = _prompt_float("Amount: ")
    if amount is None:
        return

    try:
        account.withdraw(amount)
    except (ValueError, InsufficientFundsError) as exc:
        print(f"Withdrawal failed: {exc}")


def _handle_convert(customers):
    customer = _select_customer(customers)
    if customer is None:
        return

    account = _select_account(customer)
    if account is None:
        return

    target_currency = input("Target currency: ").strip()
    exchange_rate = _prompt_float("Exchange rate: ")
    if exchange_rate is None:
        return

    try:
        account.convert_currency(target_currency, exchange_rate)
    except ValueError as exc:
        print(f"Conversion failed: {exc}")


def _handle_transfer(customers):
    customer = _select_customer(customers)
    if customer is None:
        return

    source_account = _select_account(customer, "Source account number")
    if source_account is None:
        return

    target_account = _select_account(customer, "Target account number")
    if target_account is None:
        return

    amount = _prompt_float("Amount: ")
    if amount is None:
        return

    customer.transfer(source_account, target_account, amount)


def _handle_total_balance(customers):
    customer = _select_customer(customers)
    if customer is None:
        return

    print(f"Total balance: {customer.get_total_balance():.2f}")


def _transactions_menu(customers):
    while True:
        print("\nTransactions")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Convert currency")
        print("4. Transfer")
        print("5. Show total balance")
        print("6. Back")
        choice = input("Select an option: ").strip()

        if choice == "1":
            _handle_deposit(customers)
        elif choice == "2":
            _handle_withdraw(customers)
        elif choice == "3":
            _handle_convert(customers)
        elif choice == "4":
            _handle_transfer(customers)
        elif choice == "5":
            _handle_total_balance(customers)
        elif choice == "6":
            return
        else:
            print("Invalid option.")


def menu():
    customers = []
    while True:
        print("\nBanking Laboratory")
        print("1. Add customer")
        print("2. Add bank account")
        print("3. Transactions")
        print("4. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            _add_customer(customers)
        elif choice == "2":
            _add_account(customers)
        elif choice == "3":
            _transactions_menu(customers)
        elif choice == "4":
            print("Goodbye.")
            return
        else:
            print("Invalid option.")


if __name__ == "__main__":
    menu()
