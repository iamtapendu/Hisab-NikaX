import os
import pytest
from flask_jwt_extended import decode_token

# ---------------- FIXTURES ---------------- #

@pytest.fixture
def create_user(db_session):
    """Creates and returns a sample user for users tests."""
    from users.model import User

    def _create_user(
            username="testuser",
            name="Test User",
            email="test@example.com",
            phone="9999999999",
            role="admin",
            password="TestPass123@"):
            
        user = User(
            username=username,
            name=name,
            email=email,
            phone=phone,
            role=role
        )
        user.set_password(password)

        db_session.session.add(user)
        db_session.session.commit()
        return user
    return _create_user

@pytest.fixture
def login(client):
    """
    Login helper fixture: logs in a user using given username & password.
    """
    def _login(username, password):
        payload = {"username": username, "password": password}
        res = client.post("/api/auth/login", json=payload)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert "login successful" in json["message"].lower()
        assert "access_token" in json["data"]
        assert "refresh_token" in json["data"]

        return json

    return _login


# ---------------- TEST SUITES ---------------- #

@pytest.mark.USERS
@pytest.mark.scenario("TS001")
class TestTS001:
    """
    Module: USERS	

    Test Scenario: TS001
    
    Description: __init__.py, model.py and route.py file should be available at /backend/users/
    """
    
    @pytest.mark.case("TC001")
    def test_if_init_exists(self):
        """
        Test Case: TC001

        Description: Verify __init__.py exists at /backend/users/ location
        """
        assert os.path.exists("backend/users/__init__.py")
        
    @pytest.mark.case("TC002")
    def test_if_model_exists(self):
        """
        Test Case: TC002

        Description: Verify model.py exists at /backend/users/ location
        """
        assert os.path.exists("backend/users/model.py")

    @pytest.mark.case("TC003")
    def test_if_routes_exists(self):
        """
        Test Case: TC001

        Description: Verify routes.py exists at /backend/users/ location
        """
        assert os.path.exists("backend/users/routes.py")


@pytest.mark.USERS
@pytest.mark.scenario("TS002")
class TestTS002:
    """
    Module: USERS	

    Test Scenario: TS002
    
    Description: Admin able to create users using valid data.
    """
    
    @pytest.mark.case("TC001")
    def test_if_admin_create_users(self, client, create_user, login):
        """
        Test Case: TC001

        Description: Verify only admin can access the /api/users/ and create users with valid data
        """
        # Admin account
        user = create_user()
        json = login(user.username,"TestPass123@")
        
        payload = {
            "username": "newuser",
            "password": "NewPass123@",
            "name": "New User"
        }
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.post("/api/users/", headers=headers, json=payload)
        json = res.get_json()
       
        assert res.status_code == 201
        assert json["code"] == 201
        assert json["status"] == "success"
        assert json["data"]["username"] == "newuser"
        assert json["data"]["name"] == "New User"
        assert json["data"]["role"] == "guest"

        # Admin account
        user = create_user(username="testuser2",role="manager")
        json = login(user.username,"TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.post("/api/users/", headers=headers, json=payload)
        json = res.get_json()

        assert res.status_code == 403
        assert "access denied" in json["error"].lower()

    @pytest.mark.case("TC002")
    def test_create_users_missing_data(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify user can not be created without mandatory data. i.e. username, name, password
        """
        # Admin account
        user = create_user()
        json = login(user.username,"TestPass123@")
        
        # not sending username
        payload = {
            "username": "",
            "password": "NewPass123@",
            "name": "New User"
        }
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.post("/api/users/", headers=headers, json=payload)
        json = res.get_json()
       
        assert res.status_code == 400
        assert json["code"] == 400
        assert json["status"] == "fail"
        assert "missing mandatory fields" in json["errors"].lower()

        # not sending name
        payload = {
            "username": "newuser",
            "password": "NewPass123@",
            "name": ""
        }

        res = client.post("/api/users/", headers=headers, json=payload)
        json = res.get_json()
       
        assert res.status_code == 400
        assert json["code"] == 400
        assert json["status"] == "fail"
        assert "missing mandatory fields" in json["errors"].lower()

        # not sending password
        payload = {
            "username": "newuser",
            "password": "",
            "name": "New User"
        }

        res = client.post("/api/users/", headers=headers, json=payload)
        json = res.get_json()
       
        assert res.status_code == 400
        assert json["code"] == 400
        assert json["status"] == "fail"
        assert "missing mandatory fields" in json["errors"].lower()

    @pytest.mark.case("TC003")
    def test_create_users_duplicate_username(self, client, create_user, login):
        """
        Test Case: TC003

        Description: Verify user can not be created without unique username
        """
        # Admin account
        user = create_user()
        json = login(user.username,"TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}
        
        # duplicate username
        payload = {
            "username": user.username,
            "password": "NewPass123@",
            "name": "New User"
        }

        res = client.post("/api/users/", headers=headers, json=payload)
        json = res.get_json()
       
        assert res.status_code == 409
        assert json["code"] == 409
        assert json["status"] == "fail"
        assert "username already exists" in json["errors"].lower()
        
    @pytest.mark.case("TC004")
    def test_create_users_invalid_username(self, client, create_user, login):
        """
        Test Case: TC004

        Description: Verify user can not be created with invalid username.
        """  
        # Admin account
        user = create_user()
        json = login(user.username,"TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}
        
        invalid_usernames = ["un", "_abc", "abc__", "abc@aabc", "agb_.dd", "john.", "abc_", ".shsdg", 
                             "thisusernameiswaytoolong123", "ab..cd"]

        for uname in invalid_usernames:
            payload = {
                "username": uname,
                "password": "NewPass123@",
                "name": "New User"
            }

            res = client.post("/api/users/", headers=headers, json=payload)
            json = res.get_json()

            assert res.status_code == 400
            assert json["code"] == 400
            assert json["status"] == "fail"
            assert "invalid" in json["errors"].lower()

    