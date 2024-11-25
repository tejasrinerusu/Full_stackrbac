from pydantic import BaseModel


class Token(BaseModel):
    permissions: list[str]
    token: str
