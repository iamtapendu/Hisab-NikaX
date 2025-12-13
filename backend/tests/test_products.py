import os
import pytest
from sqlalchemy import select
from extensions import db

# ---------------- FIXTURES ---------------- #


@pytest.fixture
def create_user(db_session):
    """Creates and returns a sample user for products tests."""
    from users.model import User

    def _create_user(
        username="testuser",
        name="Test User",
        email="test@example.com",
        phone="9999999999",
        role="admin",
        password="TestPass123@",
    ):

        user = User(username=username, name=name, email=email, phone=phone, role=role)
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


@pytest.fixture
def create_product(db_session):
    """Creates and returns a sample products for tests."""
    from products.model import Product

    def _create_product(name, buy_price="10", sell_price="20"):
        product = Product(name=name, buy_price=buy_price, sell_price=sell_price)

        db_session.session.add(product)
        db_session.session.commit()
        return product

    return _create_product


# ---------------- TEST SUITES ---------------- #


@pytest.mark.PRODUCTS
@pytest.mark.scenario("TS001")
class TestTS001:
    """
    Module: PRODUCTS

    Test Scenario: TS001

    Description: __init__.py, model.py and route.py file should be available at /backend/products/
    """

    @pytest.mark.case("TC001")
    def test_if_init_exists(self):
        """
        Test Case: TC001

        Description: Verify __init__.py exists at /backend/products/ location
        """
        assert os.path.exists("backend/products/__init__.py")

    @pytest.mark.case("TC002")
    def test_if_model_exists(self):
        """
        Test Case: TC002

        Description: Verify model.py exists at /backend/products/ location
        """
        assert os.path.exists("backend/products/model.py")

    @pytest.mark.case("TC003")
    def test_if_routes_exists(self):
        """
        Test Case: TC001

        Description: Verify routes.py exists at /backend/products/ location
        """
        assert os.path.exists("backend/products/routes.py")


@pytest.mark.PRODUCTS
@pytest.mark.scenario("TS002")
class TestTS002:
    """
    Module: PRODUCTS

    Test Scenario: TS002

    Description: Users with valid login credentials along with role able to see all the products
    """

    @pytest.mark.case("TC001")
    def test_without_login(self, client):
        """
        Test Case: TC001

        Description: Verify without valid login credential no able to access products api
        """
        res = client.get("/api/products/")
        json = res.get_json()

        assert res.status_code == 401
        assert "missing " in json["msg"].lower()

    @pytest.mark.case("TC002")
    def test_with_different_roles(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify with only manager, admin and staff roles are allowed for product api access
        """
        guest = create_user(username="usr1", role="guest")
        json = login(guest.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/products/", headers=headers)
        json = res.get_json()

        assert res.status_code == 403
        assert json["code"] == 403
        assert json["status"] == "fail"
        assert "forbidden" in json["errors"].lower()

        staff = create_user(username="usr2", role="staff")
        json = login(staff.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/products/", headers=headers)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"

        manager = create_user(username="usr3", role="manager")
        json = login(manager.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/products/", headers=headers)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"

        admin = create_user(username="usr4", role="admin")
        json = login(admin.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/products/", headers=headers)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"

    @pytest.mark.case("TC003")
    def test_products_pagination(self, client, create_user, login, create_product):
        """
        Test Case: TC003

        Description: Verify pagination is working perfectly
        """
        user = create_user()
        json = login(user.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        for i in range(27):
            create_product(name=f"product_{i}")

        res = client.get("/api/products/?page=1&per_page=10", headers=headers)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert len(json["data"]) == 10
        assert json["pagination"]["page"] == 1
        assert json["pagination"]["per_page"] == 10
        assert json["pagination"]["pages"] == 3
        assert json["pagination"]["total"] == 27

        res = client.get("/api/products/?page=5&per_page=3", headers=headers)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert len(json["data"]) == 3
        assert json["pagination"]["page"] == 5
        assert json["pagination"]["per_page"] == 3
        assert json["pagination"]["pages"] == 9
        assert json["pagination"]["total"] == 27
