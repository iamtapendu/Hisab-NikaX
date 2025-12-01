import pytest
from app import create_app
from extensions import db
from config import TestConfig

@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for tests."""
    app = create_app(TestConfig)
    return app


@pytest.fixture(scope="session")
def db_session(app):
    """Create database tables once per test session."""
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()


@pytest.fixture(scope="function")
def client(app, db_session):
    """Provide a new test client for each test function."""
    with app.test_client() as client:
        yield client
        # Clean DB between tests
        db_session.session.remove()
        for table in reversed(db.metadata.sorted_tables):
            db_session.session.execute(table.delete())
        db_session.session.commit()


def pytest_itemcollected(item):
    nodeid = item.nodeid.split("::")[-1]
    final_name = ""

    # item.iter_markers() gives only actual markers, avoids bool or list issues.
    for mark in item.iter_markers():
        if mark.name == "scenario":      # <-- Your scenario markers
            final_name = f" {mark.args[0]}" + final_name
        elif mark.name == "case":            # <-- Your TC001 markers
            final_name += f" {mark.args[0]}"
        else:
            final_name = f"{mark.name}" + final_name
            
    if final_name:
        # Rename test for report
        item._nodeid = f"{final_name}: {nodeid}"