import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from api.api_v1.api import api_router
from utils.exception import UvicornException


app = FastAPI()


@app.exception_handler(UvicornException)
async def uvicorn_exception_handler(request: Request, exc: UvicornException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message, "error": exc.error},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT")))
