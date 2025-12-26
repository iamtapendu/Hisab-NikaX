import pytest
from datetime import datetime
import os

from core.security import hash_password
from modules.users.model import User

# ---------------- FIXTURES ---------------- #


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
@pytest.mark.scenario("TS001")
class TestTS001:
    """
    Module: USERS

    Test Scenario: TS001

    Description: model, routes, service and schema file should be available at /backend/modules/users/
    """

    @pytest.mark.case("TC001")
    def test_if_model_exists(self):
        """
        Test Case: TC001

        Description: Verify model.py file should be available at /backend/modules/users/
        """
        assert os.path.exists("backend/modules/users/model.py")

    @pytest.mark.case("TC002")
    def test_if_routes_exists(self):
        """
        Test Case: TC002

        Description: Verify routes.py file should be available at /backend/modules/users/
        """
        assert os.path.exists("backend/modules/users/routes.py")

    @pytest.mark.case("TC003")
    def test_if_service_exists(self):
        """
        Test Case: TC003

        Description: Verify service.py file should be available at /backend/modules/users/
        """
        assert os.path.exists("backend/modules/users/service.py")

    @pytest.mark.case("TC004")
    def test_if_schema_exists(self):
        """
        Test Case: TC004

        Description: Verify schema.py file should be available at /backend/modules/users/
        """
        assert os.path.exists("backend/modules/users/schema.py")


@pytest.mark.USERS
@pytest.mark.scenario("TS002")
class TestTS002:
    """
    Module: USERS

    Test Scenario: TS002

    Description: User able to view their own profile
    """

    @pytest.mark.case("TC001")
    def test_valid_users_profile(self, client, create_user, login):
        """
        Test Case: TC001

        Description: Verify users able to see their own profile data.
        """
        user = create_user(username="User001", role="admin")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/profile", headers=headers)
        body = res.json()
        print(body)
        assert res.status_code == 200
        assert body["username"] == "User001"
        assert body["role"] == "admin"

        user = create_user(username="User002", role="manager")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/profile", headers=headers)
        body = res.json()
        print(body)
        assert res.status_code == 200
        assert body["username"] == "User002"
        assert body["role"] == "manager"

        user = create_user(username="User003", role="staff")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/profile", headers=headers)
        body = res.json()
        print(body)
        assert res.status_code == 200
        assert body["username"] == "User003"
        assert body["role"] == "staff"

        user = create_user(username="User004", role="guest")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/profile", headers=headers)
        body = res.json()
        print(body)
        assert res.status_code == 200
        assert body["username"] == "User004"
        assert body["role"] == "guest"

    @pytest.mark.case("TC002")
    def test_invalid_users_profile(self, client):
        """
        Test Case: TC002

        Description: Verify users able to see their own profile data.
        """
        res = client.get("/api/v1/users/profile")
        print(res.json())
        assert res.status_code == 401


