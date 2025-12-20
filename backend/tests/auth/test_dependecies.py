import pytest
import jwt
import time

from core.config import settings

# ---------------- TEST FIXTURES ---------------- #


@pytest.fixture
def login(client, test_user):
    def _get_tokens():
        res = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.username,
                "password": "Password@123",
                "grant_type": "password",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert res.status_code == 200
        body = res.json()
        return body["access_token"], body["refresh_token"]

    return _get_tokens


# ---------------- TEST SUITES ---------------- #


@pytest.mark.AUTH
@pytest.mark.scenario("DPN001")
class TestTS001:
    """
    Module: AUTH

    Test Scenario: DPN001

    Description: Auth module get_current_refresh_token working as expected
    """

    @pytest.mark.case("TC001")
    def test_get_current_refresh_token_valid(self, client, test_user, login):
        """
        Test Case: TC001

        Description: Verify get_current_refresh_token returns JWTPayload with valid data
        """
        # login to get refresh token
        _, refresh = login()

        # call test endpoint that uses ONLY the dependency
        res = client.post(
            "/_test/refresh-dep",
            headers={"Authorization": f"Bearer {refresh}"},
        )

        payload = res.json()

        assert res.status_code == 200
        assert payload["sub"] == str(test_user.id)
        assert payload["type"] == "refresh"
        assert payload["role"] == "admin"
        assert "jti" in payload
        assert "exp" in payload
        assert "iat" in payload
        assert "iss" in payload
        print(res.json())

    @pytest.mark.case("TC002")
    def test_get_current_refresh_token_rejects_access_token(self, client, test_user, login):
        """
        Test Case: TC002

        Description: Verify get_current_refresh_token raise error with access token
        """
        access, _ = login()

        res = client.post(
            "/_test/refresh-dep",
            headers={"Authorization": f"Bearer {access}"},
        )

        body = res.json()

        assert res.status_code == 401
        assert "invalid token type" in body["msg"].lower()
        assert "access" in body["errors"].lower()
        print(res.json())

    @pytest.mark.case("TC003")
    def test_missing_authorization_header(self, client):
        """
        Test Case: TC003

        Description: Verify get_current_refresh_token raise error with Missing Authorization header
        """
        res = client.post("/_test/refresh-dep")
        body = res.json()

        assert res.status_code == 401
        print(res.json())

    @pytest.mark.case("TC004")
    def test_without_bearer(self, client, login):
        """
        Test Case: TC004

        Description: Verify get_current_refresh_token raise error with Authorization header without Bearer
        """
        # login to get refresh token
        _, refresh = login()

        res = client.post(
            "/_test/refresh-dep",
            headers={"Authorization": f"Token {refresh}"},
        )
        body = res.json()

        assert res.status_code == 401
        print(res.json())

    @pytest.mark.case("TC005")
    def test_refresh_token_reused_after_logout(self, client, login):
        """
        Test Case: TC005

        Description: Verify get_current_refresh_token raise error with Refresh token reused after logout
        """
        # login to get refresh token
        _, refresh = login()

        # logout revokes refresh token
        client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {refresh}"},
        )

        # reuse revoked token
        res = client.post(
            "/_test/refresh-dep",
            headers={"Authorization": f"Bearer {refresh}"},
        )

        assert res.status_code == 401
        print(res.json())

    @pytest.mark.case("TC006")
    def test_malform_authorization_header(self, client):
        """
        Test Case: TC006

        Description: Verify get_current_refresh_token raise error with Malformed Authorization header (Bearer only)
        """

        res = client.post(
            "/_test/refresh-dep",
            headers={"Authorization": "Bearer"},
        )

        assert res.status_code == 401
        print(res.json())

    @pytest.mark.case("TC007")
    def test_invalid_jwt_format(self, client):
        """
        Test Case: TC007

        Description: Verify get_current_refresh_token raise error with Invalid JWT format
        """
        res = client.post(
            "/_test/refresh-dep",
            headers={"Authorization": "Bearer abc.def.ghi"},
        )
        body = res.json()

        assert res.status_code == 401
        assert "invalid" in body["msg"].lower()
        print(res.json())

    @pytest.mark.case("TC008")
    def test_expired_refresh_token(self, client, test_user):
        """
        Test Case: TC008

        Description: Verify get_current_refresh_token raise error with Expired refresh token
        """

        payload = {
            "sub": str(test_user.id),
            "role": test_user.role,
            "type": "refresh",
            "jti": "expired-jti",
            "iat": int(time.time()) - 1000,
            "exp": int(time.time()) - 500,
            "iss": settings.PROJECT_NAME,
        }

        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        res = client.post(
            "/_test/refresh-dep",
            headers={"Authorization": f"Bearer {token}"},
        )

        body = res.json()
        assert res.status_code == 401
        assert "expired" in body["msg"].lower()
        print(res.json())

    @pytest.mark.case("TC009")
    def test_wrong_secret(self, client, test_user):
        """
        Test Case: TC009

        Description: Verify get_current_refresh_token raise error with Token signed with wrong secret
        """
        payload = {
            "sub": str(test_user.id),
            "role": test_user.role,
            "type": "refresh",
            "jti": "wrong-secret",
            "iat": 0,
            "exp": 9999999999,
            "iss": settings.PROJECT_NAME,
        }

        token = jwt.encode(payload, "WRONG_SECRET", algorithm=settings.JWT_ALGORITHM)

        res = client.post(
            "/_test/refresh-dep",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert res.status_code == 401
        print(res.json())

    @pytest.mark.case("TC010")
    def test_wrong_issuer(self, client, test_user):
        """
        Test Case: TC010

        Description: Verify get_current_refresh_token raise error with Token with wrong issuer
        """
        payload = {
            "sub": str(test_user.id),
            "role": test_user.role,
            "type": "refresh",
            "jti": "wrong-issuer",
            "iat": 0,
            "exp": 9999999999,
            "iss": "OTHER_APP",
        }

        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        res = client.post(
            "/_test/refresh-dep",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert res.status_code == 401
        print(res.json())
