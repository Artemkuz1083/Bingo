# TODO для связи lobby-service с остальными сервисами

Это не срочные задачи для моей части, а список того, что надо будет доделать,
когда остальные сервисы будут готовы.

## auth-service

- JWT уже появился в `auth-service`.
- `user_id` лежит в claim `sub`.
- Отображаемое имя игрока берется из JWT claim `username`, а для старых токенов может временно прийти в `X-User-Name`.
- `lobby-service` уже умеет читать `Authorization: Bearer <token>`.
- Заголовок `X-User-Id` оставлен только как временный fallback для ручного тестирования, пока frontend полностью не перейдет на JWT.

## game-engine-service

- Когда хост запускает игру через `POST /rooms/{room_id}/start`, `lobby-service` сообщает об этом в `game-engine-service`.
- Шары больше не выпадают по таймеру: хост достает следующий шар через `POST /rooms/{room_id}/draw`, а `lobby-service` проксирует это в `game-engine-service`.
- Статус комнаты все равно должен менять только `lobby-service`, а не `game-engine-service`.

## card-service

- Надо договориться, когда создавать карточки игрокам: сразу при входе в комнату или когда хост запускает игру.
- Для связи можно использовать `room_id` как `game_id`, если потом не решим сделать отдельный id игры.
- `card-service` должен будет получать `user_id` игрока и `room_id`.

## winner-service

- Когда `winner-service` подтвердит победителя, он должен сообщить в `lobby-service`, что игру надо завершить.
- Для этого потом нужен отдельный запрос или внутренний endpoint, который переведет комнату в `finished`.
- Надо будет решить, как проверять, что такой запрос пришел именно от `winner-service`, а не от обычного игрока.

## frontend

- Подключить кнопки создания комнаты, входа в комнату, списка игроков и старта игры к endpoint-ам `lobby-service`.
- Пока для теста можно передавать `X-User-Id`.
- Когда появится авторизация, заменить это на `Authorization: Bearer <token>`.

## запуск проекта

- Общий `docker-compose.yml` уже появился.
- `lobby-service` подключен к compose с отдельной PostgreSQL `bingo_lobby`.
- Переменные для lobby: `DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `CORS_ORIGINS`, `LOBBY_GAME_ENGINE_SERVICE_URL`, `HTTP_TIMEOUT_SECONDS`, `INTERNAL_SERVICE_TOKEN`.

## Current integration contract

- When a host starts a room, `lobby-service` can notify game engine with `POST {LOBBY_GAME_ENGINE_SERVICE_URL}/game/{room_id}/start`.
- The notification payload is `room_id` and `player_user_ids`.
- When a host draws a ball, `lobby-service` calls `POST {LOBBY_GAME_ENGINE_SERVICE_URL}/game/{room_id}/draw`.
- `winner-service` can finish an active room with `POST /internal/rooms/{room_id}/finish`.
- This internal endpoint requires `X-Internal-Service-Token: <INTERNAL_SERVICE_TOKEN>`.
