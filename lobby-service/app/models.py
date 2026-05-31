from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RoomStatus(str, Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    FINISHED = "finished"


DEFAULT_WINNING_PATTERN = "top_row"


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False, default="BINGO room")
    host_user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=RoomStatus.WAITING.value,
        index=True,
    )
    winning_pattern: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=DEFAULT_WINNING_PATTERN,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    players: Mapped[list["RoomPlayer"]] = relationship(
        back_populates="room",
        cascade="all, delete-orphan",
        order_by="RoomPlayer.joined_at",
    )


class RoomPlayer(Base):
    __tablename__ = "room_players"
    __table_args__ = (
        UniqueConstraint("room_id", "user_id", name="uq_room_players_room_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(80), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    room: Mapped[Room] = relationship(back_populates="players")
