from ..connect import session_maker
from ..models import Plan
from loader import logger, config


def get_all_plans():
    with session_maker() as session:
        return session.query(Plan).all()

def get_plan(plan_id):
    with session_maker() as session:
        return session.query(Plan).filter(Plan.id == plan_id).first()