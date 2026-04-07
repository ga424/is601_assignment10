from app.auth.security import hash_password, verify_password


def test_hash_password_generates_different_value():
    plain = "SecurePass123"
    hashed = hash_password(plain)
    assert hashed != plain


def test_verify_password_matches_hash():
    plain = "SecurePass123"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True


def test_verify_password_rejects_invalid_password():
    hashed = hash_password("SecurePass123")
    assert verify_password("WrongPass123", hashed) is False
