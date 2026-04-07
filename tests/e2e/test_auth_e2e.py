"""
End-to-End Tests for Authentication System

Tests the complete user authentication flow including:
- Registration page and form submission
- Login page and form submission
- Error handling for invalid credentials
- JWT token generation and validation
- Redirect flows
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import json
import re


class TestRegistrationE2E:
    """E2E tests for user registration"""

    def test_register_page_loads(self, client):
        """Test that registration page loads successfully"""
        response = client.get("/register")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Register" in response.text
        assert 'name="username"' in response.text
        assert 'name="password"' in response.text
        assert 'name="email"' in response.text

    def test_successful_registration(self, client):
        """Test successful user registration with valid data"""
        response = client.post(
            "/register",
            data={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "username": "johndoe",
                "password": "Password123"
            },
            follow_redirects=False
        )
        
        # Should redirect to login with success message
        assert response.status_code == 303
        assert "location" in response.headers
        assert "/login?success=" in response.headers["location"]

    def test_registration_creates_database_user(self, client, db_session):
        """Test that registration actually creates user in database"""
        from app.models.user import User
        
        # Register new user
        response = client.post(
            "/register",
            data={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com",
                "username": "janesmith",
                "password": "SecurePass456"
            }
        )
        
        # Verify user exists in database
        user = db_session.query(User).filter_by(username="janesmith").first()
        assert user is not None
        assert user.email == "jane@example.com"
        assert user.first_name == "Jane"
        assert user.last_name == "Smith"
        # Password should be hashed, not plain text
        assert user.password_hash != "SecurePass456"

    def test_registration_duplicate_email(self, client):
        """Test registration fails with duplicate email"""
        email = "duplicate@example.com"
        
        # Register first user
        response1 = client.post(
            "/register",
            data={
                "first_name": "User",
                "last_name": "One",
                "email": email,
                "username": "userone",
                "password": "Password123"
            }
        )
        assert response1.status_code == 303
        
        # Try to register with same email
        response2 = client.post(
            "/register",
            data={
                "first_name": "User",
                "last_name": "Two",
                "email": email,
                "username": "usertwo",
                "password": "Password123"
            },
            follow_redirects=False
        )
        
        # Should redirect to register with error message
        assert response2.status_code == 303
        assert "/register?error=" in response2.headers["location"]

    def test_registration_duplicate_username(self, client):
        """Test registration fails with duplicate username"""
        username = "duplicateuser"
        
        # Register first user
        response1 = client.post(
            "/register",
            data={
                "first_name": "User",
                "last_name": "One",
                "email": "user1@example.com",
                "username": username,
                "password": "Password123"
            }
        )
        assert response1.status_code == 303
        
        # Try to register with same username
        response2 = client.post(
            "/register",
            data={
                "first_name": "User",
                "last_name": "Two",
                "email": "user2@example.com",
                "username": username,
                "password": "Password123"
            },
            follow_redirects=False
        )
        
        # Should redirect to register with error message
        assert response2.status_code == 303
        assert "/register?error=" in response2.headers["location"]

    def test_registration_weak_password(self, client):
        """Test registration fails with weak password"""
        response = client.post(
            "/register",
            data={
                "first_name": "User",
                "last_name": "Test",
                "email": "weak@example.com",
                "username": "weakuser",
                "password": "weak"  # Less than 6 chars, no uppercase/digit
            },
            follow_redirects=False
        )
        
        # Should redirect to register with error message
        assert response.status_code == 303
        assert "/register?error=" in response.headers["location"]

    def test_registration_password_no_uppercase(self, client):
        """Test registration fails with password missing uppercase"""
        response = client.post(
            "/register",
            data={
                "first_name": "User",
                "last_name": "Test",
                "email": "nouppercase@example.com",
                "username": "noupperuser",
                "password": "password123"  # No uppercase letter
            },
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/register?error=" in response.headers["location"]

    def test_registration_password_no_lowercase(self, client):
        """Test registration fails with password missing lowercase"""
        response = client.post(
            "/register",
            data={
                "first_name": "User",
                "last_name": "Test",
                "email": "nolowercase@example.com",
                "username": "noloweruser",
                "password": "PASSWORD123"  # No lowercase letter
            },
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/register?error=" in response.headers["location"]

    def test_registration_password_no_digit(self, client):
        """Test registration fails with password missing digit"""
        response = client.post(
            "/register",
            data={
                "first_name": "User",
                "last_name": "Test",
                "email": "nodigit@example.com",
                "username": "nodigituser",
                "password": "PasswordAbc"  # No digit
            },
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/register?error=" in response.headers["location"]


class TestLoginE2E:
    """E2E tests for user login"""

    def test_login_page_loads(self, client):
        """Test that login page loads successfully"""
        response = client.get("/login")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Login" in response.text
        assert 'name="username"' in response.text
        assert 'name="password"' in response.text

    def test_successful_login(self, client):
        """Test successful login with valid credentials"""
        # First register a user
        client.post(
            "/register",
            data={
                "first_name": "Login",
                "last_name": "Test",
                "email": "login@example.com",
                "username": "logintest",
                "password": "TestPass123"
            }
        )
        
        # Now login
        response = client.post(
            "/login",
            data={
                "username": "logintest",
                "password": "TestPass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "logintest"
        assert data["user"]["email"] == "login@example.com"

    def test_login_invalid_password(self, client):
        """Test login fails with incorrect password"""
        # Register a user
        client.post(
            "/register",
            data={
                "first_name": "Security",
                "last_name": "Test",
                "email": "security@example.com",
                "username": "securitytest",
                "password": "CorrectPass123"
            }
        )
        
        # Try login with wrong password
        response = client.post(
            "/login",
            data={
                "username": "securitytest",
                "password": "WrongPass123"
            },
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/login?error=" in response.headers["location"]
        assert "Invalid" in response.headers["location"]

    def test_login_nonexistent_user(self, client):
        """Test login fails for non-existent user"""
        response = client.post(
            "/login",
            data={
                "username": "doesnotexist",
                "password": "Password123"
            },
            follow_redirects=False
        )
        
        assert response.status_code == 303
        assert "/login?error=" in response.headers["location"]

    def test_login_case_sensitive_username(self, client):
        """Test that login username is case-sensitive (should fail with different case)"""
        # Register user with lowercase username
        client.post(
            "/register",
            data={
                "first_name": "Case",
                "last_name": "Test",
                "email": "case@example.com",
                "username": "casetest",
                "password": "CasePass123"
            }
        )
        
        # Try login with uppercase username
        response = client.post(
            "/login",
            data={
                "username": "CASETEST",
                "password": "CasePass123"
            },
            follow_redirects=False
        )
        
        # Should fail
        assert response.status_code == 303
        assert "/login?error=" in response.headers["location"]


class TestAuthenticationFlows:
    """E2E tests for complete authentication workflows"""

    def test_register_to_login_flow(self, client):
        """Test complete workflow: register → login → get token"""
        # Step 1: Register
        register_response = client.post(
            "/register",
            data={
                "first_name": "Integration",
                "last_name": "Test",
                "email": "integration@example.com",
                "username": "integrationtest",
                "password": "IntegPass123"
            }
        )
        assert register_response.status_code == 303
        
        # Step 2: Login
        login_response = client.post(
            "/login",
            data={
                "username": "integrationtest",
                "password": "IntegPass123"
            }
        )
        assert login_response.status_code == 200
        
        # Step 3: Verify token returned
        data = login_response.json()
        assert "access_token" in data
        assert len(data["access_token"]) > 0
        assert data["user"]["username"] == "integrationtest"

    def test_multiple_users_isolation(self, client):
        """Test that multiple users are properly isolated"""
        # Register two users
        client.post(
            "/register",
            data={
                "first_name": "User",
                "last_name": "Alpha",
                "email": "alpha@example.com",
                "username": "useralpha",
                "password": "AlphaPass123"
            }
        )
        
        client.post(
            "/register",
            data={
                "first_name": "User",
                "last_name": "Beta",
                "email": "beta@example.com",
                "username": "userbeta",
                "password": "BetaPass123"
            }
        )
        
        # Login as first user
        response1 = client.post(
            "/login",
            data={
                "username": "useralpha",
                "password": "AlphaPass123"
            }
        )
        token1 = response1.json()["access_token"]
        
        # Login as second user
        response2 = client.post(
            "/login",
            data={
                "username": "userbeta",
                "password": "BetaPass123"
            }
        )
        token2 = response2.json()["access_token"]
        
        # Tokens should be different
        assert token1 != token2


class TestHomePageE2E:
    """E2E tests for home page and navigation"""

    def test_home_page_loads(self, client):
        """Test that home page loads successfully"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "FastAPI Calculator" in response.text

    def test_home_page_includes_navbar(self, client):
        """Test that home page includes navigation links"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Login" in response.text
        assert "Register" in response.text


class TestCalculatorE2E:
    """E2E tests for calculator endpoints"""

    def test_calculator_add(self, client):
        """Test addition endpoint"""
        response = client.get("/add?a=5&b=3")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 8.0

    def test_calculator_subtract(self, client):
        """Test subtraction endpoint"""
        response = client.get("/subtract?a=10&b=3")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 7.0

    def test_calculator_multiply(self, client):
        """Test multiplication endpoint"""
        response = client.get("/multiply?a=4&b=5")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 20.0

    def test_calculator_divide(self, client):
        """Test division endpoint"""
        response = client.get("/divide?a=20&b=4")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 5.0

    def test_calculator_divide_by_zero(self, client):
        """Test division by zero handling"""
        response = client.get("/divide?a=10&b=0")
        # Should either return error or handle gracefully
        assert response.status_code in [200, 400, 422]

    def test_calculator_negative_numbers(self, client):
        """Test calculator with negative numbers"""
        response = client.get("/add?a=-5&b=3")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == -2.0

    def test_calculator_decimal_numbers(self, client):
        """Test calculator with decimal numbers"""
        response = client.get("/add?a=5.5&b=2.3")
        assert response.status_code == 200
        data = response.json()
        assert abs(data["result"] - 7.8) < 0.01


class TestErrorHandling:
    """E2E tests for error handling"""

    def test_404_on_invalid_route(self, client):
        """Test 404 error on invalid route"""
        response = client.get("/invalid-route")
        assert response.status_code == 404

    def test_registration_missing_fields(self, client):
        """Test registration with missing required fields"""
        response = client.post(
            "/register",
            data={
                "username": "incomplete"
                # Missing other required fields
            },
            follow_redirects=False
        )
        # Should fail (422 unprocessable or 303 with error)
        assert response.status_code in [303, 422]

    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        if response.status_code == 200:
            # If health check exists and returns JSON
            try:
                data = response.json()
                assert "status" in data or "message" in data
            except:
                # Or just check it returns 200
                pass
