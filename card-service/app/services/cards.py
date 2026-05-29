import random

from app.schemas.cards import CardCell, CardResponse, WinnerCheckData


BALL_RANGES = {
    "B": range(1, 16),
    "I": range(16, 31),
    "N": range(31, 46),
    "G": range(46, 61),
    "O": range(61, 76),
}

COLUMN_LETTERS = tuple(BALL_RANGES.keys())
FREE_ROW = 2
FREE_COL = 2


def generate_card(game_id: str, user_id: str) -> CardResponse:
    columns = {
        letter: random.sample(list(numbers), 5)
        for letter, numbers in BALL_RANGES.items()
    }
    rows: list[list[CardCell]] = []

    for row in range(5):
        cells: list[CardCell] = []
        for col, letter in enumerate(COLUMN_LETTERS):
            if row == FREE_ROW and col == FREE_COL:
                cells.append(
                    CardCell(
                        row=row,
                        col=col,
                        letter=letter,
                        label="FREE",
                        marked=True,
                        is_free=True,
                    )
                )
                continue

            number = columns[letter][row]
            cells.append(
                CardCell(
                    row=row,
                    col=col,
                    letter=letter,
                    number=number,
                    label=f"{letter}{number}",
                )
            )
        rows.append(cells)

    return CardResponse(
        game_id=game_id,
        user_id=user_id,
        cells=rows,
        marked_numbers=[],
    )


def mark_number(card: CardResponse, number: int) -> tuple[CardResponse, bool]:
    matched = False
    marked_numbers = set(card.marked_numbers)

    for row in card.cells:
        for cell in row:
            if cell.number == number:
                cell.marked = True
                matched = True
                marked_numbers.add(number)

    card.marked_numbers = sorted(marked_numbers)
    return card, matched


def build_winner_check_data(card: CardResponse) -> WinnerCheckData:
    columns = [
        [card.cells[row][col] for row in range(5)]
        for col in range(5)
    ]
    diagonals = [
        [card.cells[index][index] for index in range(5)],
        [card.cells[index][4 - index] for index in range(5)],
    ]

    return WinnerCheckData(
        game_id=card.game_id,
        user_id=card.user_id,
        rows=card.cells,
        columns=columns,
        diagonals=diagonals,
        marked_numbers=card.marked_numbers,
    )
