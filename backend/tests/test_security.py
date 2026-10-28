from datetime import timedelta
import pytest
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing():
    pwd = "StrongPassword987!"
    hashed = get_password_hash(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_creation_and_decoding():
    subject = "123"
    token = create_access_token(subject=subject, extra_claims={"role": "admin"})
    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == subject
    assert payload["role"] == "admin"
    assert "exp" in payload


def test_jwt_expired_token():
    subject = "123"
    expired_delta = timedelta(seconds=-10)
    token = create_access_token(subject=subject, expires_delta=expired_delta)
    payload = decode_access_token(token)
    assert payload is None


def test_jwt_malformed_token():
    assert decode_access_token("not-a-valid-jwt-token") is None

