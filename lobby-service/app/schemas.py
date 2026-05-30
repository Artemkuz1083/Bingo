from datetime import datetime

from pydantic import BaseModel


class PlayerResponse(BaseModel):
    user_id: str
    joined_at: datetime


class RoomResponse(BaseModel):
    id: int
    host_user_id: str
    status: str
    players: list[PlayerResponse]
    created_at: datetime
    updated_at: datetime


class PlayersResponse(BaseModel):
    room_id: int
    players: list[PlayerResponse]
