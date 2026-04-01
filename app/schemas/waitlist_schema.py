from pydantic import BaseModel, EmailStr, constr

class WaitlistCreate(BaseModel):
    full_name: constr(min_length=2, max_length=100)
    phone_number: constr(min_length=10, max_length=15)
    email: EmailStr