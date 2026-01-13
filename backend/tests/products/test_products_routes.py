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
    def _create_product(name, buy_price="10", sell_price="20"):
        product = Product(name=name, buy_price=buy_price, sell_price=sell_price)

        db_session.session.add(product)
        db_session.session.commit()
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


# @pytest.mark.PRODUCTS
# @pytest.mark.scenario("TS002")
# class TestTS002:
#     """
#     Module: PRODUCTS

#     Test Scenario: TS002

#     Description: Users with valid login credentials along with role able to see all the products
#     """

#     @pytest.mark.case("TC001")
#     def test_without_login(self, client):
#         """
#         Test Case: TC001

#         Description: Verify without valid login credential no able to access products api
#         """
#         res = client.get("/api/products/")
#         json = res.get_json()

#         assert res.status_code == 401
#         assert json["code"] == 401
#         assert json["status"] == "fail"
#         assert "missing " in json["errors"].lower()

#     @pytest.mark.case("TC002")
#     def test_with_different_roles(self, client, create_user, login):
#         """
#         Test Case: TC002

#         Description: Verify with only manager, admin and staff roles are allowed for product api access
#         """
#         guest = create_user(username="usr1", role="guest")
#         json = login(guest.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.get("/api/products/", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 403
#         assert json["code"] == 403
#         assert json["status"] == "fail"
#         assert "forbidden" in json["errors"].lower()

#         staff = create_user(username="usr2", role="staff")
#         json = login(staff.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.get("/api/products/", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert json["code"] == 200
#         assert json["status"] == "success"

#         manager = create_user(username="usr3", role="manager")
#         json = login(manager.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.get("/api/products/", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert json["code"] == 200
#         assert json["status"] == "success"

#         admin = create_user(username="usr4", role="admin")
#         json = login(admin.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.get("/api/products/", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert json["code"] == 200
#         assert json["status"] == "success"

#     @pytest.mark.case("TC003")
#     def test_products_pagination(self, client, create_user, login, create_product):
#         """
#         Test Case: TC003

#         Description: Verify pagination is working perfectly
#         """
#         user = create_user()
#         json = login(user.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         for i in range(27):
#             create_product(name=f"product_{i}")

#         res = client.get("/api/products/?page=1&per_page=10", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert json["code"] == 200
#         assert json["status"] == "success"
#         assert len(json["data"]) == 10
#         assert json["pagination"]["page"] == 1
#         assert json["pagination"]["per_page"] == 10
#         assert json["pagination"]["pages"] == 3
#         assert json["pagination"]["total"] == 27

#         res = client.get("/api/products/?page=5&per_page=3", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert json["code"] == 200
#         assert json["status"] == "success"
#         assert len(json["data"]) == 3
#         assert json["pagination"]["page"] == 5
#         assert json["pagination"]["per_page"] == 3
#         assert json["pagination"]["pages"] == 9
#         assert json["pagination"]["total"] == 27

#     @pytest.mark.case("TC004")
#     def test_get_products_by_id(self, client, create_user, login, create_product):
#         """
#         Test Case: TC004

#         Description: Verify with only manager, admin and staff roles are allowed for
#         product api access when fetching data by id
#         """
#         create_product(name=f"product_1")
#         res = client.get("/api/products/1")
#         json = res.get_json()

#         assert res.status_code == 401
#         assert json["code"] == 401
#         assert json["status"] == "fail"
#         assert "missing " in json["errors"].lower()

#         guest = create_user(username="usr1", role="guest")
#         json = login(guest.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.get("/api/products/1", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 403
#         assert json["code"] == 403
#         assert json["status"] == "fail"
#         assert "forbidden" in json["errors"].lower()

#         staff = create_user(username="usr2", role="staff")
#         json = login(staff.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.get("/api/products/1", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert json["code"] == 200
#         assert json["status"] == "success"

#         manager = create_user(username="usr3", role="manager")
#         json = login(manager.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.get("/api/products/1", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert json["code"] == 200
#         assert json["status"] == "success"

#         admin = create_user(username="usr4", role="admin")
#         json = login(admin.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.get("/api/products/1", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert json["code"] == 200
#         assert json["status"] == "success"
#         assert json["data"]["name"] == "product_1"

