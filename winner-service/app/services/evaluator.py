import re

from app.schemas.winners import CardCell, WinnerCheckData

WINNING_PATTERN_POSITIONS = {
    "top_row": [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
    "middle_row": [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)],
    "bottom_row": [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
    "left_column": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
    "middle_column": [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2)],
    "right_column": [(0, 4), (1, 4), (2, 4), (3, 4), (4, 4)],
    "main_diagonal": [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)],
    "anti_diagonal": [(0, 4), (1, 3), (2, 2), (3, 1), (4, 0)],
    "four_corners": [(0, 0), (0, 4), (4, 0), (4, 4)],
    "x_shape": [
        (0, 0), (1, 1), (2, 2), (3, 3), (4, 4),
        (0, 4), (1, 3), (3, 1), (4, 0),
    ],
    "plus_shape": [
        (0, 2), (1, 2), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (3, 2), (4, 2),
    ],
    "small_frame": [
        (1, 1), (1, 2), (1, 3),
        (2, 1), (2, 3),
        (3, 1), (3, 2), (3, 3),
    ],
}


def normalize_drawn_numbers(raw_balls: list[str | int | dict]) -> set[int]:
    numbers: set[int] = set()
    for ball in raw_balls:
        if isinstance(ball, int):
            numbers.add(ball)
            continue
        if isinstance(ball, dict):
            number = ball.get("number")
            if isinstance(number, int):
                numbers.add(number)
                continue
            ball = ball.get("label", "")

        match = re.search(r"\d+", str(ball))
        if match is not None:
            numbers.add(int(match.group()))

    return numbers


def is_cell_covered(cell: CardCell, drawn_numbers: set[int]) -> bool:
    if cell.is_free:
        return True
    if cell.number is None:
        return False
    return cell.number in drawn_numbers


def is_winning_line(cells: list[CardCell], drawn_numbers: set[int]) -> bool:
    return all(is_cell_covered(cell, drawn_numbers) for cell in cells)


def cells_for_pattern(card: WinnerCheckData, winning_pattern: str) -> list[CardCell]:
    positions = WINNING_PATTERN_POSITIONS.get(winning_pattern, WINNING_PATTERN_POSITIONS["top_row"])
    return [card.rows[row][col] for row, col in positions]


def has_bingo(
    card: WinnerCheckData,
    drawn_balls: list[str | int | dict],
    winning_pattern: str = "top_row",
) -> bool:
    drawn_numbers = normalize_drawn_numbers(drawn_balls)
    return is_winning_line(cells_for_pattern(card, winning_pattern), drawn_numbers)
