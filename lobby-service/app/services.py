from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import DEFAULT_WINNING_PATTERN, Room, RoomPlayer, RoomStatus


def get_room(db: Session, room_id: int) -> Room | None:
    return db.scalar(
        select(Room)
        .where(Room.id == room_id)
        .options(selectinload(Room.players))
    )


def list_rooms(db: Session, status: str | None = None) -> list[Room]:
    query = select(Room).options(selectinload(Room.players)).order_by(Room.created_at.desc())
    if status:
        query = query.where(Room.status == status)

    return list(db.scalars(query))


def create_room(
    db: Session,
    host_user_id: str,
    host_display_name: str | None = None,
    name: str | None = None,
    winning_pattern: str = DEFAULT_WINNING_PATTERN,
) -> Room:
    room = Room(
        name=(name or "BINGO room").strip()[:80] or "BINGO room",
        host_user_id=host_user_id,
        status=RoomStatus.WAITING.value,
        winning_pattern=winning_pattern,
    )
    db.add(room)
    db.flush()

    db.add(
        RoomPlayer(
            room_id=room.id,
            user_id=host_user_id,
            display_name=host_display_name or host_user_id,
        )
    )
    db.commit()

    return get_room(db, room.id)


def find_player(db: Session, room_id: int, user_id: str) -> RoomPlayer | None:
    return db.scalar(
        select(RoomPlayer).where(
            RoomPlayer.room_id == room_id,
            RoomPlayer.user_id == user_id,
        )
    )


def add_player(db: Session, room: Room, user_id: str, display_name: str | None = None) -> Room:
    player = find_player(db, room.id, user_id)
    if player is None:
        db.add(
            RoomPlayer(
                room_id=room.id,
                user_id=user_id,
                display_name=display_name or user_id,
            )
        )
        db.commit()
    elif display_name and player.display_name != display_name:
        player.display_name = display_name
        db.add(player)
        db.commit()

    return get_room(db, room.id)


def delete_room(db: Session, room: Room) -> None:
    db.delete(room)
    db.commit()


def set_room_status(db: Session, room: Room, status: RoomStatus) -> Room:
    room.status = status.value
    db.add(room)
    db.commit()

    return get_room(db, room.id)


def start_room(db: Session, room: Room, winning_pattern: str) -> Room:
    room.winning_pattern = winning_pattern
    room.status = RoomStatus.ACTIVE.value
    db.add(room)
    db.commit()

    return get_room(db, room.id)
