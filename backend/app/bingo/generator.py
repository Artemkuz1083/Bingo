import random

BALL_RANGES = {
    "B": range(1, 16),
    "I": range(16, 31),
    "N": range(31, 46),
    "G": range(46, 61),
    "O": range(61, 76),
}

"""Возвращает все шары для игры в случайном порядке"""
def generator() ->list[str]:
    balls = []

    for word, numbers in BALL_RANGES.items():
        for num in numbers:
            balls.append(f"{word}{num}")

    random.shuffle(balls)
    return balls

if __name__ == "__main__":
    print(generator())