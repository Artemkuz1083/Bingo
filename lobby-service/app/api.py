from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import (
    CurrentUser,
    get_current_user,
    get_current_user_id,
    verify_internal_service_token,
)
from app.integrations import draw_game_ball, notify_game_finished, notify_game_started
from app.models import Room, RoomStatus
from app.schemas import PlayerResponse, PlayersResponse, RoomResponse, StartRoomRequest
from app.services import add_player, create_room, get_room, set_room_status, start_room

router = APIRouter()


def serialize_room(room: Room) -> RoomResponse:
    return RoomResponse(
        id=room.id,
        host_user_id=room.host_user_id,
        status=room.status,
        winning_pattern=room.winning_pattern,
        players=[
            PlayerResponse(
                user_id=player.user_id,
                display_name=player.display_name or player.user_id,
                joined_at=player.joined_at,
            )
            for player in room.players
        ],
        created_at=room.created_at,
        updated_at=room.updated_at,
    )


def load_room_or_404(db: Session, room_id: int) -> Room:
    room = get_room(db, room_id)
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    return room


@router.post("/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room_endpoint(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoomResponse:
    return serialize_room(
        create_room(
            db,
            current_user.user_id,
            current_user.display_name,
        )
    )


@router.post("/rooms/{room_id}/join", response_model=RoomResponse)
def join_room_endpoint(
    room_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoomResponse:
    room = load_room_or_404(db, room_id)

    if room.status != RoomStatus.WAITING.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Players can join only while room is waiting",
        )

    return serialize_room(
        add_player(
            db,
            room,
            current_user.user_id,
            current_user.display_name,
        )
    )


@router.get("/rooms/{room_id}", response_model=RoomResponse)
def get_room_endpoint(
    room_id: int,
    db: Session = Depends(get_db),
) -> RoomResponse:
    return serialize_room(load_room_or_404(db, room_id))


@router.get("/rooms/{room_id}/players", response_model=PlayersResponse)
def get_room_players_endpoint(
    room_id: int,
    db: Session = Depends(get_db),
) -> PlayersResponse:
    room = load_room_or_404(db, room_id)

    return PlayersResponse(
        room_id=room.id,
        players=[
            PlayerResponse(
                user_id=player.user_id,
                display_name=player.display_name or player.user_id,
                joined_at=player.joined_at,
            )
            for player in room.players
        ],
    )


@router.post("/rooms/{room_id}/start", response_model=RoomResponse)
def start_room_endpoint(
    room_id: int,
    payload: StartRoomRequest | None = None,
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

    notify_game_started(room)

    winning_pattern = payload.winning_pattern if payload is not None else "top_row"
    return serialize_room(start_room(db, room, winning_pattern))


@router.post("/rooms/{room_id}/draw")
def draw_room_ball_endpoint(
    room_id: int,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> dict:
    room = load_room_or_404(db, room_id)

    if room.host_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only room host can draw balls",
        )

    if room.status != RoomStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only active room can draw balls",
        )

    return draw_game_ball(room)


@router.post("/rooms/{room_id}/finish", response_model=RoomResponse)
def finish_room_endpoint(
    room_id: int,
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

    notify_game_finished(room)

    return serialize_room(set_room_status(db, room, RoomStatus.FINISHED))


@router.post("/internal/rooms/{room_id}/finish", response_model=RoomResponse)
def finish_room_from_service_endpoint(
    room_id: int,
    _: None = Depends(verify_internal_service_token),
    db: Session = Depends(get_db),
) -> RoomResponse:
    room = load_room_or_404(db, room_id)

    if room.status == RoomStatus.FINISHED.value:
        return serialize_room(room)

    if room.status != RoomStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only active room can be finished",
        )

    notify_game_finished(room)

    return serialize_room(set_room_status(db, room, RoomStatus.FINISHED))
