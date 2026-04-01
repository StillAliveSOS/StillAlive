import random
from uuid import UUID
from fastapi import APIRouter, Depends,Header, HTTPException
from sqlalchemy.orm import Session
from fastapi import Body
from app.core.dependencies import get_current_user
from app.models.refresh_token import RefreshToken
from app.core.database import get_db
from app.models.user import User
from app.models.otp import OTPRequest
from app.schemas.auth import OTPVerifyIn, OTPRequestIn, TokenOut
from app.services.phone_verification import verify_phone_number
from datetime import datetime
import secrets
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/request_otp")
def request_otp(data: OTPRequestIn, db: Session = Depends(get_db)):

    verify_phone_number(data.phone)

    otp = str(secrets.randbelow(900000) + 100000)

    record = db.query(OTPRequest).filter(
        OTPRequest.phone == data.phone
    ).first()

    if record:
        record.otp = otp
        record.expires_at = OTPRequest.expiry_time()
        record.verified = False
    else:
        record = OTPRequest(
            phone=data.phone,
            otp=otp,
            expires_at=OTPRequest.expiry_time(),
        )
        db.add(record)

    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        user = User(phone=data.phone)
        db.add(user)

    db.commit()

    return {"message": "OTP sent", "otp": otp, "user_id": str(user.id)}


@router.post("/verify_otp", response_model=TokenOut)
def verify_otp(data: OTPVerifyIn, db: Session = Depends(get_db)):

    record = (
        db.query(OTPRequest)
        .filter(
            OTPRequest.phone == data.phone,
            OTPRequest.otp == data.otp,
            OTPRequest.verified == False,
        )
        .first()
    )

    if not record or record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    record.verified = True

    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        return {"exist": 0}  # or raise HTTPException for security
    
    if data.fcm_token:
        user.fcm_token = data.fcm_token

    access_token = create_access_token(
        subject=user.phone,
        user_id=user.id,
    )

    refresh_token = create_refresh_token(
        subject=user.phone,
        user_id=user.id,
    )

    db_refresh = RefreshToken(
        token=refresh_token,
        user_id=user.id if isinstance(user.id, UUID) else UUID(str(user.id)),
    )

    db.add(db_refresh)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "exist":1
    }


@router.post("/refresh")
def refresh_access_token(
    refresh_token: str = Body(...),
    db: Session = Depends(get_db)
):

    payload = decode_access_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    token_in_db = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token
    ).first()

    if not token_in_db:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    new_access_token = create_access_token(
        subject=payload["sub"],
        user_id=UUID(payload["user_id"])
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


@router.get("/status")
def user_status(current_user = Depends(get_current_user)):
    if current_user:
        return {"status": "StillAlive"}
    return {"status": "NOT StillAlive"}

@router.post("/logout")
def logout(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    refresh_token: str = Header(...)
):
    deleted = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.token == refresh_token
    ).delete()
    current_user.device_token = None
    db.commit()

    if not deleted:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"message": "Logged out successfully"}


