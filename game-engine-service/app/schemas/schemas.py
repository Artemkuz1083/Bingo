from pydantic import BaseModel

class MessageResponse(BaseModel):
    message: str

class StartGameRequest(BaseModel):
    room_id: str
    player_user_ids: list[str]

class BallResponse(BaseModel):
    label: str
    letter: str
    number: int


class DrawnBallResponse(BallResponse):
    order: int

class GameStateResponse(BaseModel):
    room_id: str
    is_active: bool
    started_at: int | None
    drawn_count: int
    remaining_count: int
    last_ball: BallResponse | None
    drawn_balls: list[DrawnBallResponse]
    player_user_ids: list[str]
