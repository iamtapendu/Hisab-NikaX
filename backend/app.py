from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.logging import configure_logging
from core.common import register_exception_handlers

from database.base import Base
from database.session import engine

from modules.auth.routes import router as auth_router
from modules.users.routes import router as users_router
from modules.products.routes import router as product_router

# from app.modules.inventory.router import router as inventory_router
# from app.modules.sales.router import router as sales_router


def create_application() -> FastAPI:
    """
    Application factory for FastAPI.

    Creates and configures the FastAPI application instance,
    including middleware, routers, and startup/shutdown events.
    """

    configure_logging()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        summary=settings.SUMMARY,
        description=settings.DESCRIPTION,
        contact=settings.CONTACT,
        license_info=settings.LICENCE,
        version=settings.VERSION,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
    )

    # CORS (React / Frontend)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom errors
    register_exception_handlers(app)

    # API Routers
    app.include_router(auth_router, prefix=f"{settings.API_PREFIX}/auth")
    app.include_router(users_router, prefix=f"{settings.API_PREFIX}/users")
    app.include_router(product_router, prefix=f"{settings.API_PREFIX}/products")

    return app


app = create_application()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables (only for dev or testing)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.clear()
