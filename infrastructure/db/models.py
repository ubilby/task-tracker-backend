from typing import Optional

from sqlalchemy import Integer, String, Boolean, ForeignKey, BIGINT
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DBUser(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    telegram_id: Mapped[Optional[int]] = mapped_column(
        BIGINT, unique=True, index=True, nullable=True
    )
    tasks = relationship("DBTask", back_populates="creator")


class DBTask(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    text: Mapped[str] = mapped_column(String, nullable=False)
    done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    creator = relationship("DBUser", back_populates="tasks")
