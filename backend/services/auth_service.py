
import bcrypt
import re

from backend.services.database_service import (
    create_user,
    get_user_by_email
)


def validate_registration(name, email, password):

    if not name.strip():
        return False, "Please enter your name."

    if not re.fullmatch(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        email.strip()
    ):
        return False, "Please enter a valid email address."

    if len(password.encode("utf-8")) < 8:
        return False, "Password must contain at least 8 characters."

    if len(password.encode("utf-8")) > 72:
        return False, "Password is too long. Maximum 72 UTF-8 bytes."

    return True, "Valid registration details."


def register_user(name, email, password):

    name = name.strip()
    email = email.strip().lower()

    valid, message = validate_registration(
        name, email, password
    )

    if not valid:
        return False, message

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    created = create_user(
        name,
        email,
        password_hash
    )

    if not created:
        return False, "An account with this email already exists."

    return True, "Registration successful. Please log in."


def login_user(email, password):

    email = email.strip().lower()

    user = get_user_by_email(email)

    if user is None:
        return False, None, "Invalid email or password."

    stored_hash = user["password_hash"].encode("utf-8")

    password_valid = bcrypt.checkpw(
        password.encode("utf-8"),
        stored_hash
    )

    if not password_valid:
        return False, None, "Invalid email or password."

    user_data = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"]
    }

    return True, user_data, "Login successful."
