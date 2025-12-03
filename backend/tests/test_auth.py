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
        role="admin"
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

        res = client.post("/api/auth/register", json=payload)
        json = res.get_json()

        assert res.status_code == 201
        assert json["code"] == 201
        assert json["status"] == "success"
        assert json["data"]["username"] == "newuser"
        assert json["data"]["name"] == "New User"
        assert json["data"]["role"] == "guest"

    @pytest.mark.case("TC002")
    def test_register_missing_fields(self, client):
        """
        Test Case: TC002
        
        Description: Verify users not able to register without giving mandatory data.
        i.e. name, username, and password.
        """
        # No data
        res = client.post("/api/auth/register", json={})
        json = res.get_json()

        assert res.status_code == 400
        assert json["code"] == 400
        assert "Missing mandatory fields" in json["errors"]
        assert json["status"] == "fail"

        # Only username
        res = client.post("/api/auth/register", json={"username":"testuser"})
        json = res.get_json()

        assert res.status_code == 400
        assert json["code"] == 400
        assert "Missing mandatory fields" in json["errors"]
        assert json["status"] == "fail"

        # Username and password
        res = client.post("/api/auth/register", json={"username":"testuser","password":"New@Pass123"})
        json = res.get_json()

        assert res.status_code == 400
        assert json["code"] == 400
        assert "Missing mandatory fields" in json["errors"]
        assert json["status"] == "fail"

    @pytest.mark.case("TC003")
    def test_duplicate_username(self, client, create_user):
        """
        Test Case: TC003

        Description: Verify users not able to register without giving unique username.
        """
        payload = {
            "username": "testuser",
            "password": "TestPass123@",
            "name": "Another"
        }

        res = client.post("/api/auth/register", json=payload)
        json = res.get_json()

        assert res.status_code == 409
        assert json["code"] == 409
        assert "Username already exists" in json["errors"]
        assert json["status"] == "fail"

@pytest.mark.AUTH
@pytest.mark.scenario("TS003")
class TestTS003:
    """
    Module: AUTH	

    Test Scenario: TS003
    
    Description: Users able to login themselves with valid data.
    """

    @pytest.mark.case("TC001")
    def test_login_success(self, client, create_user):
        """
        Test Case: TC001

        Description: Verify users able to login themselves with valid username and password.
        """
        payload = {"username": "testuser", "password": "TestPass123@"}
        res = client.post("/api/auth/login", json=payload)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert "login successful" in json["message"].lower()
        assert "access_token" in json["data"]
        assert "refresh_token" in json["data"]

        # Registering new user
        payload = {
            "username": "newuser",
            "password": "NewPass123@",
            "name": "New User"
        }
        res = client.post("/api/auth/register", json=payload)

        res = client.post("/api/auth/login", json={"username": "newuser","password": "NewPass123@"})
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert "login successful" in json["message"].lower()
        assert "access_token" in json["data"]
        assert "refresh_token" in json["data"]
 
    @pytest.mark.case("TC002")
    def test_login_wrong_data(self, client, create_user):
        """
        Test Case: TC002

        Description: Verify users not able to login themselves with invalid username and password.
        """
        # Wrong password
        payload = {"username": "testuser", "password": "Wrong123@"}
        res = client.post("/api/auth/login", json=payload)
        json = res.get_json()

        assert res.status_code == 400
        assert json["code"] == 400
        assert json["status"] == "fail"
        assert "not able to login" in json["message"].lower()
        assert "invalid username/password" in json["errors"].lower()

        # Wrong username
        payload = {"username": "testuser1", "password": "Wrong123@"}
        res = client.post("/api/auth/login", json=payload)
        json = res.get_json()

        assert res.status_code == 400
        assert json["code"] == 400
        assert json["status"] == "fail"
        assert "not able to login" in json["message"].lower()
        assert "invalid username/password" in json["errors"].lower()

    @pytest.mark.case("TC003")
    def test_login_missing_fields(self, client):
        """
        Test Case: TC003

        Description: Verify users not able to login themselves without username and password.
        """
        # without password
        payload = {"username": "testuser"}
        res = client.post("/api/auth/login", json=payload)
        json = res.get_json()

        assert res.status_code == 400
        assert json["code"] == 400
        assert json["status"] == "fail"
        assert "not able to login" in json["message"].lower()
        assert "missing username/password" in json["errors"].lower()

        # Without username
        payload = {"password": "TestPass123@"}
        res = client.post("/api/auth/login", json=payload)
        json = res.get_json()

        assert res.status_code == 400
        assert json["code"] == 400
        assert json["status"] == "fail"
        assert "not able to login" in json["message"].lower()
        assert "missing username/password" in json["errors"].lower()

