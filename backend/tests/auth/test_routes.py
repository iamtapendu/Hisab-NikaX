import pytest
import os

# ---------------- TEST SUITES ---------------- #


@pytest.mark.AUTH
@pytest.mark.scenario("TS001")
class TestTS001:
    """
    Module: AUTH

    Test Scenario: TS001

    Description: model, routes, service and schema file should be available at /backend/modules/auth/
    """

    @pytest.mark.case("TC001")
    def test_if_model_exists(self):
        """
        Test Case: TC001

        Description: Verify model exists at backend/modules/auth/ location
        """
        assert os.path.exists("backend/modules/auth/model.py")

    @pytest.mark.case("TC002")
    def test_if_routes_exists(self):
        """
        Test Case: TC002

        Description: Verify route.py exists at backend/modules/auth/ location
        """
        assert os.path.exists("backend/modules/auth/routes.py")

    @pytest.mark.case("TC003")
    def test_if_schema_exists(self):
        """
        Test Case: TC003

        Description: Verify schema.py exists at backend/modules/auth/ location
        """
        assert os.path.exists("backend/modules/auth/schema.py")

    @pytest.mark.case("TC004")
    def test_if_service_exists(self):
        """
        Test Case: TC004

        Description: Verify schema.py exists at backend/modules/auth/ location
        """
        assert os.path.exists("backend/modules/auth/service.py")