#     @pytest.mark.case("TC005")
#     def test_get_products_by_invalid_id(self, client, create_user, login):
#         """
#         Test Case: TC005

#         Description: Verify users not able to fetch data with invalid id
#         """

#         admin = create_user(username="usr4", role="admin")
#         json = login(admin.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.get("/api/products/99", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 404
#         assert json["code"] == 404
#         assert json["status"] == "fail"

#     @pytest.mark.case("TC006")
#     def test_get_products_by_search(self, client, create_user, login, create_product):
#         """
#         Test Case: TC006

#         Description: Verify with only manager, admin and staff roles are allowed
#         for product api access when searching
#         """
#         create_product(name=f"product_1")
#         res = client.get("/api/products/search?q=pr")
#         json = res.get_json()

#         assert res.status_code == 401
#         assert json["code"] == 401
#         assert json["status"] == "fail"
#         assert "missing " in json["errors"].lower()

#         guest = create_user(username="usr1", role="guest")
#         json = login(guest.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.get("/api/products/search?q=pr", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 403
#         assert json["code"] == 403
#         assert json["status"] == "fail"
#         assert "forbidden" in json["errors"].lower()

#         staff = create_user(username="usr2", role="staff")
#         json = login(staff.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.get("/api/products/search?q=pr", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert json["code"] == 200
#         assert json["status"] == "success"

#         manager = create_user(username="usr3", role="manager")
#         json = login(manager.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.get("/api/products/search?q=pr", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert json["code"] == 200
#         assert json["status"] == "success"

#         admin = create_user(username="usr4", role="admin")
#         json = login(admin.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.get("/api/products/search?q=pr", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert json["code"] == 200
#         assert json["status"] == "success"
#         assert json["data"][0]["name"] == "product_1"

#     @pytest.mark.case("TC007")
#     def test_searched_products_results(self, client, create_user, login, create_product):
#         """
#         Test Case: TC007

#         Description: Verify searching by keyword working perfectly
#         """
#         create_product(name=f"MUD GUARD HERO 22 BLACK")
#         create_product(name=f"MUD GUARD HERO 20 BLACK")
#         create_product(name=f"MUD GUARD HERO 22 RED")
#         create_product(name=f"MUD GUARD HERO 20 RED")
#         create_product(name=f"MUD GUARD VW 22 BLACK")
#         create_product(name=f"MUD GUARD VW 20 BLACK")
#         create_product(name=f"MUD GUARD VW 22 RED")
#         create_product(name=f"MUD GUARD VW 20 RED")

#         admin = create_user()
#         json = login(admin.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.get("/api/products/search?q=MUD 20 RED", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert json["code"] == 200
#         assert json["status"] == "success"
#         assert len(json["data"]) == 2


# @pytest.mark.PRODUCTS
# @pytest.mark.scenario("TS003")
# class TestTS003:
#     """
#     Module: PRODUCTS

#     Test Scenario: TS003

#     Description: Users with valid login credentials along with role able to create new product
#     """

#     @pytest.mark.case("TC001")
#     def test_create_product_without_login(self, client):
#         """
#         Test Case: TC001

#         Description: Verify without valid login credential no able to create products api
#         """
#         payload = {"name": "Product", "buy_price": "100", "sell_price": "110"}
#         res = client.post("/api/products/", json=payload)
#         json = res.get_json()

#         assert res.status_code == 401
#         assert json["code"] == 401
#         assert json["status"] == "fail"
#         assert "missing " in json["errors"].lower()

#     @pytest.mark.case("TC002")
#     def test_create_product_with_different_roles(self, client, create_user, login):
#         """
#         Test Case: TC002

#         Description: Verify with only manager, admin roles are allowed for product create api
#         """
#         payload = {"name": "Product", "buy_price": "100", "sell_price": "110"}
#         guest = create_user(username="usr1", role="guest")
#         json = login(guest.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.post("/api/products/", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 403
#         assert json["code"] == 403
#         assert json["status"] == "fail"
#         assert "forbidden" in json["errors"].lower()

#         staff = create_user(username="usr2", role="staff")
#         json = login(staff.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.post("/api/products/", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 403
#         assert json["code"] == 403
#         assert json["status"] == "fail"

