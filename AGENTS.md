# Project Context

This is an educational Bingo project built as a set of microservices plus a simple frontend.

## Services

- `auth-service` - registration, login, password hashing, JWT issuing.
- `user-service` - user profile and user-related data.
- `lobby-service` - rooms, room players, and room/game status.
- `card-service` - Bingo cards for players.
- `game-engine-service` - Bingo ball generation and game state.
- `winner-service` - winner validation flow.
- `frontend` - static HTML/CSS/JS pages.

## Shared Contracts

- `auth-service` issues JWT tokens.
- User id is stored in the JWT `sub` claim.
- Protected service requests should use `Authorization: Bearer <token>`.
- `lobby-service` owns room status transitions: `waiting`, `active`, `finished`.
- Other services can react to game events, but they should not directly own lobby room status.
- `room_id` can be used as `game_id` unless the project later introduces a separate game id.
- Temporary local/manual testing may still use `X-User-Id` where a service supports it, but JWT is the primary contract.

## Ports

- `auth-service`: `8001`
- `user-service`: `8002`
- `lobby-service`: `8003`
- RabbitMQ: `5672`, management UI `15672`

## Databases

- `auth-service` uses PostgreSQL database `bingo_auth`.
- `user-service` uses PostgreSQL database `bingo_users`.
- `lobby-service` uses PostgreSQL database `bingo_lobby`.
- Redis is used by `card-service` and `game-engine-service` where implemented.

## Lobby Service Notes

`lobby-service` currently:

- creates rooms;
- adds the host as the first player;
- lets players join waiting rooms;
- returns room and player lists;
- lets only the host start an active game;
- lets only the host finish an active game;
- reads JWT `sub` through `Authorization: Bearer <token>`;
- still supports `X-User-Id` as a temporary fallback.

Run tests:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& c:\dev\ucheba\Bingo\lobby-service\.venv\Scripts\Activate.ps1
pytest
```

## Development Rules

- Check existing code and README/TODO files before changing a service.
- Keep changes scoped to the requested service unless a shared contract or compose setup must change.
- Do not overwrite unrelated work in other services.
- If a service-to-service contract changes, update the related README/TODO notes.
- Prefer matching the simple style already used in this project over introducing new frameworks or heavy abstractions.
