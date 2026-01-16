import os
import pytest

from modules.users.model import User
from modules.products.model import Product
from core.security import hash_password


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


@pytest.fixture
def create_product(db_session):
    def _create_product(
        name, buy_price="10", sell_price="20", quantity=1, unit="pcs", brand="company"
    ):
        product = Product(
            name=name,
            buy_price=buy_price,
            sell_price=sell_price,
            quantity=quantity,
            unit=unit,
            brand=brand,
        )

        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        return product

    return _create_product


# ---------------- TEST SUITES ---------------- #


@pytest.mark.PRODUCTS
@pytest.mark.scenario("TS001")
class TestTS001:
    """
    Module: PRODUCTS

    Test Scenario: TS001

    Description: model, routes, service and schema file should be available at /backend/modules/products/
    """

    @pytest.mark.case("TC001")
    def test_if_model_exists(self):
        """
        Test Case: TC001

        Description: Verify model.py file should be available at /backend/modules/products/
        """
        assert os.path.exists("backend/modules/products/model.py")

    @pytest.mark.case("TC002")
    def test_if_routes_exists(self):
        """
        Test Case: TC002

        Description: Verify routes.py file should be available at /backend/modules/products/
        """
        assert os.path.exists("backend/modules/products/routes.py")

    @pytest.mark.case("TC003")
    def test_if_service_exists(self):
        """
        Test Case: TC001

        Description: Verify service.py file should be available at /backend/modules/products/
        """
        assert os.path.exists("backend/modules/products/service.py")

    @pytest.mark.case("TC004")
    def test_if_schema_exists(self):
        """
        Test Case: TC004

        Description: Verify schema.py file should be available at /backend/modules/products/
        """
        assert os.path.exists("backend/modules/products/schema.py")


