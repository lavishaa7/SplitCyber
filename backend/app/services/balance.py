from typing import List, Dict
from sqlalchemy.orm import Session
from app.models import Group, Expense, ExpenseSplit, Settlement, GroupMember, User
from app.schemas import UserBalanceDetail, DebtTransaction, GroupBalanceSummary

def calculate_group_balances(db: Session, group_id: int) -> GroupBalanceSummary:
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise ValueError("Group not found")

    # Get all members in the group
    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    user_map: Dict[int, User] = {}
    for m in members:
        user_map[m.user_id] = m.user

    # Data structures for tracking spending and shares
    user_paid: Dict[int, float] = {u_id: 0.0 for u_id in user_map}
    user_share: Dict[int, float] = {u_id: 0.0 for u_id in user_map}
    settlements_paid: Dict[int, float] = {u_id: 0.0 for u_id in user_map}
    settlements_received: Dict[int, float] = {u_id: 0.0 for u_id in user_map}

    # Fetch expenses for the group
    expenses = db.query(Expense).filter(Expense.group_id == group_id).all()
    total_group_spending = 0.0

    for exp in expenses:
        total_group_spending += exp.amount
        if exp.paid_by_id in user_paid:
            user_paid[exp.paid_by_id] += exp.amount
        else:
            user_paid[exp.paid_by_id] = exp.amount

        # Process splits
        for split in exp.splits:
            if split.user_id in user_share:
                user_share[split.user_id] += split.amount
            else:
                user_share[split.user_id] = split.amount

    # Fetch settlements for the group
    settlements = db.query(Settlement).filter(Settlement.group_id == group_id).all()
    for st in settlements:
        if st.payer_id in settlements_paid:
            settlements_paid[st.payer_id] += st.amount
        if st.payee_id in settlements_received:
            settlements_received[st.payee_id] += st.amount

    # Compute net balance for each member
    member_balances: List[UserBalanceDetail] = []
    net_balances: Dict[int, float] = {}

    for u_id, user in user_map.items():
        paid = user_paid.get(u_id, 0.0)
        share = user_share.get(u_id, 0.0)
        set_paid = settlements_paid.get(u_id, 0.0)
        set_rec = settlements_received.get(u_id, 0.0)

        # Net balance calculation formula
        net = (paid + set_paid) - (share + set_rec)
        net_balances[u_id] = round(net, 2)

        member_balances.append(UserBalanceDetail(
            user_id=u_id,
            name=user.name,
            email=user.email,
            avatar_color=user.avatar_color or "#8B5CF6",
            total_paid=round(paid, 2),
            total_share=round(share, 2),
            net_balance=round(net, 2)
        ))

    # Min-Cash-Flow algorithm to simplify debts
    simplified_transactions = simplify_debts(net_balances, user_map)

    return GroupBalanceSummary(
        group_id=group.id,
        group_name=group.name,
        total_group_spending=round(total_group_spending, 2),
        member_balances=member_balances,
        simplified_transactions=simplified_transactions
    )


def simplify_debts(net_balances: Dict[int, float], user_map: Dict[int, User]) -> List[DebtTransaction]:
    """
    Min-Cash-Flow greedy algorithm to calculate minimum required transfers
    to settle all group debts.
    """
    # Separate into debtors (net < 0) and creditors (net > 0)
    debtors = []   # list of [user_id, debt_amount]
    creditors = [] # list of [user_id, credit_amount]

    for u_id, net in net_balances.items():
        if net < -0.01:
            debtors.append([u_id, abs(net)])
        elif net > 0.01:
            creditors.append([u_id, net])

    transactions: List[DebtTransaction] = []

    # Sort to prioritize settling largest debts with largest credits first
    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)

    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor_id, debt_amt = debtors[i]
        creditor_id, cred_amt = creditors[j]

        settle_amt = round(min(debt_amt, cred_amt), 2)
        if settle_amt > 0.009:
            payer_user = user_map.get(debtor_id)
            payee_user = user_map.get(creditor_id)

            payer_name = payer_user.name if payer_user else f"User #{debtor_id}"
            payee_name = payee_user.name if payee_user else f"User #{creditor_id}"

            transactions.append(DebtTransaction(
                payer_id=debtor_id,
                payer_name=payer_name,
                payee_id=creditor_id,
                payee_name=payee_name,
                amount=settle_amt
            ))

        debtors[i][1] -= settle_amt
        creditors[j][1] -= settle_amt

        if debtors[i][1] <= 0.01:
            i += 1
        if creditors[j][1] <= 0.01:
            j += 1

    return transactions
