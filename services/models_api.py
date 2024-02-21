from pydantic import BaseModel
# Pydantic models
class UserCreate(BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str

class Login(BaseModel):
    email: str
    password: str