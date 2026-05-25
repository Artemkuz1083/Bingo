def create_room(client, user_id="host"):
    response = client.post("/rooms", headers={"X-User-Id": user_id})
    assert response.status_code == 201
    return response.json()


def test_create_room_adds_host_as_player(client):
    room = create_room(client)

    assert room["host_user_id"] == "host"
    assert room["status"] == "waiting"
    assert [player["user_id"] for player in room["players"]] == ["host"]


def test_join_room_is_idempotent(client):
    room = create_room(client)

    first = client.post(
        f"/rooms/{room['id']}/join",
        headers={"X-User-Id": "player"},
    )
    second = client.post(
        f"/rooms/{room['id']}/join",
        headers={"X-User-Id": "player"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    players = second.json()["players"]
    assert [player["user_id"] for player in players] == ["host", "player"]


def test_get_room_players(client):
    room = create_room(client)
    client.post(f"/rooms/{room['id']}/join", headers={"X-User-Id": "player"})

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
        headers={"X-User-Id": "player"},
    )

    assert response.status_code == 403


def test_room_status_flow(client):
    room = create_room(client)

    started = client.post(
        f"/rooms/{room['id']}/start",
        headers={"X-User-Id": "host"},
    )
    finished = client.post(
        f"/rooms/{room['id']}/finish",
        headers={"X-User-Id": "host"},
    )

    assert started.status_code == 200
    assert started.json()["status"] == "active"
    assert finished.status_code == 200
    assert finished.json()["status"] == "finished"


def test_join_after_start_is_rejected(client):
    room = create_room(client)
    client.post(f"/rooms/{room['id']}/start", headers={"X-User-Id": "host"})

    response = client.post(
        f"/rooms/{room['id']}/join",
        headers={"X-User-Id": "late-player"},
    )

    assert response.status_code == 409


def test_invalid_status_transitions_are_rejected(client):
    room = create_room(client)

    finish_before_start = client.post(
        f"/rooms/{room['id']}/finish",
        headers={"X-User-Id": "host"},
    )
    assert finish_before_start.status_code == 409

    client.post(f"/rooms/{room['id']}/start", headers={"X-User-Id": "host"})
    start_again = client.post(
        f"/rooms/{room['id']}/start",
        headers={"X-User-Id": "host"},
    )
    assert start_again.status_code == 409


def test_missing_user_header_is_unauthorized(client):
    response = client.post("/rooms")

    assert response.status_code == 401


def test_unknown_room_returns_404(client):
    response = client.get("/rooms/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


def test_invalid_room_id_returns_422(client):
    response = client.get("/rooms/not-a-uuid")

    assert response.status_code == 422
