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
        self._account_type = _account_type                    # Protected, so one prepended underscore
        self.__balance = 0.0                                  # Private, so double prepended underscore

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

        self._name = name                                    # Protected, so one prepended underscore
        self._birth_date = parsed_birth_date                 # Protected, so one prepended underscore
        self._user_id = self._next_user_id()                 # Protected, so one prepended underscore
        self.__accounts = []                                 # Private, so double prepended underscore

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


if __name__ == "__main__":
    account = BankAccount("1234567890", initial_balance=500.0)
    account.deposit(50.0)
    account.withdraw(100.0)
    account.convert_currency("CRC", 520.0)

    savings = BankAccount.create_savings("0987654321", initial_balance=200.0)
    print(savings.get_balance())

    customer = Customer("Ada Lovelace", "1990-01-15")
    customer.add_account(account)
    customer.add_account(savings)
    print(customer.get_total_balance())
    customer.transfer(account, savings, 50.0)
    print(customer.get_total_balance())
