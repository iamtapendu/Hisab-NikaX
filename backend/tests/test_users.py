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

        # manager account
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

    @pytest.mark.case("TC005")
    def test_create_users_invalid_name(self, client, create_user, login):
        """
        Test Case: TC005

        Description: Verify user can not be created with invalid name
        """
        # Admin account
        user = create_user()
        json = login(user.username,"TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}
        
        invalid_names = ["A","J0hn","John123","John_Doe","John-Doe","John!","@John","John@",
                         "J$","O'Connor","Mary-Jane","李雷","123John","J"*51,"John\tDoe","John\nDoe"]

        for name in invalid_names:
            payload = {
                "username": "TestUser",
                "password": "NewPass123@",
                "name": name
            }

            res = client.post("/api/users/", headers=headers, json=payload)
            json = res.get_json()

            assert res.status_code == 400
            assert json["code"] == 400
            assert json["status"] == "fail"
            assert "invalid" in json["errors"].lower()
    
    @pytest.mark.case("TC006")
    def test_create_users_invalid_email(self, client, create_user, login):
        """
        Test Case: TC006

        Description: Verify user can not be created with invalid email
        """
        # Admin account
        user = create_user()
        json = login(user.username,"TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}
        
        invalid_emails = ["plainaddress","@no-local-part.com","no-at-sign.com","user@","user@.com",
                          "user@com","user@site.","user@site.c","user@.site.com","user..name@example.com",
                          "user@example..com","user@exa_mple.com","user@exam!ple.com","user@site,com",
                          "user@site com","user@@example.com","user@#example.com","user@exam$ple.com",
                          "user@.com.com","user@site..domain.com","user@domain.toolongtldddd",
                          "userexample.com","user.@example.com",".user@example.com","user@-example.com",
                          "user@example-.com","user@exam..ple.com","user@ex..ample.com","user@exa mple.com",
                          "user@","user@domain..com","user\\@example.com","user@domain,com","user@domain;com",
                          "user@domain@com"]

        for email in invalid_emails:
            payload = {
                "username": "TestUser",
                "password": "NewPass123@",
                "name": "new user",
                "email": email
            }

            res = client.post("/api/users/", headers=headers, json=payload)
            json = res.get_json()
            
            assert res.status_code == 400
            assert json["code"] == 400
            assert json["status"] == "fail"
            assert "invalid" in json["errors"].lower()

    @pytest.mark.case("TC007")
    def test_create_users_invalid_phone(self, client, create_user, login):
        """
        Test Case: TC007

        Description: Verify user can not be created with invalid phone
        """
        # Admin account
        user = create_user()
        json = login(user.username,"TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}
        
        invalid_phones = ["1234567890","0123456789","5555555555","1111111111","0000000000",
                          "67890","987654321","9876543210987","+91","+91987654321","+91-987654321",
                          "+91 98765","+91--9876543210","98765 43210","98-76543210","98 76 54 32 10",
                          "+91  9876543210","+9109876543210","+91- 9876543210","+91 98765-43210",
                          "A987654321","+91A987654321","987654321O","+91-987654321O","9876543O10",
                          "98765_43210","+91_9876543210"]

        for phone in invalid_phones:
            payload = {
                "username": "TestUser",
                "password": "NewPass123@",
                "name": "new user",
                "phone": phone
            }

            res = client.post("/api/users/", headers=headers, json=payload)
            json = res.get_json()
            
            assert res.status_code == 400
            assert json["code"] == 400
            assert json["status"] == "fail"
            assert "invalid" in json["errors"].lower()

    @pytest.mark.case("TC008")
    def test_create_users_invalid_role(self, client, create_user, login):
        """
        Test Case: TC008

        Description: Verify user can not be created with invalid role
        """
        # Admin account
        user = create_user()
        json = login(user.username,"TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}
        
        invalid_roles = ["user","human","administration","executive","ceo"]

        for role in invalid_roles:
            payload = {
                "username": "TestUser",
                "password": "NewPass123@",
                "name": "new user",
                "role": role
            }

            res = client.post("/api/users/", headers=headers, json=payload)
            json = res.get_json()

            assert res.status_code == 400
            assert json["code"] == 400
            assert json["status"] == "fail"
            assert "invalid" in json["errors"].lower()

    @pytest.mark.case("TC009")
    def test_create_users_invalid_image(self, client, create_user, login):
        """
        Test Case: TC009

        Description: Verify user can not be created with invalid image
        """
        # Admin account
        user = create_user()
        json = login(user.username,"TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}
        
        invalid_images = [".jpg","image","image.bmp","image.gif","image.jpgg","imagejpeg",
                         "image.jpeg.png","image..jpg","im@ge.jpg","im#ge.png","image!.jpeg"]

        for image in invalid_images:
            payload = {
                "username": "TestUser",
                "password": "NewPass123@",
                "name": "new user",
                "image": image
            }

            res = client.post("/api/users/", headers=headers, json=payload)
            json = res.get_json()

            assert res.status_code == 400
            assert json["code"] == 400
            assert json["status"] == "fail"
            assert "invalid" in json["errors"].lower()

    @pytest.mark.case("TC010")
    def test_create_users_invalid_password(self, client, create_user, login):
        """
        Test Case: TC010

        Description: Verify user can not be created with invalid password
        """
        # Admin account
        user = create_user()
        json = login(user.username,"TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}
        
        invalid_passwords = ["password", "PASSWORD", "12345678", "password123", "PASSWORD123", 
                            "pass1234", "Passw0rd", "Passw@rd", "1234@ABC", "abcd!@#$", "ABCDEF12",
                            "abcABC!@", "abcd1234", "ABCD1234", "abcdABCD", "abcdAB12", "abcd!@12",
                            "AB12!@#", "abcdAB!@", "1234567!"]


        for password in invalid_passwords:
            payload = {
                "username": "TestUser",
                "password": password,
                "name": "new user"
            }

            res = client.post("/api/users/", headers=headers, json=payload)
            json = res.get_json()

            assert res.status_code == 400
            assert json["code"] == 400
            assert json["status"] == "fail"
            assert "invalid" in json["errors"].lower()


@pytest.mark.USERS
@pytest.mark.scenario("TS003")
class TestTS003:
    """
    Module: USERS

    Test Scenario: TS003
    
    Description: Admin able to get all users data.
    """
    
    @pytest.mark.case("TC001")
    def test_if_admin_get_all_users(self, client, create_user, login):
        """
        Test Case: TC001

        Description: Verify only admin able to get all users data.
        """
        # Admin account
        user = create_user()
        json = login(user.username,"TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/users/", headers=headers)
        json = res.get_json()
       
        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert json["data"][0]["username"] == "testuser"
        assert json["data"][0]["name"] == "Test User"
        assert json["data"][0]["role"] == "admin"

        # manager account
        user = create_user(username="testuser2",role="manager")
        json = login(user.username,"TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.post("/api/users/", headers=headers)
        json = res.get_json()

        assert res.status_code == 403
        assert "access denied" in json["error"].lower()

    @pytest.mark.case("TC002")
    def test_users_pagination(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify pagination working as expected
        """
        # creating more users for pagination
        for i in range(14):
            create_user(username="user_"+str(i))

        # Admin account
        user = create_user()
        json = login(user.username,"TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/users/?page=1&per_page=10", headers=headers)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert len(json["data"]) == 10

        res = client.get("/api/users/?page=2&per_page=10", headers=headers)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert len(json["data"]) == 5
        assert json["data"][0]["username"] == "user_10" 

    @pytest.mark.case("TC003")
    def test_get_users_without_login(self, client):
        """
        Test Case: TC003

        Description: Verify without login no one able to get access 
        """
        res = client.get("/api/users/?page=1&per_page=10")
        json = res.get_json()

        assert res.status_code == 401
        assert "missing authorization" in json["msg"].lower()


@pytest.mark.USERS
@pytest.mark.scenario("TS004")
class TestTS004:
    """
    Module: USERS	

    Test Scenario: TS004
    
    Description: Users only able get their own data using id or username. 
    """
    
    @pytest.mark.case("TC001")
    def test_get_by_user_id(self, client, create_user, login):
        """
        Test Case: TC001

        Description: Verify user able to get their own data using valid id.
        """
        user = create_user(role="guest")
        json = login(user.username,"TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/users/"+str(user.id), headers=headers)
        json = res.get_json()
       
        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert json["data"]["username"] == "testuser"
        assert json["data"]["name"] == "Test User"
        assert json["data"]["role"] == "guest"

        user2 = create_user(username="user_1")

        res = client.get("/api/users/"+str(user2.id), headers=headers)
        json = res.get_json()
       
        assert res.status_code == 403
        assert json["code"] == 403
        assert json["status"] == "fail"
        assert "user does not have admin access" in json["errors"].lower()

        # sending wrong id
        res = client.get("/api/users/"+"99", headers=headers)
        json = res.get_json()

        assert res.status_code == 403
        assert json["code"] == 403
        assert json["status"] == "fail"
        assert "user does not have admin access" in json["errors"].lower()
        
    
    @pytest.mark.case("TC002")
    def test_get_by_username(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify user able to get their own data using valid username
        """
        user = create_user(role="guest")
        json = login(user.username,"TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/users/username/"+user.username, headers=headers)
        json = res.get_json()
       
        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert json["data"]["username"] == "testuser"
        assert json["data"]["name"] == "Test User"
        assert json["data"]["role"] == "guest"

        user2 = create_user(username="user_1")

        res = client.get("/api/users/username/"+user2.username, headers=headers)
        json = res.get_json()
       
        assert res.status_code == 403
        assert json["code"] == 403
        assert json["status"] == "fail"
        assert "user does not have admin access" in json["errors"].lower()

        # wrong username
        res = client.get("/api/users/username/"+"username", headers=headers)
        json = res.get_json()
       
        assert res.status_code == 403
        assert json["code"] == 403
        assert json["status"] == "fail"
        assert "user does not have admin access" in json["errors"].lower()

    @pytest.mark.case("TC003")
    def test_get_user_data_by_admin(self, client, create_user, login):
        """
        Test Case: TC003

        Description: Verify only admin can get users data using id or username.
        """
        # admin account
        user = create_user()
        json = login(user.username,"TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        user2 = create_user(username="user_1",role="guest")

        res = client.get("/api/users/"+str(user2.id), headers=headers)
        json = res.get_json()
       
        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert json["data"]["username"] == "user_1"
        assert json["data"]["name"] == "Test User"
        assert json["data"]["role"] == "guest"

        res = client.get("/api/users/username/"+user2.username, headers=headers)
        json = res.get_json()
       
        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert json["data"]["username"] == "user_1"
        assert json["data"]["name"] == "Test User"
        assert json["data"]["role"] == "guest"

        # sending wrong id
        res = client.get("/api/users/"+"99", headers=headers)
        json = res.get_json()

        assert res.status_code == 404
        assert json["code"] == 404
        assert json["status"] == "fail"
        assert "404 not found" in json["errors"].lower()

        # wrong username
        res = client.get("/api/users/username/"+"username", headers=headers)
        json = res.get_json()
        
        assert res.status_code == 404
        assert json["code"] == 404
        assert json["status"] == "fail"
        assert "404 not found" in json["errors"].lower()

    @pytest.mark.case("TC004")
    def test_get_user_without_login(self, client, create_user):
        """
        Test Case: TC004

        Description: Verify without login no one able to get access
        """
        user = create_user()
        res = client.get("/api/users/"+str(user.id))
        json = res.get_json()

        assert res.status_code == 401
        assert "missing authorization" in json["msg"].lower()

        res = client.get("/api/users/username/"+user.username)
        json = res.get_json()

        assert res.status_code == 401
        assert "missing authorization" in json["msg"].lower()