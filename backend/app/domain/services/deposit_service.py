from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

from app.models.deposit import Deposit, DepositStatus
from app.models.account import Account
from app.domain.services.transaction_service import TransactionService
from app.schemas.transaction import TransactionCreate
from app.schemas.deposit import DepositCreate, DepositUpdate


class InsufficientFundsError(ValueError):
    pass


class DepositService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_deposits(
        self,
        user_id: int,
        account_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Deposit]:
        """Получить список вкладов"""
        query = self.db.query(Deposit).filter(Deposit.user_id == user_id)
        if account_id:
            query = query.filter(Deposit.account_id == account_id)
        return query.offset(skip).limit(limit).all()
    
    def get_deposit(self, deposit_id: int, user_id: int) -> Optional[Deposit]:
        """Получить вклад по ID"""
        return self.db.query(Deposit).filter(
            Deposit.id == deposit_id,
            Deposit.user_id == user_id
        ).first()
    
    def create_deposit(self, deposit_data: DepositCreate, user_id: int) -> Deposit:
        """Создать новый вклад"""
        if not self._get_account_for_user(deposit_data.account_id, user_id):
            raise ValueError("Account not found")
        self._ensure_sufficient_funds(deposit_data.account_id, Decimal(deposit_data.amount), user_id)
        deposit = Deposit(
            user_id=user_id,
            account_id=deposit_data.account_id,
            name=deposit_data.name,
            amount=deposit_data.amount,
            interest_rate=deposit_data.interest_rate,
            start_date=deposit_data.start_date,
            end_date=deposit_data.end_date,
            status=DepositStatus.ACTIVE
        )
        self.db.add(deposit)
        self._apply_account_balance_on_create(deposit)
        self.db.commit()
        self.db.refresh(deposit)
        return deposit
    
    def update_deposit(self, deposit_id: int, deposit_data: DepositUpdate, user_id: int) -> Optional[Deposit]:
        """Обновить вклад"""
        deposit = self.get_deposit(deposit_id, user_id)
        if not deposit:
            return None

        old_account_id = deposit.account_id
        old_amount = Decimal(deposit.amount)
        old_status = deposit.status

        new_account_id = old_account_id
        new_amount = old_amount
        new_status = old_status

        if deposit_data.amount is not None:
            new_amount = Decimal(deposit_data.amount)
        if deposit_data.status is not None:
            new_status = DepositStatus(deposit_data.status)

        self._ensure_sufficient_funds_for_update(
            old_account_id=old_account_id,
            old_amount=old_amount,
            old_status=old_status,
            new_account_id=new_account_id,
            new_amount=new_amount,
            new_status=new_status,
            user_id=user_id
        )

        update_data = deposit_data.model_dump(exclude_unset=True)
        if "status" in update_data and update_data["status"] is not None:
            update_data["status"] = DepositStatus(update_data["status"])

        if new_status == DepositStatus.COMPLETED and old_status == DepositStatus.ACTIVE:
            update_data.pop("status", None)
            for key, value in update_data.items():
                setattr(deposit, key, value)
            self.db.flush()
            return self.close_deposit(deposit_id, user_id)

        for key, value in update_data.items():
            setattr(deposit, key, value)

        self._apply_account_balance_on_update(
            old_account_id=old_account_id,
            old_amount=old_amount,
            old_status=old_status,
            new_account_id=deposit.account_id,
            new_amount=Decimal(deposit.amount),
            new_status=deposit.status,
            user_id=user_id
        )

        self.db.commit()
        self.db.refresh(deposit)
        return deposit
    
    def delete_deposit(self, deposit_id: int, user_id: int) -> bool:
        """Удалить вклад"""
        deposit = self.get_deposit(deposit_id, user_id)
        if not deposit:
            return False

        self._apply_account_balance_on_delete(deposit)
        self.db.delete(deposit)
        self.db.commit()
        return True
    
    def close_deposit(self, deposit_id: int, user_id: int) -> Optional[Deposit]:
        """Закрыть вклад"""
        deposit = self.get_deposit(deposit_id, user_id)
        if not deposit:
            return None

        if deposit.status == DepositStatus.ACTIVE:
            self._return_deposit_funds(deposit)
            self._create_interest_income(deposit)
        deposit.status = DepositStatus.COMPLETED
        self.db.commit()
        self.db.refresh(deposit)
        return deposit

    def close_overdue_deposits(self) -> int:
        """Автоматически закрыть вклады с истекшим сроком"""
        today = date.today()
        deposits = self.db.query(Deposit).filter(
            Deposit.status == DepositStatus.ACTIVE,
            Deposit.end_date <= today
        ).all()

        closed_count = 0
        for deposit in deposits:
            if not deposit.user_id:
                continue
            if self.close_deposit(deposit.id, deposit.user_id):
                closed_count += 1

        return closed_count

    def _get_account_for_user(self, account_id: int, user_id: int) -> Optional[Account]:
        return self.db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()

    def _ensure_sufficient_funds(self, account_id: int, required_amount: Decimal, user_id: int) -> None:
        if required_amount <= 0:
            return

        account = self._get_account_for_user(account_id, user_id)
        if not account:
            raise InsufficientFundsError("Счет не найден")

        if Decimal(account.balance) < required_amount:
            raise InsufficientFundsError("Недостаточно средств на счете")

    def _ensure_sufficient_funds_for_update(
        self,
        old_account_id: int,
        old_amount: Decimal,
        old_status: DepositStatus,
        new_account_id: int,
        new_amount: Decimal,
        new_status: DepositStatus,
        user_id: int
    ) -> None:
        if old_status != DepositStatus.ACTIVE and new_status != DepositStatus.ACTIVE:
            return

        if old_status == DepositStatus.ACTIVE and new_status != DepositStatus.ACTIVE:
            return

        if old_status != DepositStatus.ACTIVE and new_status == DepositStatus.ACTIVE:
            self._ensure_sufficient_funds(new_account_id, new_amount, user_id)
            return

        if old_account_id == new_account_id:
            delta = new_amount - old_amount
            if delta > 0:
                self._ensure_sufficient_funds(new_account_id, delta, user_id)
            return

        self._ensure_sufficient_funds(new_account_id, new_amount, user_id)

    def _apply_account_balance_on_create(self, deposit: Deposit) -> None:
        if deposit.status != DepositStatus.ACTIVE:
            return
        if not deposit.user_id:
            return

        account = self._get_account_for_user(deposit.account_id, deposit.user_id)
        if not account:
            return

        account.balance = Decimal(account.balance) - Decimal(deposit.amount)

    def _apply_account_balance_on_update(
        self,
        old_account_id: int,
        old_amount: Decimal,
        old_status: DepositStatus,
        new_account_id: int,
        new_amount: Decimal,
        new_status: DepositStatus,
        user_id: int
    ) -> None:
        if old_status != DepositStatus.ACTIVE and new_status != DepositStatus.ACTIVE:
            return

        if old_status == DepositStatus.ACTIVE and new_status != DepositStatus.ACTIVE:
            self._return_amount_to_account(old_account_id, old_amount, user_id)
            return

        if old_status != DepositStatus.ACTIVE and new_status == DepositStatus.ACTIVE:
            self._deduct_amount_from_account(new_account_id, new_amount, user_id)
            return

        if old_account_id == new_account_id:
            delta = new_amount - old_amount
            if delta == 0:
                return
            self._deduct_amount_from_account(new_account_id, delta, user_id)
            return

        self._return_amount_to_account(old_account_id, old_amount, user_id)
        self._deduct_amount_from_account(new_account_id, new_amount, user_id)

    def _apply_account_balance_on_delete(self, deposit: Deposit) -> None:
        if deposit.status != DepositStatus.ACTIVE:
            return

        self._return_deposit_funds(deposit)

    def _return_deposit_funds(self, deposit: Deposit) -> None:
        if not deposit.user_id:
            return
        self._return_amount_to_account(deposit.account_id, Decimal(deposit.amount), deposit.user_id)

    def _return_amount_to_account(self, account_id: int, amount: Decimal, user_id: int) -> None:
        account = self._get_account_for_user(account_id, user_id)
        if not account:
            return

        account.balance = Decimal(account.balance) + amount

    def _deduct_amount_from_account(self, account_id: int, amount: Decimal, user_id: int) -> None:
        if amount == 0:
            return

        account = self._get_account_for_user(account_id, user_id)
        if not account:
            return

        account.balance = Decimal(account.balance) - amount

    def _create_interest_income(self, deposit: Deposit) -> None:
        end_date = min(date.today(), deposit.end_date)
        days = max((end_date - deposit.start_date).days, 0)
        if days == 0:
            return

        interest_rate = Decimal(deposit.interest_rate) / Decimal("100")
        interest_amount = (Decimal(deposit.amount) * interest_rate * Decimal(days) / Decimal("365")).quantize(
            Decimal("0.01")
        )
        if interest_amount <= 0:
            return

        if not deposit.user_id:
            return
        service = TransactionService(self.db)
        service.create_transaction(
            TransactionCreate(
                amount=interest_amount,
                description=f"Проценты по вкладу: {deposit.name}",
                transaction_date=datetime.now(),
                account_id=deposit.account_id,
                transaction_type="income"
            ),
            user_id=deposit.user_id
        )
