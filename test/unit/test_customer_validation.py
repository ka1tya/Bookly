import pytest
from unittest.mock import MagicMock
from src.services.customer_service import register_customer, validate_address, validate_customer
from src.services.errors import ValidationError

def test_valid_customer():
    validate_customer("Ірина", "Мельник", "kissmyas@gmail.com", "+380661234567")

@pytest.mark.parametrize("first_name, last_name, email, phone", [
    ("", "Мельник", "kissmyas@gmail.com", "+380661234567"),
    ("Ірина", "Мельник", "kissmyas.gmail.com", "+380661234567"),
    ("Ірина", "Мельник", "kissmyas@gmail.com", "12345"),
    ("Ірина", "Мельник", "kissmyas@gmail.com", "+38066abc4567"),
])
def test_invalid_customer(first_name, last_name, email, phone):
    with pytest.raises(ValidationError):
        validate_customer(first_name, last_name, email, phone)

@pytest.mark.parametrize("email", [
    "Kissmyas@gmail.com",
    "iryna.melnyk@ukr.net",
    "iryna+shop@gmail.com",
])
def test_valid_email(email):
    validate_customer("Ірина", "Мельник", email, "+380661234567")

@pytest.mark.parametrize("email", [
    "@gmail.com",
    "kissmyas@",
    "kissmyas@gmail",
    "kiss myas@gmail.com",
    "kissmyas@@gmail.com",
])
def test_invalid_email(email):
    with pytest.raises(ValidationError):
        validate_customer("Ірина", "Мельник", email, "+380661234567")

def test_valid_address():
    validate_address({"country": "Україна", "city": "Київ", "street": "вул. Хрещатик 1"})

def test_address_without_city():
    with pytest.raises(ValidationError):
        validate_address({"country": "Україна", "city": "", "street": "вул. Хрещатик 1"})

def test_register_without_addresses():
    session = MagicMock()
    with pytest.raises(ValidationError):
        register_customer(session, "Ірина", "Мельник", "kissmyas@gmail.com", "+380661234567", [])
    session.commit.assert_not_called()
