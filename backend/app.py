from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logging import configure_logging

# from app.modules.auth.router import router as auth_router
# from app.modules.users.router import router as users_router
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

    # -------------------------
    # API Routers
    # -------------------------
    # app.include_router(
    #     auth_router,
    #     prefix=f"{settings.API_PREFIX}/auth",
    #     tags=["Auth"],
    # )

    # app.include_router(
    #     users_router,
    #     prefix=f"{settings.API_PREFIX}/users",
    #     tags=["Users"],
    # )

    # app.include_router(
    #     inventory_router,
    #     prefix=f"{settings.API_PREFIX}/inventory",
    #     tags=["Inventory"],
    # )

    # app.include_router(
    #     sales_router,
    #     prefix=f"{settings.API_PREFIX}/sales",
    #     tags=["Sales"],
    # )

    return app


app = create_application()
