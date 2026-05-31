# Lobby Service

ЭТО МОЁ ПРИМЕРНОЕ ПРЕДСТАВЛЕНИЕ АРХИТЕКТУРЫ

Исполнитель по ТЗ: Артем С.

Суть микросервиса: управление комнатами, участниками игры и статусом комнаты.

Нужно реализовать микросервис, который будет создавать игровые комнаты, добавлять игроков в комнату, хранить список участников и управлять статусом игры: `waiting`, `active`, `finished`.

Сервис получает `user_id` из JWT, который выдает `auth-service`. Идентификатор пользователя хранится в claim `sub`, а отображаемое имя игрока берется из claim `username` или заголовка `X-User-Name`.

Для ручного тестирования временно поддерживается заголовок `X-User-Id`, но основной вариант для frontend и других сервисов - `Authorization: Bearer <token>`.

Основные задачи:

- создание комнаты;
- присоединение игрока к комнате;
- получение списка игроков;
- запуск игры только хостом;
- ручная выдача следующего шара только хостом;
- изменение статуса комнаты;
- хранение данных о комнатах и игроках в PostgreSQL.

Именно этот сервис является владельцем статуса комнаты и игры. Остальные сервисы могут запрашивать статус или сообщать о событиях, но финальное изменение `waiting`, `active`, `finished` должно проходить через `lobby-service`.

## Запуск

В общем `docker-compose.yml` сервис доступен как `lobby-service` на порту `8003`. При старте контейнер сам создает таблицы в своей PostgreSQL, если `AUTO_CREATE_TABLES=true`.

Локально:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& c:\dev\ucheba\Bingo\lobby-service\.venv\Scripts\Activate.ps1
pytest
```

## Integration endpoints

- `POST /rooms` accepts optional JSON `{ "name": string, "winning_pattern": string }` and returns the created room with the host already added as first player.
- `GET /rooms?status_filter=waiting` returns rooms that can still be joined; the frontend uses this for the lobby room browser.
- `DELETE /rooms/{room_id}` lets the host close a waiting room; players should return to the room browser after the room disappears.
- On `POST /rooms/{room_id}/start`, `lobby-service` changes ownership state only after calling `POST {LOBBY_GAME_ENGINE_SERVICE_URL}/game/{room_id}/start` when `LOBBY_GAME_ENGINE_SERVICE_URL` is configured.
- The game engine payload contains `room_id` and `player_user_ids`.
- `POST /rooms/{room_id}/draw` is available only to the room host while the room is `active`; it calls `POST {LOBBY_GAME_ENGINE_SERVICE_URL}/game/{room_id}/draw`.
- `POST /internal/rooms/{room_id}/finish` lets another trusted service, for example `winner-service`, finish an active room.
- Internal requests must include `X-Internal-Service-Token` matching `INTERNAL_SERVICE_TOKEN`.
