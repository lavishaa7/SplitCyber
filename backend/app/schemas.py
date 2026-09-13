from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

# --- User Schemas ---
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    avatar_color: Optional[str] = "#8B5CF6"

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Group Schemas ---
class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = "General"

class GroupCreate(GroupBase):
    initial_member_ids: Optional[List[int]] = []

class GroupMemberResponse(BaseModel):
    user_id: int
    user: UserResponse
    joined_at: datetime

    class Config:
        from_attributes = True

class GroupResponse(GroupBase):
    id: int
    created_at: datetime
    members: List[GroupMemberResponse] = []

    class Config:
        from_attributes = True

class GroupAddMemberRequest(BaseModel):
    user_id: int


# --- Expense Schemas ---
class ExpenseSplitInput(BaseModel):
    user_id: int
    amount: Optional[float] = None
    percentage: Optional[float] = None

class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    amount: float = Field(..., gt=0)
    paid_by_id: int
    category: Optional[str] = "General"
    split_type: str = Field("EQUAL", pattern="^(EQUAL|EXACT|PERCENTAGE)$")
    splits: Optional[List[ExpenseSplitInput]] = []

class ExpenseSplitResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    amount: float
    percentage: Optional[float] = None

    class Config:
        from_attributes = True

class ExpenseResponse(BaseModel):
    id: int
    group_id: int
    title: str
    amount: float
    category: str
    split_type: str
    created_at: datetime
    paid_by: UserResponse
    splits: List[ExpenseSplitResponse] = []

    class Config:
        from_attributes = True


# --- Settlement Schemas ---
class SettlementCreate(BaseModel):
    payer_id: int
    payee_id: int
    amount: float = Field(..., gt=0)
    notes: Optional[str] = None

class SettlementResponse(BaseModel):
    id: int
    group_id: int
    payer_id: int
    payee_id: int
    payer: Optional[UserResponse] = None
    payee: Optional[UserResponse] = None
    amount: float
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- Balance & Debt Simplification Schemas ---
class UserBalanceDetail(BaseModel):
    user_id: int
    name: str
    email: str
    avatar_color: str
    total_paid: float
    total_share: float
    net_balance: float  # Positive = Owed money (Creditor), Negative = Owes money (Debtor)

class DebtTransaction(BaseModel):
    payer_id: int
    payer_name: str
    payee_id: int
    payee_name: str
    amount: float

class GroupBalanceSummary(BaseModel):
    group_id: int
    group_name: str
    total_group_spending: float
    member_balances: List[UserBalanceDetail]
    simplified_transactions: List[DebtTransaction]
