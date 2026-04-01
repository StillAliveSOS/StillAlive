from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.waitlist_schema import WaitlistCreate
from app.models.waitlist_models import Waitlist
from app.core.dependencies import get_db

router = APIRouter(prefix="/waitlist", tags=["Waitlist"])

@router.post("/join")
def join_waitlist(payload: WaitlistCreate, db: Session = Depends(get_db)):

    existing = db.query(Waitlist).filter(
        (Waitlist.email == payload.email) |
        (Waitlist.phone_number == payload.phone_number)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already registered")

    new_user = Waitlist(
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        email=payload.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Successfully joined waitlist",
        "id": new_user.id
    }