@pytest.mark.PRODUCTS
@pytest.mark.scenario("TS002")
class TestTS002:
    """
    Module: PRODUCTS

    Test Scenario: TS002

    Description: fetch all products data
    """

    @pytest.mark.case("TC001")
    def test_valid_roles_access(self, client, create_user, login):
        """
        Test Case: TC001

        Description: Verify with only manager, admin and staff are able to fetch all product data
        """
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200

        user = create_user(username="manager", role="manager")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200

        user = create_user(username="staff", role="staff")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200

    @pytest.mark.case("TC002")
    def test_guest_role_forbidden(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify guest not able to fetch product data
        """
        user = create_user(username="guest", role="guest")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 403

    @pytest.mark.case("TC003")
    def test_products_pagination(self, client, create_user, login, create_product):
        """
        Test Case: TC003

        Description: Verify pagination is working perfectly
        """
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/", headers=headers)

        for i in range(27):
            create_product(name=f"product_{i}")

        res = client.get("/api/v1/products/?page=1&per_page=10", headers=headers)
        body = res.json()

        print(body)
        assert res.status_code == 200
        assert len(body["data"]) == 10
        assert body["meta"]["page"] == 1
        assert body["meta"]["per_page"] == 10
        assert body["meta"]["pages"] == 3
        assert body["meta"]["total"] == 27

        res = client.get("/api/v1/products/?page=5&per_page=3", headers=headers)
        body = res.json()

        print(body)
        assert res.status_code == 200
        assert len(body["data"]) == 3
        assert body["meta"]["page"] == 5
        assert body["meta"]["per_page"] == 3
        assert body["meta"]["pages"] == 9
        assert body["meta"]["total"] == 27

        res = client.get("/api/v1/products/?page=10", headers=headers)
        body = res.json()

        print(body)
        assert len(body["data"]) == 0

    @pytest.mark.case("TC004")
    def test_invalid_per_page(self, client, create_user, login, create_product):
        """
        Test Case: TC004

        Description: Verify per_page>100 resulting validation error
        """
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/", headers=headers)

        for i in range(27):
            create_product(name=f"product_{i}")

        res = client.get("/api/v1/products/?page=1&per_page=101", headers=headers)
        body = res.json()

        print(body)
        assert res.status_code == 422

    @pytest.mark.case("TC005")
    def test_without_authentication(self, client):
        """
        Test Case: TC005

        Description: Verify not able access products end point without valid login
        """

        res = client.get("/api/v1/products/")
        body = res.json()

        print(body)
        assert res.status_code == 401


@pytest.mark.PRODUCTS
@pytest.mark.scenario("TS003")
class TestTS003:
    """
    Module: PRODUCTS

    Test Scenario: TS003

    Description: fetch product data by id
    """

    @pytest.mark.case("TC001")
    def test_valid_roles_access(self, client, create_user, login, create_product):
        """
        Test Case: TC001

        Description: Verify with only manager, admin and staff roles are able to fetch product data by id
        """
        user = create_user()
        access, _ = login(user.username)
        create_product(name="product1")

        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/1", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200

        user = create_user(username="manager", role="manager")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/1", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200

        user = create_user(username="staff", role="staff")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/1", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200

        user = create_user(username="guest", role="guest")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/1", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 403

    @pytest.mark.case("TC002")
    def test_product_with_invalid_id(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify users not able to fetch data with invalid id
        """
        user = create_user()
        access, _ = login(user.username)

        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/1", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 404

    @pytest.mark.case("TC003")
    def test_product_without_authentication(self, client, create_user, login):
        """
        Test Case: TC003

        Description: Verify not able access products end point without valid login
        """
        res = client.get("/api/v1/products/1")
        body = res.json()
        print(body)

        assert res.status_code == 401


@pytest.mark.PRODUCTS
@pytest.mark.scenario("TS004")
class TestTS004:
    """
    Module: PRODUCTS

    Test Scenario: TS004

    Description: search product data
    """

    @pytest.mark.case("TC001")
    def test_valid_roles_access(self, client, create_user, login, create_product):
        """
        Test Case: TC001

        Description: Verify only manager, admin and staff are able to search
        """
        user = create_user()
        access, _ = login(user.username)
        create_product(name="product brand model color size")

        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/search", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200

        user = create_user(username="manager", role="manager")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/search", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200

        user = create_user(username="staff", role="staff")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/search", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200

        user = create_user(username="guest", role="guest")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/search", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 403

    @pytest.mark.case("TC002")
    def test_search_by_keyword(self, client, create_user, login, create_product):
        """
        Test Case: TC002

        Description: Verify searching by keyword working perfectly
        """
        user = create_user()
        access, _ = login(user.username)
        create_product(name="Red Shirt Small Cotton")
        create_product(name="Blue Shirt Large Denim")
        create_product(name="Black Shoes Medium Leather")

        headers = {"Authorization": f"Bearer {access}"}
        res = client.get("/api/v1/products/search?keywords=shirt", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["meta"]["total"] == 2
        assert all("shirt" in p["name"].lower() for p in body["data"])

        res = client.get("/api/v1/products/search?keywords=red small", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["meta"]["total"] == 1
        assert body["data"][0]["name"].lower() == "red shirt small cotton"

        res = client.get("/api/v1/products/search?keywords=green", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["meta"]["total"] == 0
        assert body["data"] == []

    @pytest.mark.case("TC003")
    def test_search_without_authentication(self, client, create_user, login, create_product):
        """
        Test Case: TC003

        Description: Verify not able access products/search end point without valid login
        """
        res = client.get("/api/v1/products/search")
        body = res.json()
        print(body)

        assert res.status_code == 401

    @pytest.mark.case("TC004")
    def test_search_filters_working(self, client, create_user, login, create_product):
        """
        Test Case: TC004

        Description: Verify filters are working as expected
        """
        user = create_user(role="admin")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        create_product(name="Red Shirt", brand="Nike", unit="pcs", sell_price=500, quantity=10)
        create_product(name="Blue Shirt", brand="Adidas", unit="pcs", sell_price=1500, quantity=0)
        create_product(name="Black Shoes", brand="Nike", unit="pair", sell_price=3000, quantity=5)

        # Act & Assert: Filter by brand
        res = client.get("/api/v1/products/search?brand=nike", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["meta"]["total"] == 2
        assert all(p["brand"].lower() == "nike" for p in body["data"])

        # Act & Assert: Filter by price range
        res = client.get("/api/v1/products/search?min_price=1000&max_price=2000", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["meta"]["total"] == 1
        assert body["data"][0]["name"] == "Blue Shirt"

        # Act & Assert: Filter by stock availability (in stock)
        res = client.get("/api/v1/products/search?in_stock=true", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["meta"]["total"] == 2
        assert all(p["quantity"] > 0 for p in body["data"])

        # Act & Assert: Filter by unit
        res = client.get("/api/v1/products/search?unit=pcs", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["meta"]["total"] == 2
        assert all(p["unit"] == "pcs" for p in body["data"])

        # Act & Assert: Filter by stock availability (out of stock)
        res = client.get("/api/v1/products/search?in_stock=false", headers=headers)
        body = res.json()

        assert res.status_code == 200
        assert body["meta"]["total"] == 1
        assert body["data"][0]["quantity"] == 0

        # Act & Assert: Combined filters
        res = client.get(
            "/api/v1/products/search?brand=nike&min_price=1000&in_stock=true", headers=headers
        )
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["meta"]["total"] == 1
        assert body["data"][0]["name"] == "Black Shoes"

    @pytest.mark.case("TC005")
    def test_search_pagination_works_correctly(self, client, create_user, login, create_product):
        """
        Test Case: TC005

        Description: Verify pagination works correctly in search results
        """

        # Arrange
        user = create_user(role="admin")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        # Create multiple products to enforce pagination
        for i in range(1, 26):
            create_product(
                name=f"Product {i}", brand="PaginationTest", sell_price=100 + i, quantity=10
            )

        # Act: Page 1
        res = client.get(
            "/api/v1/products/search?keywords=Product&page=1&per_page=10", headers=headers
        )
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["meta"]["page"] == 1
        assert body["meta"]["per_page"] == 10
        assert body["meta"]["total"] == 25
        assert body["meta"]["pages"] == 3
        assert len(body["data"]) == 10

        # Act: Page 2
        res = client.get(
            "/api/v1/products/search?keywords=Product&page=2&per_page=10", headers=headers
        )
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["meta"]["page"] == 2
        assert len(body["data"]) == 10
        assert (
            body["data"][0]["name"] == "Product 15"
        )  # loaded in reverse oreder due to default order by last updated

        # Act: Page 3 (last page)
        res = client.get(
            "/api/v1/products/search?keywords=Product&page=3&per_page=10", headers=headers
        )
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["meta"]["page"] == 3
        assert len(body["data"]) == 5
        assert body["data"][-1]["name"] == "Product 1"

        # Act: Page beyond available pages
        res = client.get(
            "/api/v1/products/search?keywords=Product&page=4&per_page=10", headers=headers
        )
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["meta"]["page"] == 4
        assert body["meta"]["total"] == 25
        assert len(body["data"]) == 0

    @pytest.mark.case("TC006")
    def test_search_returns_empty_result_with_valid_pagination(self, client, create_user, login):
        """
        Test Case: TC006

        Description: Verify empty search result returns empty list with valid pagination metadata
        """

        # Arrange
        user = create_user(role="admin")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        # Act: Search with keyword that does not exist
        res = client.get(
            "/api/v1/products/search?keywords=nonexistentproduct&page=1&per_page=10",
            headers=headers,
        )
        body = res.json()
        print(body)
        # Assert
        assert res.status_code == 200

        # Data assertions
        assert "data" in body
        assert isinstance(body["data"], list)
        assert len(body["data"]) == 0

        # Pagination assertions
        assert "meta" in body
        assert body["meta"]["page"] == 1
        assert body["meta"]["per_page"] == 10
        assert body["meta"]["total"] == 0
        assert body["meta"]["pages"] == 0


@pytest.mark.PRODUCTS
@pytest.mark.scenario("TS005")
class TestTS005:
    """
    Module: PRODUCTS

    Test Scenario: TS005

    Description: Able to create product
    """

    @pytest.mark.case("TC001")
    def test_create_product_without_login(self, client):
        """
        Test Case: TC001

        Description: Verify product creation is not allowed without authentication
        """
        payload = {"name": "Product", "buy_price": "100", "sell_price": "110"}
        res = client.post("/api/v1/products/", json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 401

    @pytest.mark.case("TC002")
    def test_create_product_with_different_roles(self, client, create_user, login):
        """
        Test Case: TC002

        Description: Verify with only manager, admin roles are allowed for product create
        """
        payload = {"name": "Product", "buy_price": "100", "sell_price": "110"}
        user = create_user(username="usr1", role="guest")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.post("/api/v1/products/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 403

        user = create_user(username="usr2", role="staff")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.post("/api/v1/products/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 403

        user = create_user(username="usr3", role="manager")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.post("/api/v1/products/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 201

        user = create_user(username="usr4", role="admin")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        payload = {"name": "Product 2", "buy_price": "100", "sell_price": "110"}
        res = client.post("/api/v1/products/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 201

    @pytest.mark.case("TC003")
    def test_create_product_without_required_data(self, client, create_user, login):
        """
        Test Case: TC003

        Description: Verify without mandatory data no one is able to create product
        """
        user = create_user(username="usr4", role="admin")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        payload = {"name": "Product", "buy_price": "100", "sell_price": ""}
        res = client.post("/api/v1/products/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 422

        payload = {"name": "Product", "sell_price": "110"}
        res = client.post("/api/v1/products/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 422

        payload = {"buy_price": "100", "sell_price": ""}
        res = client.post("/api/v1/products/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 422

    @pytest.mark.case("TC004")
    def test_create_product_duplicate_name(self, client, create_user, login):
        """
        Test Case: TC004

        Description: Verify product name must be unique
        """
        user = create_user(username="usr4", role="admin")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        payload = {"name": "Product", "buy_price": "100", "sell_price": "120"}
        res = client.post("/api/v1/products/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 201

        res = client.post("/api/v1/products/", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 409

    @pytest.mark.case("TC005")
    def test_create_product_invalid_name(self, client, create_user, login):
        """
        Test Case: TC005

        Description: Verify product can not be created with invalid name
        """

        # Admin account
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        invalid_vals = [
            "ab",
            "abc",
            "a b",
            "abc##",
            "abc123!!",
            "abc/def?",
            "product" * 50,
            "abc&def",
            "<leading",
            "trailing>",
            "middle@dot",
            "_underscore",
            "abc*123",
            "abc%abc",
            "product()",
            "product+",
            "product;",
            "product'",
            "product|",
            "product[]",
            "product{}",
            "product=",
        ]

        for val in invalid_vals:
            payload = {"name": val, "buy_price": "100", "sell_price": "120"}
            res = client.post("/api/v1/products/", headers=headers, json=payload)
            print(f"{val}: {res.json()}")

            assert res.status_code == 422

    @pytest.mark.case("TC006")
    def test_create_product_invalid_description(self, client, create_user, login):
        """
        Test Case: TC006

        Description: Verify product can not be created with invalid description
        """

        # Admin account
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        invalid_vals = [
            "ab",
            "abc",
            "a b",
            "abc##",
            "abc123!!",
            "abc/def?",
            "product" * 50,
            "abc&def",
            "<leading",
            "trailing>",
            "middle@dot",
            "_underscore",
            "abc*123",
            "abc%abc",
            "product()",
            "product+",
            "product;",
            "product'",
            "product|",
            "product[]",
            "product{}",
            "product=",
        ]

        for val in invalid_vals:
            payload = {
                "name": "product",
                "buy_price": "100",
                "sell_price": "120",
                "description": val,
            }
            res = client.post("/api/v1/products/", headers=headers, json=payload)
            print(f"{val}: {res.json()}")

            assert res.status_code == 422

    @pytest.mark.case("TC007")
    def test_create_product_invalid_buy_price(self, client, create_user, login):
        """
        Test Case: TC007

        Description: Verify product can not be created with invalid buy_price
        """

        # Admin account
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        invalid_vals = [
            "-",
            "--12",
            "12-",
            "12.O",
            "-.",
            "abc",
            "12a",
            "1.2.3",
            "+-12",
            "12..3",
            "1e10",
            "--",
            "-.5",
        ]

        for val in invalid_vals:
            payload = {
                "name": "product",
                "buy_price": val,
                "sell_price": "120",
            }
            res = client.post("/api/v1/products/", headers=headers, json=payload)
            print(f"{val}: {res.json()}")

            assert res.status_code == 422

    @pytest.mark.case("TC008")
    def test_create_product_invalid_sell_price(self, client, create_user, login):
        """
        Test Case: TC008

        Description: Verify product can not be created with invalid sell_price
        """

        # Admin account
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        invalid_vals = [
            "-",
            "--12",
            "12-",
            "12.O",
            "-.",
            "abc",
            "12a",
            "1.2.3",
            "+-12",
            "12..3",
            "1e10",
            "--",
            "-.5",
        ]

        for val in invalid_vals:
            payload = {
                "name": "product",
                "buy_price": "100",
                "sell_price": val,
            }
            res = client.post("/api/v1/products/", headers=headers, json=payload)
            print(f"{val}: {res.json()}")

            assert res.status_code == 422

    @pytest.mark.case("TC009")
    def test_create_product_invalid_mrp(self, client, create_user, login):
        """
        Test Case: TC009

        Description: Verify product can not be created with invalid mrp
        """

        # Admin account
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        invalid_vals = [
            "-",
            "--12",
            "12-",
            "12.O",
            "-.",
            "abc",
            "12a",
            "1.2.3",
            "+-12",
            "12..3",
            "1e10",
            "--",
            "-.5",
        ]

        for val in invalid_vals:
            payload = {"name": "product", "buy_price": "100", "sell_price": "120", "mrp": val}
            res = client.post("/api/v1/products/", headers=headers, json=payload)
            print(f"{val}: {res.json()}")

            assert res.status_code == 422

    @pytest.mark.case("TC010")
    def test_create_product_invalid_hsn_code(self, client, create_user, login):
        """
        Test Case: TC010

        Description: Verify product can not be created with invalid hsn_code
        """

        # Admin account
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        invalid_vals = [
            "123",
            "12345",
            "1234567",
            "123456789",
            "abcd",
            "12a456",
            "20231",
            "000",
            "00000",
            "20-01",
            "2023 01",
            "2023/01",
            "999",
            "1234567890",
        ]

        for val in invalid_vals:
            payload = {"name": "product", "buy_price": "100", "sell_price": "120", "hsn_code": val}
            res = client.post("/api/v1/products/", headers=headers, json=payload)
            print(f"{val}: {res.json()}")

            assert res.status_code == 422

    @pytest.mark.case("TC011")
    def test_create_product_invalid_gst(self, client, create_user, login):
        """
        Test Case: TC011

        Description: Verify product can not be created with invalid gst
        """

        # Admin account
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        invalid_vals = [
            "-",
            "--12",
            "12-",
            "12.O",
            "-.",
            "abc",
            "12a",
            "1.2.3",
            "+-12",
            "12..3",
            "1e10",
            "--",
            "-.5",
            "10%",
            "50",
        ]

        for val in invalid_vals:
            payload = {"name": "product", "buy_price": "100", "sell_price": "120", "gst": val}
            res = client.post("/api/v1/products/", headers=headers, json=payload)
            print(f"{val}: {res.json()}")

            assert res.status_code == 422

    @pytest.mark.case("TC012")
    def test_create_product_invalid_quantity(self, client, create_user, login):
        """
        Test Case: TC012

        Description: Verify product can not be created with invalid quantity
        """

        # Admin account
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        invalid_vals = [
            "-",
            "--12",
            "12-",
            "12.",
            "-.",
            "abc",
            "12a",
            "1.2.3",
            "+-12",
            "12..3",
            "1e10",
            "--",
            "-.5",
            "10%",
        ]

        for val in invalid_vals:
            payload = {"name": "product", "buy_price": "100", "sell_price": "120", "quantity": val}
            res = client.post("/api/v1/products/", headers=headers, json=payload)
            print(f"{val}: {res.json()}")

            assert res.status_code == 422

    @pytest.mark.case("TC013")
    def test_create_product_invalid_unit(self, client, create_user, login):
        """
        Test Case: TC013

        Description: Verify product can not be created with invalid unit
        """

        # Admin account
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        invalid_vals = [
            "pc",
            "kgs",
            "grams",
            "litre",
            "liter",
            "ltr.",
            "mls",
            "boxes",
            "packet",
            "sets",
            "doz",
            "dozens",
            "PCS",
            "Kg",
            "123",
            "box1",
        ]

        for val in invalid_vals:
            payload = {"name": "product", "buy_price": "100", "sell_price": "120", "unit": val}
            res = client.post("/api/v1/products/", headers=headers, json=payload)
            print(f"{val}: {res.json()}")

            assert res.status_code == 422

    @pytest.mark.case("TC014")
    def test_create_product_invalid_brand(self, client, create_user, login):
        """
        Test Case: TC014

        Description: Verify product can not be created with invalid brand
        """

        # Admin account
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        invalid_vals = [
            "ab",
            "abc",
            "a b",
            "abc##",
            "abc123!!",
            "abc/def?",
            "product" * 50,
            "abc&def",
            "<leading",
            "trailing>",
            "middle@dot",
            "_underscore",
            "abc*123",
            "abc%abc",
            "product()",
            "product+",
            "product;",
            "product'",
            "product|",
            "product[]",
            "product{}",
            "product=",
        ]

        for val in invalid_vals:
            payload = {
                "name": "product",
                "buy_price": "100",
                "sell_price": "120",
                "brand": val,
            }
            res = client.post("/api/v1/products/", headers=headers, json=payload)
            print(f"{val}: {res.json()}")

            assert res.status_code == 422

    @pytest.mark.case("TC015")
    def test_create_product_invalid_model(self, client, create_user, login):
        """
        Test Case: TC015

        Description: Verify product can not be created with invalid model
        """

        # Admin account
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        invalid_vals = [
            "ab",
            "abc",
            "a b",
            "abc##",
            "abc123!!",
            "abc/def?",
            "product" * 50,
            "abc&def",
            "<leading",
            "trailing>",
            "middle@dot",
            "_underscore",
            "abc*123",
            "abc%abc",
            "product()",
            "product+",
            "product;",
            "product'",
            "product|",
            "product[]",
            "product{}",
            "product=",
        ]

        for val in invalid_vals:
            payload = {
                "name": "product",
                "buy_price": "100",
                "sell_price": "120",
                "model": val,
            }
            res = client.post("/api/v1/products/", headers=headers, json=payload)
            print(f"{val}: {res.json()}")

            assert res.status_code == 422

    @pytest.mark.case("TC016")
    def test_create_product_invalid_image(self, client, create_user, login):
        """
        Test Case: TC016

        Description: Verify product can not be created with invalid image
        """

        # Admin account
        user = create_user()
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        invalid_vals = [
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

        for val in invalid_vals:
            payload = {
                "name": "product",
                "buy_price": "100",
                "sell_price": "120",
                "image": val,
            }
            res = client.post("/api/v1/products/", headers=headers, json=payload)
            print(f"{val}: {res.json()}")

            assert res.status_code == 422


@pytest.mark.PRODUCTS
@pytest.mark.scenario("TS006")
class TestTS006:
    """
    Module: PRODUCTS

    Test Scenario: TS006

    Description: Able to update product
    """

    @pytest.mark.case("TC001")
    def test_update_product_without_login(self, client, create_product):
        """
        Test Case: TC001

        Description: Verify without valid login credential no able to update products
        """
        create_product(name="product")
        payload = {"name": "Product", "buy_price": "100", "sell_price": "110"}
        res = client.put("/api/v1/products/1", json=payload)
        print(res.json())

        assert res.status_code == 401

    @pytest.mark.case("TC002")
    def test_update_product_with_different_roles(self, client, create_user, login, create_product):
        """
        Test Case: TC002

        Description: Verify with only manager, admin roles are allowed for update
        """
        create_product(name="old name")
        payload = {"name": "new name"}

        user = create_user(username="guest", role="guest")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.put("/api/v1/products/1", headers=headers, json=payload)
        print(res.json())

        assert res.status_code == 403

        user = create_user(username="staff", role="staff")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.put("/api/v1/products/1", headers=headers, json=payload)
        print(res.json())

        assert res.status_code == 403

        user = create_user(username="manager", role="manager")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.put("/api/v1/products/1", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["name"] == "new name"

        user = create_user(username="admin")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        payload = {"buy_price": "500", "sell_price": "600"}
        res = client.put("/api/v1/products/1", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 200
        assert body["buy_price"] == 500.0
        assert body["sell_price"] == 600.0

    @pytest.mark.case("TC003")
    def test_update_product_with_invalid_id(self, client, create_user, login, create_product):
        """
        Test Case: TC003

        Description: Verify users not able to update product with invalid id
        """
        create_product("product")

        user = create_user(username="admin")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        payload = {"buy_price": "500", "sell_price": "600"}
        res = client.put("/api/v1/products/2", headers=headers, json=payload)
        print(res.json())

        assert res.status_code == 404

    @pytest.mark.case("TC004")
    def test_update_product_duplicate_name(self, client, create_user, login, create_product):
        """
        Test Case: TC004

        Description: Verify users not able to update product with duplicate name
        """
        user = create_user(username="admin")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        create_product("Product 1")
        create_product("Product 2")

        payload = {"name": "Product 2", "buy_price": "100", "sell_price": "120"}
        res = client.put("/api/v1/products/1", headers=headers, json=payload)
        body = res.json()
        print(body)

        assert res.status_code == 409

    @pytest.mark.case("TC005")
    def test_update_product_invalid_data(self, client, create_user, login, create_product):
        """
        Test Case: TC005

        Description: Verify users not able to update product with invalid data
        """

        # Admin account
        user = create_user(username="admin")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        create_product("product")
        payload = {"quantity": "--100"}
        res = client.put("/api/v1/products/1", headers=headers, json=payload)
        print(res.json())

        assert res.status_code == 422


@pytest.mark.PRODUCTS
@pytest.mark.scenario("TS007")
class TestTS007:
    """
    Module: PRODUCTS

    Test Scenario: TS007

    Description: Able to delete product
    """

    @pytest.mark.case("TC001")
    def test_delete_product_without_login(self, client, create_product):
        """
        Test Case: TC001

        Description: Verify without valid login credential no able to delete products
        """
        create_product(name="product")
        res = client.delete("/api/v1/products/1")
        print(res.json())

        assert res.status_code == 401

    @pytest.mark.case("TC002")
    def test_delete_product_with_different_roles(self, client, create_user, login, create_product):
        """
        Test Case: TC002

        Description: Verify with only admin are allowed for delete product api
        """
        create_product(name="product")
        
        user = create_user(username="guest", role="guest")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.delete("/api/v1/products/1", headers=headers)
        print(res.json())

        assert res.status_code == 403

        user = create_user(username="staff", role="staff")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.delete("/api/v1/products/1", headers=headers)
        print(res.json())

        assert res.status_code == 403

        user = create_user(username="manager", role="manager")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.delete("/api/v1/products/1", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 403

        user = create_user(username="admin")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.delete("/api/v1/products/1", headers=headers)

        assert res.status_code == 204

    @pytest.mark.case("TC003")
    def test_delete_product_with_invalid_id(self, client, create_user, login, create_product):
        """
        Test Case: TC003

        Description: Verify users not able to delete product with invalid id
        """
        create_product("product")

        user = create_user(username="admin")
        access, _ = login(user.username)
        headers = {"Authorization": f"Bearer {access}"}

        res = client.delete("/api/v1/products/2", headers=headers)
        body = res.json()
        print(body)

        assert res.status_code == 404