@pytest.mark.AUTH
@pytest.mark.scenario("TS002")
class TestTS002:
    """
    Module: AUTH

    Test Scenario: TS002

    Description: Users able to login themselves with valid data.
    """

    @pytest.mark.case("TC001")
    def test_login_success(self, client, test_user):
        """
        Test Case: TC001

        Description: Verify users able to login themselves with valid username and password.
        """
        payload = {
            "username": test_user.username,
            "password": "Password@123",
            "grant_type": "password",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = client.post("/api/v1/auth/login", data=payload, headers=headers)
        body = res.json()

        assert res.status_code == 200
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

    @pytest.mark.case("TC002")
    def test_login_wrong_data(self, client, test_user):
        """
        Test Case: TC002

        Description: Verify users not able to login themselves with invalid username and password.
        """
        # Wrong password
        payload = {
            "username": test_user.username,
            "password": "Wrong@123",
            "grant_type": "password",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = client.post("/api/v1/auth/login", data=payload, headers=headers)
        body = res.json()

        assert res.status_code == 401
        assert "not able to login" in body["msg"].lower()
        assert "invalid username or password" in body["errors"].lower()

        # Wrong username
        payload = {"username": "hellouser", "password": "Wrong@123", "grant_type": "password"}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = client.post("/api/v1/auth/login", data=payload, headers=headers)
        body = res.json()

        assert res.status_code == 401
        assert "not able to login" in body["msg"].lower()
        assert "invalid username or password" in body["errors"].lower()

    @pytest.mark.case("TC003")
    def test_login_missing_fields(self, client, test_user):
        """
        Test Case: TC003

        Description: Verify users not able to login themselves without username and password.
        """

        payload = {
            "username": test_user.username,
            "password": "Password@123",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = client.post("/api/v1/auth/login", data=payload, headers=headers)

        assert res.status_code == 422

        payload = {"password": "TestPass123@"}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = client.post("/api/v1/auth/login", data=payload, headers=headers)

        assert res.status_code == 422

        payload = {"username": "admin"}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = client.post("/api/v1/auth/login", data=payload, headers=headers)

        assert res.status_code == 422

        payload = {
            "username": test_user.username,
            "password": "Password@123",
            "grant_type": "password",
        }
        res = client.post("/api/v1/auth/login", json=payload)

        assert res.status_code == 422


@pytest.mark.AUTH
@pytest.mark.scenario("TS003")
class TestTS003:
    """
    Module: AUTH

    Test Scenario: TS003

    Description: Users able to refresh access token with valid refresh token.
    """

    @pytest.mark.case("TC001")
    def test_refresh_token_valid(self, client, test_user):
        """
        Test Case: TC001

        Description: Verify users able to refresh access token with valid token.
        """
        # login to get refresh token
        payload = {
            "username": test_user.username,
            "password": "Password@123",
            "grant_type": "password",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = client.post("/api/v1/auth/login", data=payload, headers=headers)
        body = res.json()

        assert res.status_code == 200
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

        refresh = body["refresh_token"]

        headers = {"Authorization": f"Bearer {refresh}"}
        res = client.post("/api/v1/auth/refresh", headers=headers)
        body = res.json()

        assert res.status_code == 200
        assert "access_token" in body
        assert "refresh_token" in body
        assert refresh != body["refresh_token"]

    @pytest.mark.case("TC002")
    def test_refresh_invalid_token(self, client):
        """
        Test Case: TC002

        Description: Verify users not able to refresh access token with invalid token
        """
        # invalid token
        headers = {"Authorization": f"Bearer invalid.token"}
        res = client.post("/api/v1/auth/refresh", headers=headers)
        body = res.json()

        assert res.status_code == 401
        assert "token invalid" in body["msg"].lower()

    @pytest.mark.case("TC003")
    def test_refresh_missing_token(self, client):
        """
        Test Case: TC003

        Description: Verify users not able to refresh access token with missing token
        """
        # missing token
        res = client.post("/api/v1/auth/refresh")
        body = res.json()

        assert res.status_code == 401
        assert "not authenticated" in body["msg"].lower()

    @pytest.mark.case("TC004")
    def test_refresh_using_access_token(self, client, test_user):
        """
        Test Case: TC004

        Description: Verify users not able to refresh access token with access token.
        """
        payload = {
            "username": test_user.username,
            "password": "Password@123",
            "grant_type": "password",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = client.post("/api/v1/auth/login", data=payload, headers=headers)
        body = res.json()

        assert res.status_code == 200
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

        access = body["access_token"]
        headers = {"Authorization": f"Bearer {access}"}

        res = client.post("/api/v1/auth/refresh", headers=headers)
        body = res.json()
        assert res.status_code == 401
        assert "invalid token type" in body["msg"].lower()
        assert "received access" in body["errors"].lower()


@pytest.mark.AUTH
@pytest.mark.scenario("TS004")
class TestTS004:
    """
    Module: AUTH

    Test Scenario: TS004

    Description: Users able to successfully logout.
    """

    @pytest.mark.case("TC001")
    def test_logout_success(self, client, test_user):
        """
        Test Case: TC001

        Description: Verify users able to logout successfully with valid data.
        """

        # Login
        payload = {
            "username": test_user.username,
            "password": "Password@123",
            "grant_type": "password",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = client.post("/api/v1/auth/login", data=payload, headers=headers)
        body = res.json()

        assert res.status_code == 200
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

        refresh = body["refresh_token"]
        headers = {"Authorization": f"Bearer {refresh}"}
        res = client.post("/api/v1/auth/logout", headers=headers)

        assert res.status_code == 204

    @pytest.mark.case("TC002")
    def test_logout_revoke_token(self, client, test_user):
        """
        Test Case: TC002

        Description: Verify logged out user refresh
        token is blacklisted and can not be used again.
        """

        # Login
        payload = {
            "username": test_user.username,
            "password": "Password@123",
            "grant_type": "password",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = client.post("/api/v1/auth/login", data=payload, headers=headers)
        body = res.json()

        assert res.status_code == 200
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

        refresh = body["refresh_token"]
        headers = {"Authorization": f"Bearer {refresh}"}
        res = client.post("/api/v1/auth/logout", headers=headers)

        assert res.status_code == 204

        res = client.post("/api/v1/auth/refresh", headers=headers)
        assert res.status_code == 401
        assert "token has been revoked" in res.json()["errors"].lower()

    @pytest.mark.case("TC003")
    def test_logout_missing_token(self, client, test_user):
        """
        Test Case: TC003

        Description: Verify users not able to logout successfully without refresh token .
        """
        payload = {
            "username": test_user.username,
            "password": "Password@123",
            "grant_type": "password",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = client.post("/api/v1/auth/login", data=payload, headers=headers)
        body = res.json()

        assert res.status_code == 200
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

        headers = {"Authorization": f"Bearer "}
        res = client.post("/api/v1/auth/logout", headers=headers)
        body = res.json()

        assert res.status_code == 401
        assert "token invalid" in body["msg"].lower()

    @pytest.mark.case("TC004")
    def test_logout_access_token(self, client, test_user):
        """
        Test Case: TC004

        Description: Verify users not able to logout with access token.
        """
        payload = {
            "username": test_user.username,
            "password": "Password@123",
            "grant_type": "password",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        res = client.post("/api/v1/auth/login", data=payload, headers=headers)
        body = res.json()

        assert res.status_code == 200
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

        access = body["access_token"]
        headers = {"Authorization": f"Bearer {access}"}
        res = client.post("/api/v1/auth/logout", headers=headers)
        body = res.json()

        assert res.status_code == 401
        assert "invalid token type" in body["msg"].lower()
