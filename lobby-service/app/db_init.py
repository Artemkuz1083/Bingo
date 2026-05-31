from sqlalchemy import inspect, text

from app.database import Base, engine
from app import models


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        columns = {column["name"] for column in inspect(connection).get_columns("room_players")}
        if "display_name" not in columns:
            connection.execute(
                text("ALTER TABLE room_players ADD COLUMN display_name VARCHAR(80)")
            )
            connection.execute(
                text("UPDATE room_players SET display_name = user_id WHERE display_name IS NULL")
            )
            connection.execute(
                text("ALTER TABLE room_players ALTER COLUMN display_name SET NOT NULL")
            )

        room_columns = {column["name"] for column in inspect(connection).get_columns("rooms")}
        if "winning_pattern" not in room_columns:
            connection.execute(
                text("ALTER TABLE rooms ADD COLUMN winning_pattern VARCHAR(32)")
            )
            connection.execute(
                text("UPDATE rooms SET winning_pattern = 'top_row' WHERE winning_pattern IS NULL")
            )
            connection.execute(
                text("ALTER TABLE rooms ALTER COLUMN winning_pattern SET NOT NULL")
            )


if __name__ == "__main__":
    init_db()