#         manager = create_user(username="usr3", role="manager")
#         json = login(manager.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.post("/api/products/", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 201
#         assert json["code"] == 201
#         assert json["status"] == "success"
#         assert json["data"]["name"] == "Product"

#         admin = create_user(username="usr4", role="admin")
#         json = login(admin.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         payload = {"name": "Product 2", "buy_price": "100", "sell_price": "110"}
#         res = client.post("/api/products/", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 201
#         assert json["code"] == 201
#         assert json["status"] == "success"
#         assert json["data"]["name"] == "Product 2"

#     @pytest.mark.case("TC003")
#     def test_create_product_without_required_data(self, client, create_user, login):
#         """
#         Test Case: TC003

#         Description: Verify without mandatory data no one is able to create product
#         """
#         admin = create_user(username="usr4", role="admin")
#         json = login(admin.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         payload = {"name": "Product", "buy_price": "100", "sell_price": ""}
#         res = client.post("/api/products/", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 400
#         assert json["code"] == 400
#         assert json["status"] == "fail"
#         assert "missing mandatory fields" in json["errors"].lower()

#         payload = {"name": "Product", "sell_price": "110"}
#         res = client.post("/api/products/", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 400
#         assert json["code"] == 400
#         assert json["status"] == "fail"
#         assert "missing mandatory fields" in json["errors"].lower()

#         payload = {"buy_price": "100", "sell_price": ""}
#         res = client.post("/api/products/", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 400
#         assert json["code"] == 400
#         assert json["status"] == "fail"
#         assert "missing mandatory fields" in json["errors"].lower()

#     @pytest.mark.case("TC004")
#     def test_create_product_duplicate_name(self, client, create_user, login):
#         """
#         Test Case: TC004

#         Description: Verify product name must be unique
#         """
#         admin = create_user(username="usr4", role="admin")
#         json = login(admin.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         payload = {"name": "Product", "buy_price": "100", "sell_price": "120"}
#         res = client.post("/api/products/", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 201
#         assert json["code"] == 201
#         assert json["status"] == "success"

#         res = client.post("/api/products/", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 409
#         assert json["code"] == 409
#         assert json["status"] == "fail"
#         assert "product name already exists" in json["errors"].lower()

#     @pytest.mark.case("TC005")
#     def test_create_product_invalid_name(self, client, create_user, login):
#         """
#         Test Case: TC005

#         Description: Verify product can not be created with invalid name
#         """

#         # Admin account
#         user = create_user()
#         json = login(user.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         invalid_vals = [
#             "ab",
#             "abc",
#             "a b",
#             "abc##",
#             "abc123!!",
#             "abc/def?",
#             "product" * 50,
#             "abc&def",
#             "<leading",
#             "trailing>",
#             "middle@dot",
#             "_underscore",
#             "abc*123",
#             "abc%abc",
#             "product()",
#             "product+",
#             "product;",
#             "product'",
#             "product|",
#             "product[]",
#             "product{}",
#             "product=",
#         ]

#         for val in invalid_vals:
#             payload = {"name": val, "buy_price": "100", "sell_price": "120"}
#             res = client.post("/api/products/", headers=headers, json=payload)
#             json = res.get_json()

#             assert res.status_code == 400
#             assert json["code"] == 400
#             assert json["status"] == "fail"
#             assert "invalid" in json["errors"].lower()

#     @pytest.mark.case("TC006")
#     def test_create_product_invalid_description(self, client, create_user, login):
#         """
#         Test Case: TC006

#         Description: Verify product can not be created with invalid description
#         """

#         # Admin account
#         user = create_user()
#         json = login(user.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         invalid_vals = [
#             "ab",
#             "abc",
#             "a b",
#             "abc##",
#             "abc123!!",
#             "abc/def?",
#             "product" * 50,
#             "abc&def",
#             "<leading",
#             "trailing>",
#             "middle@dot",
#             "_underscore",
#             "abc*123",
#             "abc%abc",
#             "product()",
#             "product+",
#             "product;",
#             "product'",
#             "product|",
#             "product[]",
#             "product{}",
#             "product=",
#         ]

