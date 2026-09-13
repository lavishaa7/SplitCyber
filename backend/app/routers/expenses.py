from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Group, GroupMember, Expense, ExpenseSplit, User
from app.schemas import ExpenseCreate, ExpenseResponse

router = APIRouter(prefix="/groups/{group_id}/expenses", tags=["Expenses"])

@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(group_id: int, expense_in: ExpenseCreate, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    payer = db.query(User).filter(User.id == expense_in.paid_by_id).first()
    if not payer:
        raise HTTPException(status_code=404, detail="Payer user not found")

    # Get group member IDs
    group_members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    member_ids = [m.user_id for m in group_members]
    if not member_ids:
        raise HTTPException(status_code=400, detail="Group has no members to split expenses with")

    if expense_in.paid_by_id not in member_ids:
        # Auto-add payer to group if not already a member
        db.add(GroupMember(group_id=group_id, user_id=expense_in.paid_by_id))
        member_ids.append(expense_in.paid_by_id)

    # Process Splits according to split_type
    calculated_splits = []

    if expense_in.split_type == "EQUAL":
        # Target users: specified splits users or all group members
        target_user_ids = [s.user_id for s in expense_in.splits] if expense_in.splits else member_ids
        target_user_ids = list(set(target_user_ids))
        if not target_user_ids:
            target_user_ids = member_ids

        per_user_amount = round(expense_in.amount / len(target_user_ids), 2)
        # Fix rounding difference on last item
        diff = round(expense_in.amount - (per_user_amount * len(target_user_ids)), 2)

        for idx, u_id in enumerate(target_user_ids):
            split_amt = per_user_amount + (diff if idx == 0 else 0.0)
            calculated_splits.append({
                "user_id": u_id,
                "amount": split_amt,
                "percentage": round((split_amt / expense_in.amount) * 100, 2)
            })

    elif expense_in.split_type == "EXACT":
        if not expense_in.splits:
            raise HTTPException(status_code=400, detail="Exact split amounts must be provided for members")
        
        total_exact = sum(s.amount or 0.0 for s in expense_in.splits)
        if abs(total_exact - expense_in.amount) > 0.05:
            raise HTTPException(
                status_code=400,
                detail=f"Sum of split amounts (${total_exact:.2f}) does not match expense total (${expense_in.amount:.2f})"
            )

        for s in expense_in.splits:
            amt = s.amount or 0.0
            calculated_splits.append({
                "user_id": s.user_id,
                "amount": round(amt, 2),
                "percentage": round((amt / expense_in.amount) * 100, 2)
            })

    elif expense_in.split_type == "PERCENTAGE":
        if not expense_in.splits:
            raise HTTPException(status_code=400, detail="Percentage split values must be provided for members")

        total_pct = sum(s.percentage or 0.0 for s in expense_in.splits)
        if abs(total_pct - 100.0) > 0.1:
            raise HTTPException(
                status_code=400,
                detail=f"Sum of split percentages ({total_pct:.1f}%) must equal 100%"
            )

        for s in expense_in.splits:
            pct = s.percentage or 0.0
            amt = round((pct / 100.0) * expense_in.amount, 2)
            calculated_splits.append({
                "user_id": s.user_id,
                "amount": amt,
                "percentage": round(pct, 2)
            })

    # Save Expense
    expense = Expense(
        group_id=group_id,
        paid_by_id=expense_in.paid_by_id,
        title=expense_in.title,
        amount=expense_in.amount,
        category=expense_in.category or "General",
        split_type=expense_in.split_type
    )
    db.add(expense)
    db.flush()

    # Save Splits
    for cs in calculated_splits:
        split_entry = ExpenseSplit(
            expense_id=expense.id,
            user_id=cs["user_id"],
            amount=cs["amount"],
            percentage=cs["percentage"]
        )
        db.add(split_entry)

    db.commit()
    db.refresh(expense)

    # Format response with user names
    return format_expense_response(expense, db)


@router.get("", response_model=List[ExpenseResponse])
def list_group_expenses(group_id: int, db: Session = Depends(get_db)):
    expenses = db.query(Expense).filter(Expense.group_id == group_id).order_by(Expense.created_at.desc()).all()
    return [format_expense_response(exp, db) for exp in expenses]


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return None


def format_expense_response(expense: Expense, db: Session) -> ExpenseResponse:
    splits_res = []
    for s in expense.splits:
        user = db.query(User).filter(User.id == s.user_id).first()
        splits_res.append({
            "id": s.id,
            "user_id": s.user_id,
            "user_name": user.name if user else f"User #{s.user_id}",
            "amount": s.amount,
            "percentage": s.percentage
        })

    return ExpenseResponse(
        id=expense.id,
        group_id=expense.group_id,
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        split_type=expense.split_type,
        created_at=expense.created_at,
        paid_by=expense.paid_by,
        splits=splits_res
    )
