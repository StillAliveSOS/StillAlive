from sqlalchemy import Column, String, Date,DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    phone = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    dob = Column(Date, nullable=True)
    address = Column(String, nullable=True)
    fcm_token = Column(String, nullable=True)
    
        
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    @property
    def is_partial_completed(self):
        return bool(self.phone and self.email)

    @property
    def is_fully_completed(self):
        return all([
            self.name,
            self.phone,
            self.email,
            self.dob,
            self.address
        ])