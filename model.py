from pydantic import BaseModel


class CartoonizeRequest(BaseModel):
    file: str
