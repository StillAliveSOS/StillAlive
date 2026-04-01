from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from app.core.config import CHECKIN_INTERVAL_MINUTES, GRACE_PERIOD_MINUTES

class SafetySetting(Base):
    __tablename__ = "safety_setting"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)

    checkin_interval_minutes  = Column(Integer, default=lambda: CHECKIN_INTERVAL_MINUTES)
    grace_period_minutes = Column(Integer, default=lambda: GRACE_PERIOD_MINUTES)