#         for val in invalid_vals:
#             payload = {
#                 "name": "product",
#                 "buy_price": "100",
#                 "sell_price": "120",
#                 "description": val,
#             }
#             res = client.post("/api/products/", headers=headers, json=payload)
#             json = res.get_json()

#             assert res.status_code == 400
#             assert json["code"] == 400
#             assert json["status"] == "fail"
#             assert "invalid" in json["errors"].lower()

#     @pytest.mark.case("TC007")
#     def test_create_product_invalid_buy_price(self, client, create_user, login):
#         """
#         Test Case: TC007

#         Description: Verify product can not be created with invalid buy_price
#         """

#         # Admin account
#         user = create_user()
#         json = login(user.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         invalid_vals = [
#             "-",
#             "--12",
#             "12-",
#             "12.",
#             "-.",
#             "abc",
#             "12a",
#             "1.2.3",
#             "+-12",
#             "12..3",
#             "1e10",
#             "--",
#             "-.5",
#         ]

#         for val in invalid_vals:
#             payload = {
#                 "name": "product",
#                 "buy_price": val,
#                 "sell_price": "120",
#             }
#             res = client.post("/api/products/", headers=headers, json=payload)
#             json = res.get_json()

#             assert res.status_code == 400
#             assert json["code"] == 400
#             assert json["status"] == "fail"
#             assert "invalid" in json["errors"].lower()

#     @pytest.mark.case("TC008")
#     def test_create_product_invalid_sell_price(self, client, create_user, login):
#         """
#         Test Case: TC008

#         Description: Verify product can not be created with invalid sell_price
#         """

#         # Admin account
#         user = create_user()
#         json = login(user.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         invalid_vals = [
#             "-",
#             "--12",
#             "12-",
#             "12.",
#             "-.",
#             "abc",
#             "12a",
#             "1.2.3",
#             "+-12",
#             "12..3",
#             "1e10",
#             "--",
#             "-.5",
#         ]

#         for val in invalid_vals:
#             payload = {
#                 "name": "product",
#                 "buy_price": "100",
#                 "sell_price": val,
#             }
#             res = client.post("/api/products/", headers=headers, json=payload)
#             json = res.get_json()

#             assert res.status_code == 400
#             assert json["code"] == 400
#             assert json["status"] == "fail"
#             assert "invalid" in json["errors"].lower()

#     @pytest.mark.case("TC009")
#     def test_create_product_invalid_mrp(self, client, create_user, login):
#         """
#         Test Case: TC009

#         Description: Verify product can not be created with invalid mrp
#         """

#         # Admin account
#         user = create_user()
#         json = login(user.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         invalid_vals = [
#             "-",
#             "--12",
#             "12-",
#             "12.",
#             "-.",
#             "abc",
#             "12a",
#             "1.2.3",
#             "+-12",
#             "12..3",
#             "1e10",
#             "--",
#             "-.5",
#         ]

#         for val in invalid_vals:
#             payload = {"name": "product", "buy_price": "100", "sell_price": "120", "mrp": val}
#             res = client.post("/api/products/", headers=headers, json=payload)
#             json = res.get_json()

#             assert res.status_code == 400
#             assert json["code"] == 400
#             assert json["status"] == "fail"
#             assert "invalid" in json["errors"].lower()

#     @pytest.mark.case("TC010")
#     def test_create_product_invalid_hsn_code(self, client, create_user, login):
#         """
#         Test Case: TC010

#         Description: Verify product can not be created with invalid hsn_code
#         """

#         # Admin account
#         user = create_user()
#         json = login(user.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         invalid_vals = [
#             "123",
#             "12345",
#             "1234567",
#             "123456789",
#             "abcd",
#             "12a456",
#             "20231",
#             "000",
#             "00000",
#             "20-01",
#             "2023 01",
#             "2023/01",
#             "999",
#             "1234567890",
#         ]

#         for val in invalid_vals:
#             payload = {"name": "product", "buy_price": "100", "sell_price": "120", "hsn_code": val}
#             res = client.post("/api/products/", headers=headers, json=payload)
#             json = res.get_json()

#             assert res.status_code == 400
#             assert json["code"] == 400
#             assert json["status"] == "fail"
#             assert "invalid" in json["errors"].lower()

