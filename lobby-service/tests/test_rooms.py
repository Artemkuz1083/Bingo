from jose import jwt


def auth_headers(user_id="host", username=None):
    payload = {"sub": user_id}
    if username:
        payload["username"] = username
    token = jwt.encode(payload, "change-me", algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


def create_room(client, user_id="host"):
    response = client.post("/rooms", headers=auth_headers(user_id))
    assert response.status_code == 201
    return response.json()


def test_create_room_adds_host_as_player(client):
    response = client.post("/rooms", headers=auth_headers("1", "host-name"))
    assert response.status_code == 201
    room = response.json()

    assert room["host_user_id"] == "1"
    assert room["status"] == "waiting"
    assert room["winning_pattern"] == "top_row"
    assert [player["display_name"] for player in room["players"]] == ["host-name"]


def test_join_room_is_idempotent(client):
    room = create_room(client)

    first = client.post(
        f"/rooms/{room['id']}/join",
        headers=auth_headers("player"),
    )
    second = client.post(
        f"/rooms/{room['id']}/join",
        headers=auth_headers("player"),
    )

    assert first.status_code == 200
    assert second.status_code == 200
    players = second.json()["players"]
    assert [player["user_id"] for player in players] == ["host", "player"]
    assert [player["display_name"] for player in players] == ["host", "player"]


def test_get_room_players(client):
    room = create_room(client)
    client.post(f"/rooms/{room['id']}/join", headers=auth_headers("player"))

    response = client.get(f"/rooms/{room['id']}/players")

    assert response.status_code == 200
    assert response.json()["room_id"] == room["id"]
    assert [player["user_id"] for player in response.json()["players"]] == [
        "host",
        "player",
    ]


def test_only_host_can_start_room(client):
    room = create_room(client)

    response = client.post(
        f"/rooms/{room['id']}/start",
        headers=auth_headers("player"),
    )

    assert response.status_code == 403


def test_room_status_flow(client):
    room = create_room(client)

    started = client.post(
        f"/rooms/{room['id']}/start",
        headers=auth_headers("host"),
        json={"winning_pattern": "main_diagonal"},
    )
    finished = client.post(
        f"/rooms/{room['id']}/finish",
        headers=auth_headers("host"),
    )

    assert started.status_code == 200
    assert started.json()["status"] == "active"
    assert started.json()["winning_pattern"] == "main_diagonal"
    assert finished.status_code == 200
    assert finished.json()["status"] == "finished"


def test_start_room_rejects_unknown_winning_pattern(client):
    room = create_room(client)

    response = client.post(
        f"/rooms/{room['id']}/start",
        headers=auth_headers("host"),
        json={"winning_pattern": "unknown"},
    )

    assert response.status_code == 422


def test_start_room_notifies_game_engine(client, monkeypatch):
    room = create_room(client)
    notified_room_ids = []

    def fake_notify_game_started(room_model):
        notified_room_ids.append(room_model.id)

    monkeypatch.setattr("app.api.notify_game_started", fake_notify_game_started)

    response = client.post(
        f"/rooms/{room['id']}/start",
        headers=auth_headers("host"),
    )

    assert response.status_code == 200
    assert notified_room_ids == [room["id"]]


def test_only_host_can_draw_ball(client, monkeypatch):
    room = create_room(client)
    client.post(f"/rooms/{room['id']}/start", headers=auth_headers("host"))

    response = client.post(
        f"/rooms/{room['id']}/draw",
        headers=auth_headers("player"),
    )

    assert response.status_code == 403


def test_host_draws_ball_through_game_engine(client, monkeypatch):
    room = create_room(client)
    client.post(f"/rooms/{room['id']}/start", headers=auth_headers("host"))
    drawn_room_ids = []

    def fake_draw_game_ball(room_model):
        drawn_room_ids.append(room_model.id)
        return {"label": "B7", "letter": "B", "number": 7, "order": 1}

    monkeypatch.setattr("app.api.draw_game_ball", fake_draw_game_ball)

    response = client.post(
        f"/rooms/{room['id']}/draw",
        headers=auth_headers("host"),
    )

    assert response.status_code == 200
    assert response.json()["label"] == "B7"
    assert drawn_room_ids == [room["id"]]


def test_finish_room_notifies_game_engine(client, monkeypatch):
    room = create_room(client)
    client.post(f"/rooms/{room['id']}/start", headers=auth_headers("host"))
    notified_room_ids = []

    def fake_notify_game_finished(room_model):
        notified_room_ids.append(room_model.id)

    monkeypatch.setattr("app.api.notify_game_finished", fake_notify_game_finished)

    response = client.post(
        f"/rooms/{room['id']}/finish",
        headers=auth_headers("host"),
    )

    assert response.status_code == 200
    assert notified_room_ids == [room["id"]]


def test_internal_finish_marks_finished_even_if_game_engine_already_stopped(client, monkeypatch):
    room = create_room(client)
    client.post(f"/rooms/{room['id']}/start", headers=auth_headers("host"))

    def fake_notify_game_finished(room_model):
        return None

    monkeypatch.setattr("app.api.notify_game_finished", fake_notify_game_finished)

    response = client.post(
        f"/internal/rooms/{room['id']}/finish",
        headers={"X-Internal-Service-Token": "internal-test-token"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "finished"


def test_join_after_start_is_rejected(client):
    room = create_room(client)
    client.post(f"/rooms/{room['id']}/start", headers=auth_headers("host"))

    response = client.post(
        f"/rooms/{room['id']}/join",
        headers=auth_headers("late-player"),
    )

    assert response.status_code == 409


def test_invalid_status_transitions_are_rejected(client):
    room = create_room(client)

    finish_before_start = client.post(
        f"/rooms/{room['id']}/finish",
        headers=auth_headers("host"),
    )
    assert finish_before_start.status_code == 409

    client.post(f"/rooms/{room['id']}/start", headers=auth_headers("host"))
    start_again = client.post(
        f"/rooms/{room['id']}/start",
        headers=auth_headers("host"),
    )
    assert start_again.status_code == 409


def test_internal_finish_requires_service_token(client):
    room = create_room(client)
    client.post(f"/rooms/{room['id']}/start", headers=auth_headers("host"))

    response = client.post(f"/internal/rooms/{room['id']}/finish")

    assert response.status_code == 401


def test_internal_finish_marks_active_room_finished(client):
    room = create_room(client)
    client.post(f"/rooms/{room['id']}/start", headers=auth_headers("host"))

    response = client.post(
        f"/internal/rooms/{room['id']}/finish",
        headers={"X-Internal-Service-Token": "internal-test-token"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "finished"


def test_internal_finish_is_idempotent_for_finished_room(client):
    room = create_room(client)
    client.post(f"/rooms/{room['id']}/start", headers=auth_headers("host"))
    client.post(f"/rooms/{room['id']}/finish", headers=auth_headers("host"))

    response = client.post(
        f"/internal/rooms/{room['id']}/finish",
        headers={"X-Internal-Service-Token": "internal-test-token"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "finished"


def test_missing_user_header_is_unauthorized(client):
    response = client.post("/rooms")

    assert response.status_code == 401


def test_legacy_user_header_still_works(client):
    response = client.post(
        "/rooms",
        headers={"X-User-Id": "legacy-host", "X-User-Name": "Legacy Host"},
    )

    assert response.status_code == 201
    assert response.json()["host_user_id"] == "legacy-host"
    assert response.json()["players"][0]["display_name"] == "Legacy Host"


def test_unknown_room_returns_404(client):
    response = client.get("/rooms/999")

    assert response.status_code == 404


def test_invalid_room_id_returns_422(client):
    response = client.get("/rooms/not-a-number")

    assert response.status_code == 422
