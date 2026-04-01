from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.emergency_contact import EmergencyContacts , ContactPhone
from app.models.user import User
from app.schemas.emergency_contact import (
    EmergencyContactWrappedResponse,
    EmergencyContactBulkCreate,
    EmergencyContactListResponse,
)

router = APIRouter(
    prefix="/emergency-contacts",
    tags=["Emergency Contacts"],
)


@router.post("/", response_model=EmergencyContactWrappedResponse)
def add_contacts(
    data: EmergencyContactBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contacts = []

    for item in data.list_contacts:
        contact = EmergencyContacts(
            user_id=current_user.id,
            name=item.name,
            relation=item.relation,
        )

        db.add(contact)
        db.flush()  

        for phone in item.phone:
            phone_obj = ContactPhone(
                contact_id=contact.id,
                phone=phone
            )
            db.add(phone_obj)

        contacts.append(contact)

    db.commit()

    for c in contacts:
        db.refresh(c)

    return {
        "message": "Contacts added successfully",
        "data": [
            {
                "id": c.id,
                "name": c.name,
                "relation": c.relation,
                "phone": [p.phone for p in c.phones]
            }
            for c in contacts
        ]
    }


@router.get("/", response_model=EmergencyContactListResponse)
def list_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contacts = (
        db.query(EmergencyContacts)
        .filter(EmergencyContacts.user_id == current_user.id)
        .all()
    )

    return {
        "message": "Contact retrieved successfully",
        "data": [
            {
                "id": c.id,
                "name": c.name,
                "relation": c.relation,
                "phone": [p.phone for p in c.phones]
            }
            for c in contacts
        ],
    }

@router.delete("/{contact_id}")
def delete_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    contact = (
        db.query(EmergencyContacts)
        .filter(
            EmergencyContacts.id == contact_id,
            EmergencyContacts.user_id == current_user.id,
        )
        .first()
    )

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()

    return {"message": "Contact deleted successfully"}