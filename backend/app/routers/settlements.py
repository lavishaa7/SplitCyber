from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Group, User, Settlement
from app.schemas import SettlementCreate, SettlementResponse

router = APIRouter(prefix="/groups/{group_id}/settlements", tags=["Settlements"])

@router.post("", response_model=SettlementResponse, status_code=status.HTTP_201_CREATED)
def create_settlement(group_id: int, settlement_in: SettlementCreate, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    payer = db.query(User).filter(User.id == settlement_in.payer_id).first()
    payee = db.query(User).filter(User.id == settlement_in.payee_id).first()

    if not payer or not payee:
        raise HTTPException(status_code=404, detail="Payer or Payee user not found")

    if settlement_in.payer_id == settlement_in.payee_id:
        raise HTTPException(status_code=400, detail="Payer and Payee cannot be the same user")

    settlement = Settlement(
        group_id=group_id,
        payer_id=settlement_in.payer_id,
        payee_id=settlement_in.payee_id,
        amount=settlement_in.amount,
        notes=settlement_in.notes or "Settlement payment"
    )
    db.add(settlement)
    db.commit()
    db.refresh(settlement)
    return settlement

@router.get("", response_model=List[SettlementResponse])
def list_group_settlements(group_id: int, db: Session = Depends(get_db)):
    return db.query(Settlement).filter(Settlement.group_id == group_id).order_by(Settlement.created_at.desc()).all()
