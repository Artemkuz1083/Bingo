import random
from dataclasses import dataclass

BALL_RANGES = {
    "B": range(1, 16),
    "I": range(16, 31),
    "N": range(31, 46),
    "G": range(46, 61),
    "O": range(61, 76),
}

BALL_POOL : list[str] =[]

for letter, numbers in BALL_RANGES.items():
    for num in numbers:
        BALL_POOL.append(f"{letter}{num}")

@dataclass
class DrawnBall:
    label: str #B7
    letter: str #B
    num: int #7
    order: int # последовательность выпадения

def parse_ball(label: str) -> tuple[str, int]:
    return label[0], int(label[1:])

def build_shuffle_pool() -> list[str]:
    pool = BALL_POOL.copy()
    random.shuffle(pool)
    return pool