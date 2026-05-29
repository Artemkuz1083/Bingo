import re

from app.schemas.winners import CardCell, WinnerCheckData


def normalize_drawn_numbers(raw_balls: list[str | int]) -> set[int]:
    numbers: set[int] = set()
    for ball in raw_balls:
        if isinstance(ball, int):
            numbers.add(ball)
            continue

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


def has_bingo(card: WinnerCheckData, drawn_balls: list[str | int]) -> bool:
    drawn_numbers = normalize_drawn_numbers(drawn_balls)
    lines = [*card.rows, *card.columns, *card.diagonals]
    return any(is_winning_line(line, drawn_numbers) for line in lines)
