import pytest

from banking import Customer


@pytest.fixture(autouse=True)
def reset_user_count():
    Customer.user_count = 0
    yield
    Customer.user_count = 0
