from typing import Literal

from pydantic import BaseModel, Field


BingoLetter = Literal["B", "I", "N", "G", "O"]


class CardPreviewRequest(BaseModel):
    game_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)


class CardCell(BaseModel):
    row: int = Field(ge=0, le=4)
    col: int = Field(ge=0, le=4)
    letter: BingoLetter
    number: int | None = Field(default=None, ge=1, le=75)
    label: str
    marked: bool = False
    is_free: bool = False


class CardResponse(BaseModel):
    game_id: str
    user_id: str
    cells: list[list[CardCell]]
