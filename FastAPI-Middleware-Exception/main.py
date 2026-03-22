from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print("Before Request is processed")
        print(f"Method: {request.method}")
        print(f"Path: {request.url.path}")

        response = await call_next(request)

        print("After Response is returned")

        return response


app.add_middleware(LoggingMiddleware)

@app.get("/hello")
async def hello():
    return {
        "message": "Hello, Welcome to FastAPI!"
    }


@app.exception_handler(StarletteHTTPException)
async def custom_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={
                "message": "The requested resource was not found"
            }
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail)}
    )