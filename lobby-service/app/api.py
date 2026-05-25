from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user_id
from app.models import Room, RoomStatus
from app.schemas import PlayerResponse, PlayersResponse, RoomResponse
from app.services import add_player, create_room, get_room, set_room_status

router = APIRouter()


def serialize_room(room: Room) -> RoomResponse:
    return RoomResponse(
        id=room.id,
        host_user_id=room.host_user_id,
        status=room.status,
        players=[
            PlayerResponse(user_id=player.user_id, joined_at=player.joined_at)
            for player in room.players
        ],
        created_at=room.created_at,
        updated_at=room.updated_at,
    )


def load_room_or_404(db: Session, room_id: UUID) -> Room:
    room = get_room(db, str(room_id))
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    return room


@router.post("/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room_endpoint(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> RoomResponse:
    return serialize_room(create_room(db, user_id))


@router.post("/rooms/{room_id}/join", response_model=RoomResponse)
def join_room_endpoint(
    room_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> RoomResponse:
    room = load_room_or_404(db, room_id)

    if room.status != RoomStatus.WAITING.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Players can join only while room is waiting",
        )

    return serialize_room(add_player(db, room, user_id))


@router.get("/rooms/{room_id}", response_model=RoomResponse)
def get_room_endpoint(
    room_id: UUID,
    db: Session = Depends(get_db),
) -> RoomResponse:
    return serialize_room(load_room_or_404(db, room_id))


@router.get("/rooms/{room_id}/players", response_model=PlayersResponse)
def get_room_players_endpoint(
    room_id: UUID,
    db: Session = Depends(get_db),
) -> PlayersResponse:
    room = load_room_or_404(db, room_id)

    return PlayersResponse(
        room_id=room.id,
        players=[
            PlayerResponse(user_id=player.user_id, joined_at=player.joined_at)
            for player in room.players
        ],
    )


@router.post("/rooms/{room_id}/start", response_model=RoomResponse)
def start_room_endpoint(
    room_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> RoomResponse:
    room = load_room_or_404(db, room_id)

    if room.host_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only room host can start the game",
        )

    if room.status != RoomStatus.WAITING.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only waiting room can be started",
        )

    return serialize_room(set_room_status(db, room, RoomStatus.ACTIVE))


@router.post("/rooms/{room_id}/finish", response_model=RoomResponse)
def finish_room_endpoint(
    room_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> RoomResponse:
    room = load_room_or_404(db, room_id)

    if room.host_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only room host can finish the game",
        )

    if room.status != RoomStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only active room can be finished",
        )

    return serialize_room(set_room_status(db, room, RoomStatus.FINISHED))
