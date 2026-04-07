# E2E Test Cases - Authentication System Documentation

## Overview
Comprehensive end-to-end test suite for the FastAPI Calculator authentication system. **28 test cases** covering registration, login, calculator operations, and error handling.

## Test Structure

### 1. **Registration Tests (9 tests)** - `TestRegistrationE2E`

| Test Name | Purpose | Expected Result |
|-----------|---------|-----------------|
| `test_register_page_loads` | Verify registration page renders | HTTP 200 with form elements |
| `test_successful_registration` | Register valid user | Redirect to login with success message |
| `test_registration_creates_database_user` | Verify user persists in DB | User created with hashed password |
| `test_registration_duplicate_email` | Reject duplicate email | Redirect to register with error |
| `test_registration_duplicate_username` | Reject duplicate username | Redirect to register with error |
| `test_registration_weak_password` | Reject password <6 chars | Redirect with error message |
| `test_registration_password_no_uppercase` | Reject password without uppercase | Redirect with error message |
| `test_registration_password_no_lowercase` | Reject password without lowercase | Redirect with error message |
| `test_registration_password_no_digit` | Reject password without digit | Redirect with error message |

**Password Requirements Tested:**
- Minimum 6 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit

### 2. **Login Tests (5 tests)** - `TestLoginE2E`

| Test Name | Purpose | Expected Result |
|-----------|---------|-----------------|
| `test_login_page_loads` | Verify login page renders | HTTP 200 with form elements |
| `test_successful_login` | Login with valid credentials | JSON response with JWT token |
| `test_login_invalid_password` | Login with wrong password | Redirect to login with error |
| `test_login_nonexistent_user` | Login for user that doesn't exist | Redirect to login with error |
| `test_login_case_sensitive_username` | Username case-sensitivity check | Failed login (case matters) |

**Valid Login Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "is_active": true,
    "is_verified": false,
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

### 3. **Authentication Flows (2 tests)** - `TestAuthenticationFlows`

| Test Name | Purpose | Expected Result |
|-----------|---------|-----------------|
| `test_register_to_login_flow` | Complete register→login workflow | User created and token received |
| `test_multiple_users_isolation` | Verify user data isolation | Different tokens for different users |

### 4. **Home Page Tests (2 tests)** - `TestHomePageE2E`

| Test Name | Purpose | Expected Result |
|-----------|---------|-----------------|
| `test_home_page_loads` | Verify home page renders | HTTP 200 with title |
| `test_home_page_includes_navbar` | Verify navigation links present | Login/Register links visible |

### 5. **Calculator Tests (7 tests)** - `TestCalculatorE2E`

| Test Name | Purpose | Expected Result |
|-----------|---------|-----------------|
| `test_calculator_add` | Test 5 + 3 | JSON: `{"result": 8.0}` |
| `test_calculator_subtract` | Test 10 - 3 | JSON: `{"result": 7.0}` |
| `test_calculator_multiply` | Test 4 × 5 | JSON: `{"result": 20.0}` |
| `test_calculator_divide` | Test 20 ÷ 4 | JSON: `{"result": 5.0}` |
| `test_calculator_divide_by_zero` | Test error handling | HTTP 200, 400, or 422 |
| `test_calculator_negative_numbers` | Test -5 + 3 | JSON: `{"result": -2.0}` |
| `test_calculator_decimal_numbers` | Test 5.5 + 2.3 | JSON: `{"result": 7.8}` |

### 6. **Error Handling Tests (3 tests)** - `TestErrorHandling`

| Test Name | Purpose | Expected Result |
|-----------|---------|-----------------|
| `test_404_on_invalid_route` | Test non-existent endpoint | HTTP 404 |
| `test_registration_missing_fields` | Submit incomplete form | HTTP 303 or 422 |
| `test_health_check_endpoint` | Verify health check exists | HTTP 200 (if implemented) |

## Running the Tests

### Run all e2e tests:
```bash
docker compose exec -T web pytest tests/e2e/test_auth_e2e.py -v
```

### Run specific test class:
```bash
docker compose exec -T web pytest tests/e2e/test_auth_e2e.py::TestRegistrationE2E -v
```

### Run specific test:
```bash
docker compose exec -T web pytest tests/e2e/test_auth_e2e.py::TestLoginE2E::test_successful_login -v
```

### Run with coverage:
```bash
docker compose exec -T web pytest tests/e2e/test_auth_e2e.py --cov=app --cov-report=html
```

### Run all tests (unit, integration, e2e):
```bash
docker compose exec -T web pytest -v
```

## Test Results Summary

**✅ All 28 E2E Tests Passing**

```
============================== 28 passed in 1.82s ==============================
```

### Coverage by Test Type:
- **Registration**: 9 tests (form, validation, database, error cases)
- **Login**: 5 tests (success, failure, edge cases)
- **Complete Flows**: 2 tests (integration scenarios)
- **Home Page**: 2 tests (UI/navigation)
- **Calculator**: 7 tests (all operations, edge cases)
- **Error Handling**: 3 tests (HTTP errors, validation)

## Key Testing Notes

1. **Database Isolation**: Each test uses a fresh transaction that's rolled back after the test
2. **TestClient**: Uses FastAPI's TestClient for HTTP-level testing with dependency overrides
3. **Fixtures**: E2E tests use the main conftest.py fixtures (db_session, etc.)
4. **Error Messages**: Tests verify redirects with error query parameters (e.g., `/register?error=...`)
5. **Password Hashing**: Verified that passwords are properly hashed, never stored as plain text

## Debugging Failed Tests

If a test fails while running e2e suite but passes individually:
- This usually indicates database state issues
- Run with `--tb=short` for detailed traceback
- Use `--preserve-db` flag to inspect database after failed test

```bash
docker compose exec -T web pytest tests/e2e/test_auth_e2e.py -v --tb=short --preserve-db
```

## Test Files Location
- **Main test file**: [tests/e2e/test_auth_e2e.py](../tests/e2e/test_auth_e2e.py)
- **Fixtures**: [tests/e2e/conftest.py](../tests/e2e/conftest.py)
- **Base fixtures**: [tests/conftest.py](../tests/conftest.py)

## Known Issues / Considerations

1. **Test Order**: Some tests are sensitive to execution order due to database state. Run full suite, not random order.
2. **Redirect Behavior**: TestClient automatically follows redirects. Tests expect final page content, not redirect headers.
3. **JWT Tokens**: Each login generates unique token with 1-hour expiration (UNIX timestamp in token).
4. **Case Sensitivity**: Username queries are case-sensitive in PostgreSQL.

## Future Test Enhancements

Potential additions:
- Protected endpoint tests (verify JWT token validation)
- Token refresh/expiration tests
- CSRF protection tests
- Rate limiting tests
- Concurrent user registration tests
- Password reset flow tests
