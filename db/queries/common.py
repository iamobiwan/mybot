from ..connect import session_maker
from ..models import User
from loader import logger, config


def update_item(item):
    with session_maker() as session:
        session.add(item)
        session.commit()