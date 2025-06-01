from datetime import datetime, timedelta, UTC
from unittest.mock import patch

import jwt
import pytest
from passlib.exc import UnknownHashError

from app.core.config import settings
from app.core.security import (
    get_password_hash,
    verify_password,
    create_jwt_token,
    decode_jwt_token,
    verify_jwt_token,
)
from app.exceptions import (
    TokenExpiredError,
    InvalidTokenError,
    MissingTokenError,
    InvalidTokenPayloadError,
)


class TestPasswordHashing:
    def test_get_password_hash_returns_string(self):
        hashed = get_password_hash("testpassword")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        hashed = get_password_hash("testpassword")
        assert verify_password("testpassword", hashed) is True

    def test_verify_password_incorrect(self):
        hashed = get_password_hash("testpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_password_invalid_hash(self):
        with pytest.raises(UnknownHashError):
            verify_password("testpassword", "invalidhash")


class TestJWTTokenCreation:
    def test_create_jwt_token_returns_string(self):
        token = create_jwt_token({"sub": "testuser"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_jwt_token_contains_expiry(self):
        with patch("app.core.security.datetime") as mock_datetime:
            fixed_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
            mock_datetime.now.return_value = fixed_time

            token = create_jwt_token({"sub": "testuser"})
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": False})

            expected_exp = int((fixed_time + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp())
            assert decoded["exp"] == expected_exp


class TestJWTTokenDecoding:
    def test_decode_valid_token(self):
        token = create_jwt_token({"sub": "testuser"})
        decoded = decode_jwt_token(token)
        assert decoded["sub"] == "testuser"
        assert "exp" in decoded

    def test_decode_invalid_token(self):
        invalid_token = "invalid.token.here"
        with pytest.raises(jwt.PyJWTError):
            decode_jwt_token(invalid_token)


class TestJWTTokenVerification:
    def test_verify_valid_token(self):
        token = create_jwt_token({"sub": "testuser"})
        payload = verify_jwt_token(token)
        assert payload["sub"] == "testuser"

    def test_verify_missing_token(self):
        with pytest.raises(MissingTokenError):
            verify_jwt_token(None)

        with pytest.raises(MissingTokenError):
            verify_jwt_token("")

    def test_verify_expired_token(self):
        expired_payload = {
            "sub": "testuser",
            "exp": datetime.now(UTC) - timedelta(minutes=1)
        }
        expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        with pytest.raises(TokenExpiredError):
            verify_jwt_token(expired_token)

    def test_verify_invalid_token(self):
        with pytest.raises(InvalidTokenError):
            verify_jwt_token("invalid.token.here")

    def test_verify_token_missing_subject(self):
        payload_without_sub = {"username": "testuser"}  # Missing 'sub' field
        invalid_token = jwt.encode(payload_without_sub, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        with pytest.raises(InvalidTokenPayloadError) as exc_info:
            verify_jwt_token(invalid_token)

        assert "sub" in str(exc_info.value)

    def test_verify_token_with_empty_subject(self):
        payload_empty_sub = {"sub": ""}
        invalid_token = jwt.encode(payload_empty_sub, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        with pytest.raises(InvalidTokenPayloadError) as exc_info:
            verify_jwt_token(invalid_token)

        assert "sub" in str(exc_info.value)


class TestEdgeCases:
    def test_create_token_with_empty_payload(self):
        token = create_jwt_token({})
        decoded = decode_jwt_token(token)
        assert "exp" in decoded
        assert len(decoded) == 1  # Only contains exp

    def test_verify_token_with_additional_fields(self):
        token = create_jwt_token({"sub": "testuser", "extra": "data"})
        payload = verify_jwt_token(token)
        assert payload["sub"] == "testuser"
        assert payload["extra"] == "data"

    def test_token_with_max_expiry(self):
        # Test with maximum possible expiry (near datetime max)
        max_expiry = datetime(9999, 12, 31, 23, 59, 59, tzinfo=UTC)
        payload = {
            "sub": "testuser",
            "exp": max_expiry
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        decoded = verify_jwt_token(token)
        assert decoded["sub"] == "testuser"

    def test_token_with_special_chars_in_subject(self):
        special_sub = "user@domain.com"
        token = create_jwt_token({"sub": special_sub})
        decoded = verify_jwt_token(token)
        assert decoded["sub"] == special_sub
