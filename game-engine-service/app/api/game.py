from fastapi import APIRouter, HTTPException

from app.engine import engine
from app.schemas.schemas import GameStateResponse, BallResponse, MessageResponse, StartGameRequest

router = APIRouter()

@router.post("/{room_id}/start", response_model=MessageResponse, status_code=201)
async def start_game(room_id: str, body: StartGameRequest):
    started = await engine.start_game(room_id, body.player_user_ids)
    if not started:
        raise HTTPException(status_code=409, detail="Game is already running for this room")
    return {"message": f"Game started for room {room_id}"}

@router.post("/{room_id}/stop", response_model=MessageResponse)
async def stop_game(room_id: str):
    stopped = await engine.stop_game(room_id)
    if not stopped:
        raise HTTPException(status_code=404, detail="No active game found for this room")
    return {"message": f"Stop signal sent for room {room_id}"}


@router.get("/{room_id}/state", response_model=GameStateResponse)
async def get_state(room_id: str):
    return await engine.get_state(room_id)

@router.get("/{room_id}/last", response_model=BallResponse | None)
async def get_last_ball(room_id: str):
    state = await engine.get_state(room_id)
    if state["last_ball"] is None:
        raise HTTPException(status_code=404, detail="No balls drawn yet")
    return state["last_ball"]