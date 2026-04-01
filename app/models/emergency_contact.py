import uuid
from sqlalchemy import Column, String, ForeignKey ,UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class EmergencyContacts(Base):
    __tablename__ = "emergency_contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    relation = Column(String, nullable=True)

    phones = relationship(
        "ContactPhone",
        back_populates="contact",
        cascade="all, delete-orphan"
    )


class ContactPhone(Base):
    __tablename__ = "contact_phones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("emergency_contacts.id"))

    phone = Column(String, nullable=False)

    contact = relationship("EmergencyContacts", back_populates="phones")
    __table_args__ = (
        UniqueConstraint('contact_id', 'phone', name='unique_contact_phone'),
    )