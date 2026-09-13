from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import GroupBalanceSummary
from app.services.balance import calculate_group_balances

router = APIRouter(prefix="/groups/{group_id}/balances", tags=["Balances"])

@router.get("", response_model=GroupBalanceSummary)
def get_group_balance_summary(group_id: int, db: Session = Depends(get_db)):
    try:
        return calculate_group_balances(db, group_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
