from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Room, RoomPlayer, RoomStatus


def get_room(db: Session, room_id: int) -> Room | None:
    return db.scalar(
        select(Room)
        .where(Room.id == room_id)
        .options(selectinload(Room.players))
    )


def create_room(db: Session, host_user_id: str) -> Room:
    room = Room(host_user_id=host_user_id, status=RoomStatus.WAITING.value)
    db.add(room)
    db.flush()

    db.add(RoomPlayer(room_id=room.id, user_id=host_user_id))
    db.commit()

    return get_room(db, room.id)


def find_player(db: Session, room_id: int, user_id: str) -> RoomPlayer | None:
    return db.scalar(
        select(RoomPlayer).where(
            RoomPlayer.room_id == room_id,
            RoomPlayer.user_id == user_id,
        )
    )


def add_player(db: Session, room: Room, user_id: str) -> Room:
    if find_player(db, room.id, user_id) is None:
        db.add(RoomPlayer(room_id=room.id, user_id=user_id))
        db.commit()

    return get_room(db, room.id)


def set_room_status(db: Session, room: Room, status: RoomStatus) -> Room:
    room.status = status.value
    db.add(room)
    db.commit()

    return get_room(db, room.id)
