import os
import pytest
from flask_jwt_extended import decode_token

# ---------------- FIXTURES ---------------- #

@pytest.fixture
def create_user(db_session):
    """Creates and returns a sample user for login/auth tests."""
    from users.model import User

    user = User(
        username="testuser",
        name="Test User",
        email="test@example.com",
        phone="9999999999",
        role="user"
    )
    user.set_password("TestPass123@")

    db_session.session.add(user)
    db_session.session.commit()
    return user


# ---------------- TEST SUITES ---------------- #

@pytest.mark.AUTH
@pytest.mark.scenario("TS001")
class TestTS001:
    """
    Module: AUTH	

    Test Scenario: TS001
    
    Description: __init__.py and route.py file should be available at /backend/auth/
    """
    
    @pytest.mark.case("TC001")
    def test_if_init_exists(self):
        """
        Test Case: TC001

        Description: Verify __init__.py exists at /backend/auth/ location
        """
        assert os.path.exists("backend/auth/__init__.py")

    @pytest.mark.case("TC002")
    def test_if_routes_exists(self):
        """
        Test Case: TC002

        Description: Verify route.py exists at /backend/auth/ location
        """
        assert os.path.exists("backend/auth/routes.py")
        
@pytest.mark.AUTH
@pytest.mark.scenario("TS002")
class TestTS002:
    """
    Module: AUTH

    Test Scenario: TS002

    Description: Users able to register themselves with valid data
    """
    @pytest.mark.case("TC001")
    def test_register_success(self, client):
        """
        Test Case: TC002

        Description: Verify users able to register themselves with valid data. 
        i.e. name, username and password.
        """
        payload = {
            "username": "newuser",
            "password": "NewPass123@",
            "name": "New User"
        }

        res = client.post("api/auth/register", json=payload)
        json = res.get_json()

        assert res.status_code == 201
        assert json["success"] is True
        assert json["data"]["username"] == "newuser"
        assert json["data"]["name"] == "New User"
        assert json["data"]["role"] == "guest"

#     @pytest.mark.fail
#     def test_register_missing_fields(self, client):
#         res = client.post("/auth/register", json={})
#         json = res.get_json()

#         assert res.status_code == 400
#         assert "Missing mandatory fields" in json["errors"]

#     @pytest.mark.fail
#     def test_register_duplicate_username(self, client, create_user):
#         payload = {
#             "username": "testuser",
#             "password": "TestPass123@",
#             "name": "Another"
#         }

#         res = client.post("/auth/register", json=payload)
#         json = res.get_json()

#         assert res.status_code == 409
#         assert "Username already exists" in json["errors"]


# @pytest.mark.auth
# class TestLogin:
#     """Test login functionality"""

#     @pytest.mark.success
#     def test_login_success(self, client, create_user):
#         payload = {"username": "testuser", "password": "TestPass123@"}
#         res = client.post("/auth/login", json=payload)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert "access_token" in json["data"]
#         assert "refresh_token" in json["data"]

#     @pytest.mark.fail
#     def test_login_wrong_password(self, client, create_user):
#         payload = {"username": "testuser", "password": "Wrong123@"}
#         res = client.post("/auth/login", json=payload)
#         json = res.get_json()

#         assert res.status_code == 400
#         assert "Invalid username/password" in json["errors"]

#     @pytest.mark.fail
#     def test_login_missing_fields(self, client):
#         res = client.post("/auth/login", json={"username": ""})
#         json = res.get_json()

#         assert res.status_code == 400
#         assert "Missing username/password" in json["errors"]


# @pytest.mark.auth
# class TestRefreshToken:
#     """Test JWT refresh token"""

#     @pytest.mark.success
#     def test_refresh_success(self, client, create_user):
#         # login to get refresh token
#         login = client.post("/auth/login", json={
#             "username": "testuser",
#             "password": "TestPass123@"
#         }).get_json()

#         refresh = login["data"]["refresh_token"]

#         headers = {"Authorization": f"Bearer {refresh}"}
#         res = client.post("/auth/refresh", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert "access_token" in json["data"]

#     @pytest.mark.fail
#     def test_refresh_without_token(self, client):
#         res = client.post("/auth/refresh")
#         assert res.status_code == 401  # JWT missing


# @pytest.mark.auth
# class TestLogout:
#     """Test access + refresh token logout"""

#     @pytest.mark.success
#     def test_logout_success(self, client, create_user, blacklist):
#         # Login
#         login = client.post("/auth/login", json={
#             "username": "testuser",
#             "password": "TestPass123@"
#         }).get_json()

#         access = login["data"]["access_token"]
#         refresh = login["data"]["refresh_token"]

#         headers = {"Authorization": f"Bearer {access}"}
#         res = client.post("/auth/logout",
#                           json={"refresh_token": refresh},
#                           headers=headers)

#         json = res.get_json()
#         assert res.status_code == 200
#         assert json["success"] is True

#         # both tokens should be blacklisted
#         access_jti = decode_token(access)["jti"]
#         refresh_jti = decode_token(refresh)["jti"]

#         assert access_jti in blacklist
#         assert refresh_jti in blacklist

#     @pytest.mark.fail
#     def test_logout_missing_refresh_token(self, client, create_user):
#         login = client.post("/auth/login", json={
#             "username": "testuser",
#             "password": "TestPass123@"
#         }).get_json()

#         access = login["data"]["access_token"]
#         headers = {"Authorization": f"Bearer {access}"}

#         res = client.post("/auth/logout", json={}, headers=headers)
#         assert res.status_code == 400


# @pytest.mark.auth
# class TestProtectedRoute:
#     """Test that protected routes respect JWT"""

#     @pytest.mark.success
#     def test_access_protected_with_token(self, client, create_user):
#         login = client.post("/auth/login", json={
#             "username": "testuser",
#             "password": "TestPass123@"
#         }).get_json()

#         token = login["data"]["access_token"]
#         headers = {"Authorization": f"Bearer {token}"}

#         res = client.get("/api/users", headers=headers)
#         assert res.status_code != 401  # Authorized

#     @pytest.mark.fail
#     def test_access_protected_without_token(self, client):
#         res = client.get("/api/users")
#         assert res.status_code == 401
