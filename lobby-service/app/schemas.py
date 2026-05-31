from datetime import datetime
from typing import Literal

from pydantic import BaseModel

WinningPattern = Literal[
    "top_row",
    "middle_row",
    "bottom_row",
    "left_column",
    "middle_column",
    "right_column",
    "main_diagonal",
    "anti_diagonal",
    "four_corners",
    "x_shape",
    "plus_shape",
    "small_frame",
]


class PlayerResponse(BaseModel):
    user_id: str
    display_name: str
    joined_at: datetime


class RoomResponse(BaseModel):
    id: int
    host_user_id: str
    status: str
    winning_pattern: WinningPattern
    players: list[PlayerResponse]
    created_at: datetime
    updated_at: datetime


class StartRoomRequest(BaseModel):
    winning_pattern: WinningPattern = "top_row"


class PlayersResponse(BaseModel):
    room_id: int
    players: list[PlayerResponse]