#     @pytest.mark.case("TC011")
#     def test_create_product_invalid_gst(self, client, create_user, login):
#         """
#         Test Case: TC011

#         Description: Verify product can not be created with invalid gst
#         """

#         # Admin account
#         user = create_user()
#         json = login(user.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         invalid_vals = [
#             "-",
#             "--12",
#             "12-",
#             "12.",
#             "-.",
#             "abc",
#             "12a",
#             "1.2.3",
#             "+-12",
#             "12..3",
#             "1e10",
#             "--",
#             "-.5",
#             "10%",
#         ]

#         for val in invalid_vals:
#             payload = {"name": "product", "buy_price": "100", "sell_price": "120", "gst": val}
#             res = client.post("/api/products/", headers=headers, json=payload)
#             json = res.get_json()

#             assert res.status_code == 400
#             assert json["code"] == 400
#             assert json["status"] == "fail"
#             assert "invalid" in json["errors"].lower()

#     @pytest.mark.case("TC012")
#     def test_create_product_invalid_quantity(self, client, create_user, login):
#         """
#         Test Case: TC012

#         Description: Verify product can not be created with invalid quantity
#         """

#         # Admin account
#         user = create_user()
#         json = login(user.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         invalid_vals = [
#             "-",
#             "--12",
#             "12-",
#             "12.",
#             "-.",
#             "abc",
#             "12a",
#             "1.2.3",
#             "+-12",
#             "12..3",
#             "1e10",
#             "--",
#             "-.5",
#             "10%",
#         ]

#         for val in invalid_vals:
#             payload = {"name": "product", "buy_price": "100", "sell_price": "120", "quantity": val}
#             res = client.post("/api/products/", headers=headers, json=payload)
#             json = res.get_json()

#             assert res.status_code == 400
#             assert json["code"] == 400
#             assert json["status"] == "fail"
#             assert "invalid" in json["errors"].lower()

#     @pytest.mark.case("TC013")
#     def test_create_product_invalid_unit(self, client, create_user, login):
#         """
#         Test Case: TC013

#         Description: Verify product can not be created with invalid unit
#         """

#         # Admin account
#         user = create_user()
#         json = login(user.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         invalid_vals = [
#             "pc",
#             "kgs",
#             "grams",
#             "litre",
#             "liter",
#             "ltr.",
#             "mls",
#             "boxes",
#             "packet",
#             "sets",
#             "doz",
#             "dozens",
#             "PCS",
#             "Kg",
#             "123",
#             "box1",
#         ]

#         for val in invalid_vals:
#             payload = {"name": "product", "buy_price": "100", "sell_price": "120", "unit": val}
#             res = client.post("/api/products/", headers=headers, json=payload)
#             json = res.get_json()

#             assert res.status_code == 400
#             assert json["code"] == 400
#             assert json["status"] == "fail"
#             assert "invalid" in json["errors"].lower()

#     @pytest.mark.case("TC014")
#     def test_create_product_invalid_brand(self, client, create_user, login):
#         """
#         Test Case: TC014

#         Description: Verify product can not be created with invalid brand
#         """

#         # Admin account
#         user = create_user()
#         json = login(user.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         invalid_vals = [
#             "ab",
#             "abc",
#             "a b",
#             "abc##",
#             "abc123!!",
#             "abc/def?",
#             "product" * 50,
#             "abc&def",
#             "<leading",
#             "trailing>",
#             "middle@dot",
#             "_underscore",
#             "abc*123",
#             "abc%abc",
#             "product()",
#             "product+",
#             "product;",
#             "product'",
#             "product|",
#             "product[]",
#             "product{}",
#             "product=",
#         ]

#         for val in invalid_vals:
#             payload = {
#                 "name": "product",
#                 "buy_price": "100",
#                 "sell_price": "120",
#                 "brand": val,
#             }
#             res = client.post("/api/products/", headers=headers, json=payload)
#             json = res.get_json()

#             assert res.status_code == 400
#             assert json["code"] == 400
#             assert json["status"] == "fail"
#             assert "invalid" in json["errors"].lower()

#     @pytest.mark.case("TC015")
#     def test_create_product_invalid_model(self, client, create_user, login):
#         """
#         Test Case: TC015

