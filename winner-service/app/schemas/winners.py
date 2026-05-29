from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


ClaimStatus = Literal[
    "queued",
    "processing",
    "won",
    "rejected",
    "verification_failed",
    "reward_failed",
]


class ClaimResponse(BaseModel):
    claim_id: str
    game_id: str
    user_id: str
    status: ClaimStatus
    reason: str | None = None
    created_at: datetime
    updated_at: datetime


class WinnerResponse(BaseModel):
    game_id: str
    user_id: str
    claim_id: str
    reward_amount: Decimal = Field(ge=0)
    reward_status: Literal["pending", "paid", "failed", "skipped"]
    created_at: datetime


class WinnerClaimMessage(BaseModel):
    claim_id: str
    game_id: str
    user_id: str
    token: str


class CardCell(BaseModel):
    row: int
    col: int
    letter: str
    number: int | None = None
    label: str
    marked: bool = False
    is_free: bool = False


class WinnerCheckData(BaseModel):
    game_id: str
    user_id: str
    rows: list[list[CardCell]]
    columns: list[list[CardCell]]
    diagonals: list[list[CardCell]]
    marked_numbers: list[int] = Field(default_factory=list)


class GameState(BaseModel):
    room_id: str
    status: str | None = None
    last_ball: str | int | None = None
    drawn_balls: list[str | int] = Field(default_factory=list)