@pytest.mark.AUTH
@pytest.mark.scenario("TS004")
class TestTS004:
    """
    Module: AUTH	

    Test Scenario: TS004
    
    Description: Users able to refresh access token with valid refresh token.
    """

    @pytest.mark.case("TC001")
    def test_refresh_token_valid(self, client, create_user):
        """
        Test Case: TC001

        Description: Verify users able to refresh access token with valid token.
        """
        # login to get refresh token
        payload = {"username": "testuser", "password": "TestPass123@"}
        res = client.post("/api/auth/login", json=payload)
        json = res.get_json()
        
        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert "access_token" in json["data"]
        assert "refresh_token" in json["data"]

        refresh = json["data"]["refresh_token"]
        
        headers = {"Authorization": f"Bearer {refresh}"}
        res = client.post("/api/auth/refresh", headers=headers)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert "access_token" in json["data"]
        assert "token refreshed successfully" in json["message"].lower()

    @pytest.mark.case("TC002")
    def test_refresh_invalid_token(self, client):
        """
        Test Case: TC002

        Description: Verify users not able to refresh access token with invalid token or missing token.
        """
        # invalid token
        headers = {"Authorization": f"Bearer invalid token"}
        res = client.post("/api/auth/refresh", headers=headers)
        json = res.get_json()

        assert res.status_code == 422
        assert "bad authorization header" in json["msg"].lower()
        
        # without token
        res = client.post("/api/auth/refresh")
        assert res.status_code == 401  # JWT missing


@pytest.mark.AUTH
@pytest.mark.scenario("TS005")
class TestTS005:
    """
    Module: AUTH	

    Test Scenario: TS005
    
    Description: Users able to successfully logout.
    """

    @pytest.mark.case("TC001")
    def test_logout_success(self, client, create_user):
        """
        Test Case: TC001

        Description: Verify users able to logout successfully with valid data.
        """
        from extensions import blacklist
        # Login
        login = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "TestPass123@"
        }).get_json()

        access = login["data"]["access_token"]
        refresh = login["data"]["refresh_token"]

        headers = {"Authorization": f"Bearer {access}"}
        res = client.post("/api/auth/logout",
                          json={"refresh_token": refresh},
                          headers=headers)

        json = res.get_json()
        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert "logout successfully" in json["message"].lower()

        # both tokens should be blacklisted
        access_jti = decode_token(access)["jti"]
        refresh_jti = decode_token(refresh)["jti"]

        assert access_jti in blacklist
        assert refresh_jti in blacklist

    @pytest.mark.case("TC002")
    def test_logout_blacklisted_token(self, client, create_user):
        """
        Test Case: TC002

        Description: Verify logged out users access token and refresh
        token is blacklisted and can not be used again.
        """
        from extensions import blacklist
        # Login
        login = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "TestPass123@"
        }).get_json()

        access = login["data"]["access_token"]
        refresh = login["data"]["refresh_token"]

        headers = {"Authorization": f"Bearer {access}"}
        res = client.post("/api/auth/logout",
                          json={"refresh_token": refresh},
                          headers=headers)
        
        # both tokens should be blacklisted
        access_jti = decode_token(access)["jti"]
        refresh_jti = decode_token(refresh)["jti"]
        
        assert access_jti in blacklist
        assert refresh_jti in blacklist

        headers = {"Authorization": f"Bearer {refresh}"}
        res = client.post("/api/auth/refresh", headers=headers)
        assert res.status_code == 401
        assert "token has been revoked" in res.get_json()["msg"].lower()

        headers = {"Authorization": f"Bearer {access}"}
        res = client.post("/api/auth/logout", headers=headers)
        assert res.status_code == 401
        assert "token has been revoked" in res.get_json()["msg"].lower()

    @pytest.mark.case("TC003")
    def test_logout_missing_token(self, client, create_user):
        """
        Test Case: TC003

        Description: Verify users not able to logout successfully without refresh token .
        """
        login = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "TestPass123@"
        }).get_json()

        access = login["data"]["access_token"]
        refresh = login["data"]["refresh_token"]

        # sending wrong headers
        headers = {"Authorization": f"Bearer {refresh}"}
        res = client.post("/api/auth/logout",
                          json={"refresh_token": access},
                          headers=headers)

        json = res.get_json()
        assert res.status_code == 422

        # sending access token in place of refresh token
        headers = {"Authorization": f"Bearer {access}"}
        res = client.post("/api/auth/logout",
                          json={"refresh_token": access},
                          headers=headers)

        json = res.get_json()
        assert res.status_code == 400
        assert json["code"] == 400
        assert json["status"] == "fail"
        assert "invalid refresh token" in json["errors"].lower()

        # not sending refresh token
        headers = {"Authorization": f"Bearer {access}"}
        res = client.post("/api/auth/logout",
                          json={"refresh_token": ""},
                          headers=headers)

        json = res.get_json()
        assert res.status_code == 400
        assert json["code"] == 400
        assert json["status"] == "fail"
        assert "refresh token is required" in json["errors"].lower()

        # not sending refresh token
        headers = {"Authorization": f"Bearer {access}"}
        res = client.post("/api/auth/logout", 
                          json={},
                          headers=headers)

        json = res.get_json()
        assert res.status_code == 400
        assert json["code"] == 400
        assert json["status"] == "fail"
        assert "refresh token is required" in json["errors"].lower()
        
        
        
