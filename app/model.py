import uuid
from enum import IntEnum

from typing import List
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import NoResultFound

from .db import engine


class SafeUser(BaseModel):
    """token を含まないUser"""

    id: int
    name: str
    leader_card_id: int

    # SafeUser.from_orm(row) できるようにする
    class Config:
        orm_mode = True


def create_user(name: str, leader_card_id: int) -> str:
    """Create new user and returns their token"""
    # UUID4は天文学的な確率だけど衝突する確率があるので、気にするならリトライする必要がある。
    # サーバーでリトライしない場合は、クライアントかユーザー（手動）にリトライさせることになる。
    # ユーザーによるリトライは一般的には良くないけれども、確率が非常に低ければ許容できる場合もある。
    token = str(uuid.uuid4())
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "INSERT INTO `user` (name, token, leader_card_id)"
                " VALUES (:name, :token, :leader_card_id)"
            ),
            {"name": name, "token": token, "leader_card_id": leader_card_id},
        )
        # DB側で生成されたPRIMARY KEYを参照できる
        print(f"create_user(): {result.lastrowid=}")
    return token


def _get_user_by_token(conn, token: str) -> SafeUser | None:
    result = conn.execute(
        text("SELECT * From `user` Where `token`=:token"),
        {"token": token},
    )
    try:
        row = result.one()
    except NoResultFound:
        return None
    return SafeUser.from_orm(row)


def get_user_by_token(token: str) -> SafeUser | None:
    with engine.begin() as conn:
        return _get_user_by_token(conn, token)


def update_user(id: int, name: str, leader_card_id: int) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE user "
                "SET name=:name, leader_card_id=:leader_card_id "
                "WHERE id=:id"
            ),
            {"id": id, "name": name, "leader_card_id": leader_card_id},
        )


# room -------------------------------------------------------
class Room(BaseModel):
    id: int
    live_id: int
    host_id: int


class RoomMember(BaseModel):
    room_id: int
    user_id: int
    live_difficult: int


class LiveDifficulty(IntEnum):
    normal = 1
    hard = 2


class JoinRoomResult(IntEnum):
    Ok = 1
    RoomFull = 2
    Disbanded = 3
    OtherError = 4


class WaitRoomStatus(IntEnum):
    Waiting = 1
    LiveStart = 2
    Dissolution = 3


def create_room(
        live_id: int, host_user_id: int, difficulty: LiveDifficulty) -> int:
    """部屋を作ってroom_idを返します"""
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "INSERT INTO `room` (live_id, host_user_id)"
                " VALUES (:live_id, :host_user_id)"
            ),
            {live_id: live_id, host_user_id: host_user_id}
        )
        room_id = result.lastrowid
        conn.execute(
            text(
                "INSERT INTO `room_member` (room_id, user_id, live_difficult)"
                " VALUES (:room_id, :user_id, live_difficult)"
            ),
            {
                "room_id": room_id,
                "user_id": host_user_id,
                "live_difficulty": difficulty.value,
            }
        )
        return room_id


def get_room(room_id: int) -> Room | None:
    with engine.begin() as conn:
        conn.execute(
            text(""),
        )
        # TODO: 実装


def delete_room(room_id: int) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(""),
        )
        # TODO: 実装


def get_room_list_by_live_id(live_id: int) -> List[Room]:
    with engine.begin() as conn:
        conn.execute(
            text(""),
        )
        # TODO: 実装


def create_room_member(difficulty: LiveDifficulty) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(""),
        )
        # TODO: 実装


def delete_room_member() -> None:
    with engine.begin() as conn:
        conn.execute(
            text(""),
        )
        # TODO: 実装
