from app.schemas.winners import CardCell, GameState, WinnerCheckData
from app.services.evaluator import has_bingo, normalize_drawn_numbers


def cell(row: int, col: int, number: int | None, is_free: bool = False) -> CardCell:
    return CardCell(
        row=row,
        col=col,
        letter="B",
        number=number,
        label="FREE" if is_free else f"B{number}",
        is_free=is_free,
    )


def build_card() -> WinnerCheckData:
    rows = [
        [cell(row, col, row * 5 + col + 1) for col in range(5)]
        for row in range(5)
    ]
    rows[2][2] = cell(2, 2, None, is_free=True)
    columns = [[rows[row][col] for row in range(5)] for col in range(5)]
    diagonals = [
        [rows[index][index] for index in range(5)],
        [rows[index][4 - index] for index in range(5)],
    ]
    return WinnerCheckData(
        game_id="game-1",
        user_id="1",
        rows=rows,
        columns=columns,
        diagonals=diagonals,
        marked_numbers=[],
    )


def test_normalize_drawn_numbers_accepts_labels_and_numbers() -> None:
    assert normalize_drawn_numbers(["B1", "I20", 33, "O75"]) == {1, 20, 33, 75}


def test_normalize_drawn_numbers_accepts_game_engine_balls() -> None:
    assert normalize_drawn_numbers(
        [{"label": "B1", "number": 1}, {"label": "I20", "number": 20}]
    ) == {1, 20}


def test_game_state_accepts_game_engine_last_ball_object() -> None:
    state = GameState.model_validate(
        {
            "room_id": "room-1",
            "is_active": True,
            "last_ball": {"label": "B7", "letter": "B", "number": 7},
            "drawn_balls": [{"label": "B7", "letter": "B", "number": 7, "order": 1}],
        },
    )

    assert state.last_ball == {"label": "B7", "letter": "B", "number": 7}


def test_has_bingo_detects_completed_row() -> None:
    assert has_bingo(build_card(), ["B1", "B2", "B3", "B4", "B5"], "top_row")


def test_has_bingo_detects_diagonal_with_free_cell() -> None:
    assert has_bingo(build_card(), [1, 7, 19, 25], "main_diagonal")


def test_has_bingo_rejects_incomplete_lines() -> None:
    assert not has_bingo(build_card(), [1, 2, 3, 4, 7, 13], "top_row")


def test_has_bingo_checks_selected_pattern_only() -> None:
    card = build_card()

    assert has_bingo(card, [1, 2, 3, 4, 5], "top_row")
    assert not has_bingo(card, [1, 2, 3, 4, 5], "middle_column")


def test_has_bingo_accepts_four_corners_pattern() -> None:
    assert has_bingo(build_card(), [1, 5, 21, 25], "four_corners")


def test_has_bingo_accepts_plus_shape_pattern() -> None:
    assert has_bingo(build_card(), [3, 8, 11, 12, 14, 15, 18, 23], "plus_shape")


def test_has_bingo_accepts_small_frame_pattern() -> None:
    assert has_bingo(build_card(), [7, 8, 9, 12, 14, 17, 18, 19], "small_frame")