@pytest.mark.USERS
@pytest.mark.scenario("TS003")
class TestTS003:
    """
    Module: USERS

    Test Scenario: TS003

    Description: Fetch all users data
    """

    @pytest.mark.case("TC001")
    def test_get_all_users(self, client, create_user, login):
        """
        Test Case: TC001

        Description: Verify only admin able to get all users data.
        """

        for i in range(14):
            create_user(username="User_" + str(i))

        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/?page=3&per_page=3", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert len(body["data"]) == 3
        assert body["data"][0]["username"] == "User_6"

        user = create_user(username="User002", role="manager")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/?page=3&per_page=3", headers=headers)
        print(res.json())
        assert res.status_code == 403

        user = create_user(username="User003", role="staff")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/?page=3&per_page=3", headers=headers)
        print(res.json())
        assert res.status_code == 403

        user = create_user(username="User004", role="guest")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/?page=3&per_page=3", headers=headers)
        print(res.json())
        assert res.status_code == 403

    @pytest.mark.case("TC002")
    def test_get_all_users_pagination(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify pagination working as expected
        """
        for i in range(14):
            create_user(username="User_" + str(i))

        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/?page=3&per_page=3", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert len(body["data"]) == 3
        assert body["data"][0]["username"] == "User_6"
        assert body["meta"]["page"] == 3
        assert body["meta"]["per_page"] == 3
        assert body["meta"]["pages"] == 5
        assert body["meta"]["total"] == 15

    @pytest.mark.case("TC003")
    def test_invalid_get_all_users(self, client):
        """
        Test Case: TC003

        Description: Verify without login no one able to get access
        """

        res = client.get("/api/v1/users/?page=3&per_page=3")
        body = res.json()
        print(body)

        assert res.status_code == 401


@pytest.mark.USERS
@pytest.mark.scenario("TS004")
class TestTS004:
    """
    Module: USERS

    Test Scenario: TS004

    Description: Fetch user data by id
    """

    @pytest.mark.case("TC001")
    def test_get_user_by_id(self, client, create_user, login):
        """
        Test Case: TC001

        Description: Verify admin able to get users data using valid id
        """

        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/1", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["username"] == "admin"

    @pytest.mark.case("TC002")
    def test_get_user_by_invalid_id(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify no one able to get data without valid id
        """

        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/99", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 404

    @pytest.mark.case("TC003")
    def test_get_user_only_by_admin(self, client, create_user, login):
        """
        Test Case: TC003

        Description: Verify only admin can get users data using id
        """

        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/1", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["username"] == "admin"

        user = create_user(username="User002", role="manager")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/1", headers=headers)
        print(res.json())
        assert res.status_code == 403

        user = create_user(username="User003", role="staff")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/1", headers=headers)
        print(res.json())
        assert res.status_code == 403

        user = create_user(username="User004", role="guest")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/1", headers=headers)
        print(res.json())
        assert res.status_code == 403

    @pytest.mark.case("TC004")
    def test_get_user_without_login(self, client, create_user):
        """
        Test Case: TC004

        Description: Verify without login no one able to get user data using id
        """
        create_user()
        res = client.get("/api/v1/users/1")
        body = res.json()
        print(body)

        assert res.status_code == 401


@pytest.mark.USERS
@pytest.mark.scenario("TS005")
class TestTS005:
    """
    Module: USERS

    Test Scenario: TS005

    Description: Fetch user data by username
    """

    @pytest.mark.case("TC001")
    def test_get_user_by_username(self, client, create_user, login):
        """
        Test Case: TC001

        Description: Verify admin able to get user’s data using valid username
        """

        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/username/admin", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["username"] == "admin"

    @pytest.mark.case("TC002")
    def test_get_user_by_invalid_username(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify no one able to get data without valid username
        """

        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/username/invalid_username", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 404

    @pytest.mark.case("TC003")
    def test_get_user_only_by_admin(self, client, create_user, login):
        """
        Test Case: TC003

        Description: Verify only admin can get users data using username
        """

        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/username/admin", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["username"] == "admin"

        user = create_user(username="User002", role="manager")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/username/admin", headers=headers)
        print(res.json())
        assert res.status_code == 403

        user = create_user(username="User003", role="staff")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/username/admin", headers=headers)
        print(res.json())
        assert res.status_code == 403

        user = create_user(username="User004", role="guest")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/users/username/admin", headers=headers)
        print(res.json())
        assert res.status_code == 403

    @pytest.mark.case("TC004")
    def test_get_user_without_login(self, client, create_user):
        """
        Test Case: TC004

        Description: Verify without login no one able to get user data using username
        """
        create_user()
        res = client.get("/api/v1/users/username/admin")
        body = res.json()
        print(body)

        assert res.status_code == 401


@pytest.mark.USERS
@pytest.mark.scenario("TS006")
class TestTS006:
    """
    Module: USERS

    Test Scenario: TS002

    Description: Able to create users
    """

    @pytest.mark.case("TC001")
    def test_create_users(self, client, create_user, login):
        """
        Test Case: TC001

        Description: Verify admin can create users with valid data
        """

        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"username": "newuser", "password": "NewPass123@", "name": "New User"}

        res = client.post("/api/v1/users/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 201
        assert body["username"] == "newuser"
        assert body["name"] == "New User"
        assert body["role"] == "guest"

    @pytest.mark.case("TC002")
    def test_create_users_only_admin(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify only admin able to create users
        """
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"username": "newuser", "password": "NewPass123@", "name": "New User"}

        res = client.post("/api/v1/users/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 201
        assert body["username"] == "newuser"
        assert body["name"] == "New User"
        assert body["role"] == "guest"

        user = create_user(username="manager", role="manager")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"username": "newuser1", "password": "NewPass123@", "name": "New User"}

        res = client.post("/api/v1/users/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 403

        user = create_user(username="staff", role="staff")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"username": "newuser1", "password": "NewPass123@", "name": "New User"}

        res = client.post("/api/v1/users/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 403

        user = create_user(username="guest", role="guest")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"username": "newuser1", "password": "NewPass123@", "name": "New User"}

        res = client.post("/api/v1/users/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 403

    @pytest.mark.case("TC003")
    def test_create_users_without_login(self, client):
        """
        Test Case: TC003

        Description: Verify without login no one able to create user
        """

        payload = {"username": "newuser", "password": "NewPass123@", "name": "New User"}

        res = client.post("/api/v1/users/", json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 401

    @pytest.mark.case("TC004")
    def test_create_users_missing_data(self, client, create_user, login):
        """
        Test Case: TC004

        Description: Verify user can not be created without mandatory data. i.e. username, name, password
        """
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"username": "", "password": "NewPass123@", "name": "New User"}

        res = client.post("/api/v1/users/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 422

        # not sending name
        payload = {"username": "user001", "password": "NewPass123@"}

        res = client.post("/api/v1/users/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 422

        # not sending password
        payload = {"username": "user001", "password": "", "name": "User"}

        res = client.post("/api/v1/users/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 422

    @pytest.mark.case("TC005")
    def test_create_users_duplicate_username(self, client, create_user, login):
        """
        Test Case: TC005

        Description: Verify user can not be created without unique username
        """

        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"username": user.username, "password": "NewPass123@", "name": "New User"}

        res = client.post("/api/v1/users/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 409

    @pytest.mark.case("TC006")
    def test_create_users_role_default(self, client, create_user, login):
        """
        Test Case: TC006

        Description: Verify if role is not provided its gets default value as Guest
        """

        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"username": "TestUser", "password": "NewPass123@", "name": "New User"}

        res = client.post("/api/v1/users/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 201
        assert body["username"] == "TestUser"
        assert body["role"] == "guest"

    @pytest.mark.case("TC007")
    def test_create_users_invalid_username(self, client, create_user, login):
        """
        Test Case: TC007

        Description: Verify user can not be created with invalid username.
        """
        # Admin account
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        invalid_usernames = [
            "un",
            "_abc",
            "abc__",
            "abc@aabc",
            "agb_.dd",
            "john.",
            "abc_",
            ".shsdg",
            "thisusernameiswaytoolong123",
            "ab..cd",
        ]

        for uname in invalid_usernames:
            payload = {"username": uname, "password": "NewPass123@", "name": "New User"}
            res = client.post("/api/v1/users/", headers=headers, json=payload)

            assert res.status_code == 422

    @pytest.mark.case("TC008")
    def test_create_users_invalid_name(self, client, create_user, login):
        """
        Test Case: TC008

        Description: Verify user can not be created with invalid name
        """
        # Admin account
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        invalid_names = [
            "A",
            "0hngfdg",
            "John123()",
            "John_Doe",
            "John-Doe",
            "John!",
            "@John",
            "John@",
            "J$",
            "O'Connor",
            "Mary-Jane",
            "李雷",
            "123John",
            "J" * 51,
            "John\tDoe",
            "John\nDoe",
        ]

        for name in invalid_names:
            payload = {"username": "TestUser", "password": "NewPass123@", "name": name}
            res = client.post("/api/v1/users/", headers=headers, json=payload)

            assert res.status_code == 422

    @pytest.mark.case("TC009")
    def test_create_users_invalid_email(self, client, create_user, login):
        """
        Test Case: TC009

        Description: Verify user can not be created with invalid email
        """
        # Admin account
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        invalid_emails = [
            "plainaddress",
            "@no-local-part.com",
            "no-at-sign.com",
            "user@",
            "user@.com",
            "user@com",
            "user@site.",
            "user@site.c",
            "user@.site.com",
            "user..name@example.com",
            "user@example..com",
            "user@exa_mple.com",
            "user@exam!ple.com",
            "user@site,com",
            "user@site com",
            "user@@example.com",
            "user@#example.com",
            "user@exam$ple.com",
            "user@.com.com",
            "user@site..domain.com",
            "user@domain.toolongtldddd",
            "userexample.com",
            "user.@example.com",
            ".user@example.com",
            "user@-example.com",
            "user@example-.com",
            "user@exam..ple.com",
            "user@ex..ample.com",
            "user@exa mple.com",
            "user@",
            "user@domain..com",
            "user\\@example.com",
            "user@domain,com",
            "user@domain;com",
            "user@domain@com",
        ]

        for email in invalid_emails:
            payload = {
                "username": "TestUser",
                "password": "NewPass123@",
                "name": "new user",
                "email": email,
            }
            res = client.post("/api/v1/users/", headers=headers, json=payload)

            assert res.status_code == 422

    @pytest.mark.case("TC010")
    def test_create_users_invalid_phone(self, client, create_user, login):
        """
        Test Case: TC010

        Description: Verify user can not be created with invalid phone
        """
        # Admin account
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        invalid_phones = [
            "1234567890",
            "0123456789",
            "5555555555",
            "1111111111",
            "0000000000",
            "67890",
            "987654321",
            "9876543210987",
            "+91",
            "+91987654321",
            "+91-987654321",
            "+91 98765",
            "+91--9876543210",
            "98765 43210",
            "98-76543210",
            "98 76 54 32 10",
            "+91  9876543210",
            "+9109876543210",
            "+91- 9876543210",
            "+91 98765-43210",
            "A987654321",
            "+91A987654321",
            "987654321O",
            "+91-987654321O",
            "9876543O10",
            "98765_43210",
            "+91_9876543210",
        ]

        for phone in invalid_phones:
            payload = {
                "username": "TestUser",
                "password": "NewPass123@",
                "name": "new user",
                "phone": phone,
            }

            res = client.post("/api/v1/users/", headers=headers, json=payload)

            assert res.status_code == 422

    @pytest.mark.case("TC011")
    def test_create_users_invalid_role(self, client, create_user, login):
        """
        Test Case: TC011

        Description: Verify user can not be created with invalid role
        """
        # Admin account
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        invalid_roles = ["user", "human", "administration", "executive", "ceo"]

        for role in invalid_roles:
            payload = {
                "username": "TestUser",
                "password": "NewPass123@",
                "name": "new user",
                "role": role,
            }

            res = client.post("/api/v1/users/", headers=headers, json=payload)

            assert res.status_code == 422

    @pytest.mark.case("TC012")
    def test_create_users_invalid_image(self, client, create_user, login):
        """
        Test Case: TC012

        Description: Verify user can not be created with invalid image
        """
        # Admin account
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        invalid_images = [
            ".jpg",
            "image",
            "image.bmp",
            "image.gif",
            "image.jpgg",
            "imagejpeg",
            "image.jpeg.png",
            "image..jpg",
            "im@ge.jpg",
            "im#ge.png",
            "image!.jpeg",
        ]

        for image in invalid_images:
            payload = {
                "username": "TestUser",
                "password": "NewPass123@",
                "name": "new user",
                "image": image,
            }

            res = client.post("/api/v1/users/", headers=headers, json=payload)

            assert res.status_code == 422

    @pytest.mark.case("TC013")
    def test_create_users_invalid_password(self, client, create_user, login):
        """
        Test Case: TC013

        Description: Verify user can not be created with invalid password
        """
        # Admin account
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        invalid_passwords = [
            "password",
            "PASSWORD",
            "12345678",
            "password123",
            "PASSWORD123",
            "pass1234",
            "Passw0rd",
            "Passw@rd",
            "1234@ABC",
            "abcd!@#$",
            "ABCDEF12",
            "abcABC!@",
            "abcd1234",
            "ABCD1234",
            "abcdABCD",
            "abcdAB12",
            "abcd!@12",
            "AB12!@#",
            "abcdAB!@",
            "1234567!",
        ]

        for password in invalid_passwords:
            payload = {"username": "TestUser", "password": password, "name": "new user"}

            res = client.post("/api/v1/users/", headers=headers, json=payload)

            assert res.status_code == 422

    @pytest.mark.case("TC014")
    def test_create_users_extra_payload_field(self, client, create_user, login):
        """
        Test Case: TC014

        Description: Verify extra/unexpected fields are ignored
        """
        # Admin account
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        payload = {
            "username": "TestUser",
            "password": "Test@pass123",
            "name": "new user",
            "unwanted": "value",
        }

        res = client.post("/api/v1/users/", headers=headers, json=payload)
        print(res.json())
        assert res.status_code == 201
        assert "unwanted" not in res.json()


@pytest.mark.USERS
@pytest.mark.scenario("TS007")
class TestTS007:
    """
    Module: USERS

    Test Scenario: TS007

    Description: Able to update users
    """

    @pytest.mark.case("TC001")
    def test_update_by_user(self, client, create_user, login):
        """
        Test Case: TC001

        Description: Verify user able to update their own data with valid data.
        """
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"username": "TestUser", "name": "New User"}

        res = client.put("/api/v1/users/" + str(user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 200
        assert body["username"] == "TestUser"
        assert body["name"] == "New User"

    @pytest.mark.case("TC002")
    def test_update_by_admin(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify only admin able to update others data with valid data
        """
        target_user = create_user(username="target_user", name="User001", role="guest")
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"name": "New User"}

        res = client.put("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 200
        assert body["name"] == "New User"

        user = create_user(username="manager", role="manager")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"name": "New User"}

        res = client.put("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 403

        user = create_user(username="staff", role="staff")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"name": "New User"}

        res = client.put("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 403

        user = create_user(username="guest", role="guest")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"name": "New User"}

        res = client.put("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 403

    @pytest.mark.case("TC003")
    def test_update_invalid_id(self, client, create_user, login):
        """
        Test Case: TC003

        Description: Verify user able to update with a valid user id
        """
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"name": "New User"}

        res = client.put("/api/v1/users/" + str(99), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 404

    @pytest.mark.case("TC004")
    def test_update_unique_username(self, client, create_user, login):
        """
        Test Case: TC004

        Description: Verify while updating username it must be unique
        """
        create_user(username="User001", name="User001", role="guest")
        target_user = create_user(username="User002", name="User002", role="guest")
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"username": "User001"}

        res = client.put("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 409

        payload = {"username": "User002"}

        res = client.put("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 200

    @pytest.mark.case("TC005")
    def test_update_password_rejected(self, client, create_user, login):
        """
        Test Case: TC005

        Description: Verify users not able to update password using update api call
        """
        create_user(username="User001", name="User001", role="guest")
        target_user = create_user(username="User002", name="User002", role="guest")
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"password": "New@password*123"}

        res = client.put("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 400

    @pytest.mark.case("TC006")
    def test_update_role_only_by_admin(self, client, create_user, login):
        """
        Test Case: TC006

        Description: Verify only admin able to update user role
        """
        target_user = create_user(username="target_user", name="User001", role="guest")
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"role": "admin"}

        res = client.put("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 200
        assert body["role"] == "admin"

        user = create_user(username="manager", role="manager")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        res = client.put("/api/v1/users/" + str(user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 200
        assert body["role"] == "manager"

        user = create_user(username="staff", role="staff")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        res = client.put("/api/v1/users/" + str(user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 200
        assert body["role"] == "staff"

        user = create_user(username="guest", role="guest")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        res = client.put("/api/v1/users/" + str(user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 200
        assert body["role"] == "guest"

    @pytest.mark.case("TC007")
    def test_update_last_updated(self, client, create_user, login):
        """
        Test Case: TC007

        Description: Verify after successful update last updated value updated automatically
        """
        target_user = create_user(username="target_user", name="User001", role="guest")
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"role": "admin"}

        res = client.put("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 200
        assert body["role"] == "admin"
        created_at = datetime.fromisoformat(body["created_at"])
        last_updated = datetime.fromisoformat(body["last_updated"])
        assert created_at < last_updated

    @pytest.mark.case("TC008")
    def test_update_empty_payload(self, client, create_user, login):
        """
        Test Case: TC008

        Description: Verify empty update payload is rejected
        """
        target_user = create_user(username="target_user", name="User001", role="guest")
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {}

        res = client.put("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 400

    @pytest.mark.case("TC009")
    def test_update_extra_fields_ignored(self, client, create_user, login):
        """
        Test Case: TC008

        Description: Verify extra/unexpected fields are ignored
        """
        target_user = create_user(username="target_user", name="User001", role="guest")
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"unwanted": "value", "name": "user002"}

        res = client.put("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 200


@pytest.mark.USERS
@pytest.mark.scenario("TS008")
class TestTS008:
    """
    Module: USERS

    Test Scenario: TS008

    Description: Able to update password
    """

    @pytest.mark.case("TC001")
    def test_update_password_by_user(self, client, create_user, login):
        """
        Test Case: TC001

        Description: Verify users able to change password with valid old and new password using valid id
        """
        user = create_user(role="manager")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"current_password": "Password@123", "new_password": "New@pass123"}

        res = client.patch("/api/v1/users/" + str(user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 200
        login(user.username, "New@pass123")

    @pytest.mark.case("TC002")
    def test_update_password_invalid_id(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify users not able to change password without valid id
        """
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"current_password": "Password@123", "new_password": "New@pass123"}

        res = client.patch("/api/v1/users/" + str(99), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 404

    @pytest.mark.case("TC003")
    def test_update_password_only_by_admin(self, client, create_user, login):
        """
        Test Case: TC003

        Description: Verify only admin able to update others password with valid data
        """
        target_user = create_user(username="user", role="guest")
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"current_password": "Password@123", "new_password": "New@pass123"}

        res = client.patch("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 200
        login(target_user.username, "New@pass123")

        user = create_user(username="manager", role="manager")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"current_password": "New@pass123", "new_password": "Password@123"}

        res = client.patch("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 403

        user = create_user(username="staff", role="staff")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"current_password": "New@pass123", "new_password": "Password@123"}

        res = client.patch("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 403

        user = create_user(username="guest", role="guest")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"current_password": "New@pass123", "new_password": "Password@123"}

        res = client.patch("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 403

    @pytest.mark.case("TC004")
    def test_update_password_bypass_by_admin(self, client, create_user, login):
        """
        Test Case: TC004

        Description: verify only admin able change password without needing to care about current password.
        """
        target_user = create_user(username="user", role="guest")
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"current_password": "invalidpass", "new_password": "New@pass123"}

        res = client.patch("/api/v1/users/" + str(target_user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 200
        login(target_user.username, "New@pass123")

    @pytest.mark.case("TC005")
    def test_update_password_same_password(self, client, create_user, login):
        """
        Test Case: TC005

        Description: Verify user not able to update password if the password is same as current
        """
        user = create_user(role="manager")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"current_password": "Password@123", "new_password": "Password@123"}

        res = client.patch("/api/v1/users/" + str(user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 409

    @pytest.mark.case("TC006")
    def test_update_password_wrong_current_password(self, client, create_user, login):
        """
        Test Case: TC006

        Description: Verify user not able to update password if the current password doesnt match
        """
        user = create_user(role="manager")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"current_password": "Password", "new_password": "Password@123"}

        res = client.patch("/api/v1/users/" + str(user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 401

    @pytest.mark.case("TC007")
    def test_update_password_last_updated(self, client, create_user, login):
        """
        Test Case: TC007

        Description: Verify after successful update last updated value updated automatically
        """
        user = create_user(role="manager")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {"current_password": "Password@123", "new_password": "New@pass123"}

        res = client.patch("/api/v1/users/" + str(user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 200
        created_at = datetime.fromisoformat(body["created_at"])
        last_updated = datetime.fromisoformat(body["last_updated"])
        assert created_at < last_updated

    @pytest.mark.case("TC008")
    def test_update_password_empty_payload_rejected(self, client, create_user, login):
        """
        Test Case: TC008

        Description: Verify empty update payload is rejected
        """
        user = create_user(role="manager")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {}

        res = client.patch("/api/v1/users/" + str(user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 422

    @pytest.mark.case("TC009")
    def test_update_password_extra_field_ignored(self, client, create_user, login):
        """
        Test Case: TC009

        Description: Verify extra/unexpected fields are ignored
        """
        user = create_user(role="manager")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        payload = {
            "current_password": "Password@123",
            "new_password": "New@pass123",
            "unwanted": "value",
        }

        res = client.patch("/api/v1/users/" + str(user.id), headers=headers, json=payload)
        body = res.json()
        print(body)
        assert res.status_code == 200


@pytest.mark.USERS
@pytest.mark.scenario("TS009")
class TestTS009:
    """
    Module: USERS

    Test Scenario: TS009

    Description: Able to delete users
    """

    @pytest.mark.case("TC001")
    def test_delete_user(self, client, create_user, login):
        """
        Test Case: TC001

        Description: Verify admin able to delete user using valid id
        """
        target_user = create_user(username="user", role="guest")
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        res = client.delete("/api/v1/users/" + str(target_user.id), headers=headers)
        assert res.status_code == 204

    @pytest.mark.case("TC002")
    def test_delete_invalid_user_id(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify admin not able to delete user without valid id
        """
        target_user = create_user(username="user", role="guest")
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        res = client.delete("/api/v1/users/" + str(99), headers=headers)
        body = res.json()
        print(body)
        assert res.status_code == 404

    @pytest.mark.case("TC003")
    def test_delete_user_only_by_admin(self, client, create_user, login):
        """
        Test Case: TC003

        Description: Verify only admin can delete user
        """
        target_user = create_user(username="user", role="guest")
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        res = client.delete("/api/v1/users/" + str(target_user.id), headers=headers)
        assert res.status_code == 204

        user = create_user(username="manager", role="manager")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        res = client.delete("/api/v1/users/" + str(target_user.id), headers=headers)
        body = res.json()
        print(body)
        assert res.status_code == 403

        user = create_user(username="staff", role="staff")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        res = client.delete("/api/v1/users/" + str(target_user.id), headers=headers)
        body = res.json()
        print(body)
        assert res.status_code == 403

        user = create_user(username="guest", role="guest")
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        res = client.delete("/api/v1/users/" + str(target_user.id), headers=headers)
        body = res.json()
        print(body)
        assert res.status_code == 403

    @pytest.mark.case("TC004")
    def test_delete_admin_own_account(self, client, create_user, login):
        """
        Test Case: TC004

        Description: Verify current admin can not delete his own account
        """
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}

        res = client.delete("/api/v1/users/" + str(user.id), headers=headers)
        body = res.json()
        print(body)
        assert res.status_code == 403
