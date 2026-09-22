import logging

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
        self._account_type = _account_type
        self.__balance = 0.0

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


if __name__ == "__main__":
    account = BankAccount("1234567890", initial_balance=500.0)
    account.deposit(50.0)
    account.withdraw(100.0)
    account.convert_currency("CRC", 520.0)

    savings = BankAccount.create_savings("0987654321", initial_balance=200.0)
    print(savings.get_balance())
