from pydantic import BaseModel
from typing import Any, TypeVar, List, Generic
from fastapi import FastAPI, Request
from fastapi.exceptions import ResponseValidationError, RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from fastapi import HTTPException


T = TypeVar("T")


class PaginationMeta(BaseModel):
    """
    For holding pagination data
    """

    page: int
    per_page: int
    total: int
    pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta


class ErrorResponse(BaseModel):
    """
    Schema for ErrorResponse
    """

    msg: str
    errors: Any | None = None


def register_exception_handlers(app: FastAPI) -> None:
    """
    Used for registering custom exception handlers.
    """

    @app.exception_handler(HTTPException)
    def http_exception_handler(request: Request, exc: HTTPException):
        if isinstance(exc.detail, dict):
            content = {**exc.detail}
        else:
            content = {"msg": exc.detail, "errors": None}

        return JSONResponse(status_code=exc.status_code, content=content)
    
    @app.exception_handler(RequestValidationError)
    def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "msg": "Validation failed",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(ResponseValidationError)
    def response_validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "msg": "Validation failed",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "msg": "Internal server error",
                "errors": str(exc),
            },
        )