#         Description: Verify product can not be created with invalid model
#         """

#         # Admin account
#         user = create_user()
#         json = login(user.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         invalid_vals = [
#             "ab",
#             "abc",
#             "a b",
#             "abc##",
#             "abc123!!",
#             "abc/def?",
#             "product" * 50,
#             "abc&def",
#             "<leading",
#             "trailing>",
#             "middle@dot",
#             "_underscore",
#             "abc*123",
#             "abc%abc",
#             "product()",
#             "product+",
#             "product;",
#             "product'",
#             "product|",
#             "product[]",
#             "product{}",
#             "product=",
#         ]

#         for val in invalid_vals:
#             payload = {
#                 "name": "product",
#                 "buy_price": "100",
#                 "sell_price": "120",
#                 "model": val,
#             }
#             res = client.post("/api/products/", headers=headers, json=payload)
#             json = res.get_json()

#             assert res.status_code == 400
#             assert json["code"] == 400
#             assert json["status"] == "fail"
#             assert "invalid" in json["errors"].lower()

#     @pytest.mark.case("TC016")
#     def test_create_product_invalid_image(self, client, create_user, login):
#         """
#         Test Case: TC016

#         Description: Verify product can not be created with invalid image
#         """

#         # Admin account
#         user = create_user()
#         json = login(user.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         invalid_vals = [
#             ".jpg",
#             "image",
#             "image.bmp",
#             "image.gif",
#             "image.jpgg",
#             "imagejpeg",
#             "image.jpeg.png",
#             "image..jpg",
#             "im@ge.jpg",
#             "im#ge.png",
#             "image!.jpeg",
#         ]

#         for val in invalid_vals:
#             payload = {
#                 "name": "product",
#                 "buy_price": "100",
#                 "sell_price": "120",
#                 "image": val,
#             }
#             res = client.post("/api/products/", headers=headers, json=payload)
#             json = res.get_json()

#             assert res.status_code == 400
#             assert json["code"] == 400
#             assert json["status"] == "fail"
#             assert "invalid" in json["errors"].lower()


# @pytest.mark.PRODUCTS
# @pytest.mark.scenario("TS004")
# class TestTS004:
#     """
#     Module: PRODUCTS

#     Test Scenario: TS004

#     Description: Users with valid login credentials along with role able to update new product
#     """

#     @pytest.mark.case("TC001")
#     def test_update_product_without_login(self, client, create_product):
#         """
#         Test Case: TC001

#         Description: Verify without valid login credential no able to update products api
#         """
#         create_product(name="product")
#         payload = {"name": "Product", "buy_price": "100", "sell_price": "110"}
#         res = client.put("/api/products/1", json=payload)
#         json = res.get_json()

#         assert res.status_code == 401
#         assert json["code"] == 401
#         assert json["status"] == "fail"
#         assert "missing " in json["errors"].lower()

#     @pytest.mark.case("TC002")
#     def test_update_product_with_different_roles(self, client, create_user, login, create_product):
#         """
#         Test Case: TC002

#         Description: Verify with only manager, admin roles are allowed for update api
#         """
#         create_product(name="old name")
#         payload = {"name": "new name"}
#         guest = create_user(username="usr1", role="guest")
#         json = login(guest.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.put("/api/products/1", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 403
#         assert json["code"] == 403
#         assert json["status"] == "fail"
#         assert "forbidden" in json["errors"].lower()

#         staff = create_user(username="usr2", role="staff")
#         json = login(staff.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.put("/api/products/1", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 403
#         assert json["code"] == 403
#         assert json["status"] == "fail"

#         manager = create_user(username="usr3", role="manager")
#         json = login(manager.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.put("/api/products/1", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert json["code"] == 200
#         assert json["status"] == "success"
#         assert json["data"]["name"] == "new name"

#         admin = create_user(username="usr4", role="admin")
#         json = login(admin.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         payload = {"buy_price": "500", "sell_price": "600"}
#         res = client.put("/api/products/1", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert json["code"] == 200
#         assert json["status"] == "success"
#         assert json["data"]["buy_price"] == 500.0
#         assert json["data"]["sell_price"] == 600.0

