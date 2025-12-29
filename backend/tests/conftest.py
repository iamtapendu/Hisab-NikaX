import pytest
from fastapi import Depends, APIRouter
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import create_application
from database.base import Base
from dependencies.db import get_db
from dependencies.auth import get_current_refresh_token, get_current_user, required_roles
from core.security import create_access_token, create_refresh_token


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    app = create_application()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    router = APIRouter()

    @router.post("/_test/refresh-dep")
    async def _test_refresh_dep(token=Depends(get_current_refresh_token)):
        return token

    @router.post("/_test/current-user-dep")
    async def _test_current_user_dep(token=Depends(get_current_user)):
        return token

    @router.post("/_test/required-roles-dep")
    async def _test_required_role_dep(token=Depends(required_roles("admin"))):
        return token

    app.include_router(router)

    with TestClient(app) as client:
        yield client


@pytest.fixture
def access_token():
    def _access_token(id="1", role="admin"):
        return create_access_token(
            subject=str(id),
            role=role,
        )

    return _access_token


@pytest.fixture
def refresh_token():
    def _refresh_token(id="1", role="admin"):
        return create_refresh_token(
            subject=str(id),
            role=role,
        )

    return _refresh_token


def pytest_itemcollected(item):
    nodeid = item.nodeid.split("::")[-1]
    final_name = ""

    # item.iter_markers() gives only actual markers, avoids bool or list issues.
    for mark in item.iter_markers():
        if mark.name == "scenario":  # <-- Your scenario markers
            final_name = f" {mark.args[0]}" + final_name
        elif mark.name == "case":  # <-- Your TC001 markers
            final_name += f" {mark.args[0]}"
        else:
            final_name = f"{mark.name}" + final_name

    if final_name:
        # Rename test for report
        item._nodeid = f"{final_name}: {nodeid}"
