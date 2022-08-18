import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

@dataclass
class TgBot:
    token: str
    admin_ids: List[int]

@dataclass
class DbConfig:
    host: str
    port: str
    user: str
    password: str
    name: str

@dataclass
class Misc:
    pass

@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Misc

def load_config(path: str = None):
    load_dotenv(path)
    return Config(
        tg_bot=TgBot(
            token=os.getenv('BOT_TOKEN'),
            admin_ids=list(map(int, os.getenv('ADMINS').split(',')))
        ),
        db=DbConfig(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            name=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
        ),
        misc=Misc()
    )