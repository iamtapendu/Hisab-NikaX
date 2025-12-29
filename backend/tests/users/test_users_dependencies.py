import pytest
import jwt
import time

from core.config import settings

from core.security import hash_password
from modules.users.model import User


# ---------------- TEST FIXTURES ---------------- #


@pytest.fixture
def create_user(db_session):
    def _create_user(
        username="admin",
        name="admin",
        password="Password@123",
        email="testuser@example.com",
        phone="9876543210",
        role="admin",
        image="database/images/image.png",
    ) -> User:
        user = User(
            username=username,
            name=name,
            password_hash=hash_password(password),
            email=email,
            phone=phone,
            role=role,
            image=image,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def login(client):
    def _login(username, password="Password@123"):
        res = client.post(
            "/api/v1/auth/login",
            data={
                "username": username,
                "password": password,
                "grant_type": "password",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert res.status_code == 200
        body = res.json()
        return body["access_token"], body["refresh_token"]

    return _login


# ---------------- TEST SUITES ---------------- #


@pytest.mark.USERS
@pytest.mark.scenario("DPN001")
class TestTS001:
    """
    Module: USERS

    Test Scenario: DPN001

    Description: Users module get_current_user working as expected
    """

    @pytest.mark.case("TC001")
    def test_get_current_user_valid(self, client, create_user, login):
        """
        Test Case: TC001

        Description: Verify get_current_user returns user with valid data
        """
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.post("/_test/current-user-dep", headers=headers)

        payload = res.json()
        print(payload)

        assert res.status_code == 200
        assert payload["id"] == user.id
        assert payload["role"] == user.role

    @pytest.mark.case("TC002")
    def test_get_current_user_reject_refresh_token(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify get_current_user raise error with refresh token
        """
        user = create_user()
        _, refresh = login(user.username)
        headers = {"Authorization": f"Bearer {refresh}"}

        res = client.post("/_test/current-user-dep", headers=headers)

        payload = res.json()

        assert res.status_code == 401
        assert "invalid token type" in payload["msg"].lower()
        assert "access" in payload["errors"].lower()
        print(payload)

    @pytest.mark.case("TC003")
    def test_missing_authorization_header(self, client):
        """
        Test Case: TC003

        Description: Verify get_current_user raise error with missing authorization header
        """
        res = client.post("/_test/current-user-dep")

        assert res.status_code == 401
        print(res.json())

    @pytest.mark.case("TC004")
    def test_without_bearer(self, client, create_user, login):
        """
        Test Case: TC004

        Description: Verify get_current_user raise error with authorization header without bearer
        """
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"{access}"}

        res = client.post("/_test/current-user-dep", headers=headers)

        assert res.status_code == 401
        print(res.json())

    @pytest.mark.case("TC005")
    def test_malform_authorization_header(self, client):
        """
        Test Case: TC005

        Description: Verify get_current_user raise error with malformed authorization header (bearer only)
        """
        headers = {"Authorization": f"Bearer "}
        res = client.post("/_test/current-user-dep", headers=headers)

        assert res.status_code == 401
        print(res.json())

    @pytest.mark.case("TC006")
    def test_token_user_not_exists(self, client, access_token):
        """
        Test Case: TC006

        Description: Verify get_current_user raise error with token user does not exists
        """
        access = access_token(id="5")
        headers = {"Authorization": f"Bearer {access}"}

        res = client.post("/_test/current-user-dep", headers=headers)

        assert res.status_code == 404
        print(res.json())

    @pytest.mark.case("TC007")
    def test_invalid_jwt_format(self, client):
        """
        Test Case: TC007

        Description: Verify get_current_user raise error with invalid jwt format
        """
        res = client.post(
            "/_test/current-user-dep",
            headers={"Authorization": "Bearer abc.def.ghi"},
        )

        assert res.status_code == 401
        print(res.json())

    @pytest.mark.case("TC008")
    def test_expired_refresh_token(self, client, create_user):
        """
        Test Case: TC008

        Description: Verify get_current_user raise error with expired access token
        """
        user = create_user()
        payload = {
            "sub": str(user.id),
            "role": user.role,
            "type": "access",
            "jti": "expired-jti",
            "iat": int(time.time()) - 1000,
            "exp": int(time.time()) - 500,
            "iss": settings.PROJECT_NAME,
        }

        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        res = client.post(
            "/_test/current-user-dep",
            headers={"Authorization": f"Bearer {token}"},
        )

        body = res.json()
        assert res.status_code == 401
        assert "expired" in body["msg"].lower()
        print(res.json())

    @pytest.mark.case("TC009")
    def test_wrong_secret(self, client, create_user):
        """
        Test Case: TC009

        Description: Verify get_current_user raise error with token signed with wrong secret
        """
        user = create_user()
        payload = {
            "sub": str(user.id),
            "role": user.role,
            "type": "access",
            "jti": "wrong-secret",
            "iat": 0,
            "exp": 9999999999,
            "iss": settings.PROJECT_NAME,
        }

        token = jwt.encode(payload, "WRONG_SECRET", algorithm=settings.JWT_ALGORITHM)

        res = client.post(
            "/_test/current-user-dep",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert res.status_code == 401
        print(res.json())

    @pytest.mark.case("TC010")
    def test_wrong_issuer(self, client, create_user):
        """
        Test Case: TC010

        Description: Verify get_current_user raise error with token with wrong issuer
        """
        user = create_user()

        payload = {
            "sub": str(user.id),
            "role": user.role,
            "type": "access",
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


@pytest.mark.USERS
@pytest.mark.scenario("DPN002")
class TestTS002:
    """
    Module: USERS

    Test Scenario: DPN002

    Description: Users module get_current_user working as expected
    """

    @pytest.mark.case("TC001")
    def test_required_roles_valid(self, client, create_user, login):
        """
        Test Case: TC001

        Description: Verify required_roles working as expected with valid roles
        """
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.post("/_test/required-roles-dep", headers=headers)

        payload = res.json()
        print(payload)

        assert res.status_code == 200

    @pytest.mark.case("TC002")
    def test_required_roles_invalid(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify required_roles raise error with invalid roles.
        Valid roles - admin, manager, staff, guest
        """
        user = create_user(role="user")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.post("/_test/required-roles-dep", headers=headers)

        payload = res.json()
        print(payload)

        assert res.status_code == 403

    @pytest.mark.case("TC003")
    def test_required_roles_forged(self, client, create_user, access_token):
        """
        Test Case: TC003

        Description: Verify required_roles raise error with token with forged role
        """
        user = create_user()
        access = access_token(id=user.id, role="staff")
        headers = {"Authorization": f"Bearer {access}"}

        res = client.post("/_test/required-roles-dep", headers=headers)

        payload = res.json()
        print(payload)

        assert res.status_code == 401
