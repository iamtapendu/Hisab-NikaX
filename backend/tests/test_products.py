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
        assert json["code"] == 401
        assert json["status"] == "fail"
        assert "missing " in json["errors"].lower()

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

    @pytest.mark.case("TC004")
    def test_get_products_by_id(self, client, create_user, login, create_product):
        """
        Test Case: TC004

        Description: Verify with only manager, admin and staff roles are allowed for
        product api access when fetching data by id
        """
        create_product(name=f"product_1")
        res = client.get("/api/products/1")
        json = res.get_json()

        assert res.status_code == 401
        assert json["code"] == 401
        assert json["status"] == "fail"
        assert "missing " in json["errors"].lower()

        guest = create_user(username="usr1", role="guest")
        json = login(guest.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/products/1", headers=headers)
        json = res.get_json()

        assert res.status_code == 403
        assert json["code"] == 403
        assert json["status"] == "fail"
        assert "forbidden" in json["errors"].lower()

        staff = create_user(username="usr2", role="staff")
        json = login(staff.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/products/1", headers=headers)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"

        manager = create_user(username="usr3", role="manager")
        json = login(manager.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/products/1", headers=headers)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"

        admin = create_user(username="usr4", role="admin")
        json = login(admin.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/products/1", headers=headers)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert json["data"]["name"] == "product_1"

    @pytest.mark.case("TC005")
    def test_get_products_by_invalid_id(self, client, create_user, login):
        """
        Test Case: TC005

        Description: Verify users not able to fetch data with invalid id
        """

        admin = create_user(username="usr4", role="admin")
        json = login(admin.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/products/99", headers=headers)
        json = res.get_json()

        assert res.status_code == 404
        assert json["code"] == 404
        assert json["status"] == "fail"

    @pytest.mark.case("TC006")
    def test_get_products_by_search(self, client, create_user, login, create_product):
        """
        Test Case: TC006

        Description: Verify with only manager, admin and staff roles are allowed
        for product api access when searching
        """
        create_product(name=f"product_1")
        res = client.get("/api/products/search?q=pr")
        json = res.get_json()

        assert res.status_code == 401
        assert json["code"] == 401
        assert json["status"] == "fail"
        assert "missing " in json["errors"].lower()

        guest = create_user(username="usr1", role="guest")
        json = login(guest.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/products/search?q=pr", headers=headers)
        json = res.get_json()

        assert res.status_code == 403
        assert json["code"] == 403
        assert json["status"] == "fail"
        assert "forbidden" in json["errors"].lower()

        staff = create_user(username="usr2", role="staff")
        json = login(staff.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/products/search?q=pr", headers=headers)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"

        manager = create_user(username="usr3", role="manager")
        json = login(manager.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/products/search?q=pr", headers=headers)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"

        admin = create_user(username="usr4", role="admin")
        json = login(admin.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/products/search?q=pr", headers=headers)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert json["data"][0]["name"] == "product_1"

    @pytest.mark.case("TC007")
    def test_searched_products_results(self, client, create_user, login, create_product):
        """
        Test Case: TC007

        Description: Verify searching by keyword working perfectly
        """
        create_product(name=f"MUD GUARD HERO 22 BLACK")
        create_product(name=f"MUD GUARD HERO 20 BLACK")
        create_product(name=f"MUD GUARD HERO 22 RED")
        create_product(name=f"MUD GUARD HERO 20 RED")
        create_product(name=f"MUD GUARD VW 22 BLACK")
        create_product(name=f"MUD GUARD VW 20 BLACK")
        create_product(name=f"MUD GUARD VW 22 RED")
        create_product(name=f"MUD GUARD VW 20 RED")

        admin = create_user()
        json = login(admin.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.get("/api/products/search?q=MUD 20 RED", headers=headers)
        json = res.get_json()

        assert res.status_code == 200
        assert json["code"] == 200
        assert json["status"] == "success"
        assert len(json["data"]) == 2


@pytest.mark.PRODUCTS
@pytest.mark.scenario("TS003")
class TestTS003:
    """
    Module: PRODUCTS

    Test Scenario: TS003

    Description: Users with valid login credentials along with role able to create new product
    """

    @pytest.mark.case("TC001")
    def test_create_product_without_login(self, client):
        """
        Test Case: TC001

        Description: Verify without valid login credential no able to create products api
        """
        payload = {"name": "Product", "buy_price": "100", "sell_price": "110"}
        res = client.post("/api/products/", json=payload)
        json = res.get_json()

        assert res.status_code == 401
        assert json["code"] == 401
        assert json["status"] == "fail"
        assert "missing " in json["errors"].lower()

    @pytest.mark.case("TC002")
    def test_create_product_with_different_roles(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify with only manager, admin roles are allowed for product create api
        """
        payload = {"name": "Product", "buy_price": "100", "sell_price": "110"}
        guest = create_user(username="usr1", role="guest")
        json = login(guest.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.post("/api/products/", headers=headers, json=payload)
        json = res.get_json()

        assert res.status_code == 403
        assert json["code"] == 403
        assert json["status"] == "fail"
        assert "forbidden" in json["errors"].lower()

        staff = create_user(username="usr2", role="staff")
        json = login(staff.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.post("/api/products/", headers=headers, json=payload)
        json = res.get_json()

        assert res.status_code == 403
        assert json["code"] == 403
        assert json["status"] == "fail"

        manager = create_user(username="usr3", role="manager")
        json = login(manager.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        res = client.post("/api/products/", headers=headers, json=payload)
        json = res.get_json()

        assert res.status_code == 201
        assert json["code"] == 201
        assert json["status"] == "success"
        assert json["data"]["name"] == "Product"

        admin = create_user(username="usr4", role="admin")
        json = login(admin.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        payload = {"name": "Product 2", "buy_price": "100", "sell_price": "110"}
        res = client.post("/api/products/", headers=headers, json=payload)
        json = res.get_json()

        assert res.status_code == 201
        assert json["code"] == 201
        assert json["status"] == "success"
        assert json["data"]["name"] == "Product 2"

    @pytest.mark.case("TC003")
    def test_create_product_without_required_data(self, client, create_user, login):
        """
        Test Case: TC003

        Description: Verify without mandatory data no one is able to create product
        """
        admin = create_user(username="usr4", role="admin")
        json = login(admin.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        payload = {"name": "Product", "buy_price": "100", "sell_price": ""}
        res = client.post("/api/products/", headers=headers, json=payload)
        json = res.get_json()

        assert res.status_code == 400
        assert json["code"] == 400
        assert json["status"] == "fail"
        assert "missing mandatory fields" in json["errors"].lower()

        payload = {"name": "Product", "sell_price": "110"}
        res = client.post("/api/products/", headers=headers, json=payload)
        json = res.get_json()

        assert res.status_code == 400
        assert json["code"] == 400
        assert json["status"] == "fail"
        assert "missing mandatory fields" in json["errors"].lower()

        payload = {"buy_price": "100", "sell_price": ""}
        res = client.post("/api/products/", headers=headers, json=payload)
        json = res.get_json()

        assert res.status_code == 400
        assert json["code"] == 400
        assert json["status"] == "fail"
        assert "missing mandatory fields" in json["errors"].lower()

    @pytest.mark.case("TC004")
    def test_create_product_duplicate_name(self, client, create_user, login):
        """
        Test Case: TC004

        Description: Verify product name must be unique
        """
        admin = create_user(username="usr4", role="admin")
        json = login(admin.username, "TestPass123@")
        headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

        payload = {"name": "Product", "buy_price": "100", "sell_price": "120"}
        res = client.post("/api/products/", headers=headers, json=payload)
        json = res.get_json()

        assert res.status_code == 201
        assert json["code"] == 201
        assert json["status"] == "success"

        res = client.post("/api/products/", headers=headers, json=payload)
        json = res.get_json()

        assert res.status_code == 409
        assert json["code"] == 409
        assert json["status"] == "fail"
        assert "product name already exists" in json["errors"].lower()