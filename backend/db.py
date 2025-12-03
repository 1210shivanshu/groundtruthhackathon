# backend/db.py



from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from datetime import datetime
import os

# -------------------------
# Database setup
# -------------------------
DB_FILE = os.environ.get("DB_FILE", "backend/users.db")
engine = create_engine(f"sqlite:///{DB_FILE}", echo=False)


# -------------------------
# Models
# -------------------------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, unique=True)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Purchase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    store_name: str
    category: str  # e.g., "Hot Cocoa"
    amount: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# -------------------------
# DB Helper functions
# -------------------------
def init_db():
    """Create DB tables if not exist"""
    SQLModel.metadata.create_all(engine)


def create_user(user_id: str, first_name: str = None, last_name: str = None) -> User:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.user_id == user_id)).first()
        if user:
            return user
        user = User(user_id=user_id, first_name=first_name, last_name=last_name)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def add_purchase(user_id: str, store_name: str, category: str, amount: float = 0.0) -> Purchase:
    with Session(engine) as session:
        purchase = Purchase(user_id=user_id, store_name=store_name, category=category, amount=amount)
        session.add(purchase)
        session.commit()
        session.refresh(purchase)
        return purchase


def get_purchases_for_user(user_id: str, limit: int = 5) -> List[Purchase]:
    with Session(engine) as session:
        stmt = select(Purchase).where(Purchase.user_id == user_id).order_by(Purchase.timestamp.desc()).limit(limit)
        results = session.exec(stmt).all()
        return results
