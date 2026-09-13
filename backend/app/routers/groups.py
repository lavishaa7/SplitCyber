from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Group, GroupMember, User
from app.schemas import GroupCreate, GroupResponse, GroupAddMemberRequest

router = APIRouter(prefix="/groups", tags=["Groups"])

@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(group_in: GroupCreate, db: Session = Depends(get_db)):
    group = Group(
        name=group_in.name,
        description=group_in.description,
        category=group_in.category or "General"
    )
    db.add(group)
    db.flush()

    # Add initial members if provided
    if group_in.initial_member_ids:
        for u_id in set(group_in.initial_member_ids):
            user = db.query(User).filter(User.id == u_id).first()
            if user:
                member = GroupMember(group_id=group.id, user_id=u_id)
                db.add(member)

    db.commit()
    db.refresh(group)
    return group

@router.get("", response_model=List[GroupResponse])
def list_groups(db: Session = Depends(get_db)):
    return db.query(Group).order_by(Group.created_at.desc()).all()

@router.get("/{group_id}", response_model=GroupResponse)
def get_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.post("/{group_id}/members", status_code=status.HTTP_201_CREATED)
def add_group_member(group_id: int, req: GroupAddMemberRequest, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == req.user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member of this group")

    member = GroupMember(group_id=group_id, user_id=req.user_id)
    db.add(member)
    db.commit()
    return {"message": f"Added user {user.name} to group {group.name}"}

@router.delete("/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_group_member(group_id: int, user_id: int, db: Session = Depends(get_db)):
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found in group")

    db.delete(member)
    db.commit()
    return None