#     @pytest.mark.case("TC003")
#     def test_update_product_with_invalid_id(self, client, create_user, login, create_product):
#         """
#         Test Case: TC003

#         Description: Verify users not able to update product with invalid id
#         """
#         create_product("product")

#         admin = create_user(username="usr4", role="admin")
#         json = login(admin.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         payload = {"buy_price": "500", "sell_price": "600"}
#         res = client.put("/api/products/2", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 404
#         assert json["code"] == 404
#         assert json["status"] == "fail"
#         assert "not found" in json["errors"].lower()

#     @pytest.mark.case("TC004")
#     def test_update_product_duplicate_name(self, client, create_user, login, create_product):
#         """
#         Test Case: TC004

#         Description: Verify users not able to update product with duplicate name
#         """
#         admin = create_user(username="usr4", role="admin")
#         json = login(admin.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         create_product("Product 1")
#         create_product("Product 2")

#         payload = {"name": "Product 2", "buy_price": "100", "sell_price": "120"}
#         res = client.put("/api/products/1", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 409
#         assert json["code"] == 409
#         assert json["status"] == "fail"
#         assert "product name already exists" in json["errors"].lower()

#     @pytest.mark.case("TC005")
#     def test_update_product_invalid_data(self, client, create_user, login, create_product):
#         """
#         Test Case: TC005

#         Description: Verify users not able to update product with invalid data
#         """

#         # Admin account
#         user = create_user()
#         json = login(user.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         create_product("product")
#         payload = {"quantity": "--100"}
#         res = client.put("/api/products/1", headers=headers, json=payload)
#         json = res.get_json()

#         assert res.status_code == 400
#         assert json["code"] == 400
#         assert json["status"] == "fail"
#         assert "invalid" in json["errors"].lower()


# @pytest.mark.PRODUCTS
# @pytest.mark.scenario("TS005")
# class TestTS005:
#     """
#     Module: PRODUCTS

#     Test Scenario: TS005

#     Description: Users with valid login credentials along with role able to delete product
#     """

#     @pytest.mark.case("TC001")
#     def test_delete_product_without_login(self, client, create_product):
#         """
#         Test Case: TC001

#         Description: Verify without valid login credential no able to delete products api
#         """
#         create_product(name="product")
#         res = client.delete("/api/products/1")
#         json = res.get_json()

#         assert res.status_code == 401
#         assert json["code"] == 401
#         assert json["status"] == "fail"
#         assert "missing " in json["errors"].lower()

#     @pytest.mark.case("TC002")
#     def test_delete_product_with_different_roles(self, client, create_user, login, create_product):
#         """
#         Test Case: TC002

#         Description: Verify with only admin are allowed for delete product api
#         """
#         create_product(name="product")
#         guest = create_user(username="usr1", role="guest")
#         json = login(guest.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.delete("/api/products/1", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 403
#         assert json["code"] == 403
#         assert json["status"] == "fail"
#         assert "forbidden" in json["errors"].lower()

#         staff = create_user(username="usr2", role="staff")
#         json = login(staff.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.delete("/api/products/1", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 403
#         assert json["code"] == 403
#         assert json["status"] == "fail"

#         manager = create_user(username="usr3", role="manager")
#         json = login(manager.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.delete("/api/products/1", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 403
#         assert json["code"] == 403
#         assert json["status"] == "fail"

#         admin = create_user(username="usr4", role="admin")
#         json = login(admin.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.delete("/api/products/1", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 200
#         assert json["code"] == 200
#         assert json["status"] == "success"

#     @pytest.mark.case("TC003")
#     def test_delete_product_with_invalid_id(self, client, create_user, login, create_product):
#         """
#         Test Case: TC003

#         Description: Verify users not able to delete product with invalid id
#         """
#         create_product("product")

#         admin = create_user(username="usr4", role="admin")
#         json = login(admin.username, "TestPass123@")
#         headers = {"Authorization": f"Bearer {json["data"]["access_token"]}"}

#         res = client.put("/api/products/2", headers=headers)
#         json = res.get_json()

#         assert res.status_code == 404
#         assert json["code"] == 404
#         assert json["status"] == "fail"
#         assert "not found" in json["errors"].lower()
