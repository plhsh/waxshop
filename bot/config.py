import os
from dataclasses import dataclass
from alchemy import menu_loader


@dataclass
class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    PAYMENTS_TOKEN = os.getenv("PAYMENTS_TOKEN")
    ADM_CHT_ID = os.getenv("ADM_CHT_ID")
    OWNERS = os.getenv("OWNERS")
    START_HOUR = 8
    START_MINUTE = 0
    END_HOUR = 22
    END_MINUTE = 45
    W_END_MORNING_ADJ = 1
    MAX_ORDER = 6


@dataclass
class Menu:
    menu_dicts = menu_loader()