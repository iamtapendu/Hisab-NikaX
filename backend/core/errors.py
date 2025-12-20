from pydantic import BaseModel
from typing import Any
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from fastapi import HTTPException


class ErrorResponse(BaseModel):
    success: bool = False
    msg: str
    errors: Any | None = None


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(HTTPException)
    def validation_exception_handler(request: Request, exc: HTTPException):
        if isinstance(exc.detail, dict):
            content = {**exc.detail}
        else:
            content = {"msg": exc.detail, "errors": None}

        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(RequestValidationError)
    def http_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "msg": "Validation failed",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "msg": "Internal server error",
                "errors": str(exc),
            },
        )
