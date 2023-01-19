from ..connect import session_maker
from ..models import Order, User, Plan
from datetime import datetime
from loader import logger, config
from services.donate import check_order, test_check_order

def create_order(user: User, plan: Plan):
    order = Order(
        status='pending',
        user_status='ожидает',
        user_id=user.id,
        plan_days=plan.days,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    if user.discount:
        order.amount = plan.amount - user.discount
        order.with_discount = True
        if user.invite_discount:
            order.invite_order = True
    else:
        order.amount = plan.amount

    with session_maker() as session:
        session.add(order)
        session.commit()
        donate_url = f'https://yoomoney.ru/quickpay/confirm.xml?receiver={config.donate.y_wallet}'\
                f'&quickpay-form=shop&sum={order.amount}&label={order.id}'
        order.donate_url = donate_url
        user.discount = 0
        user.invite_discount = False
        session.add(order)
        session.add(user)
        session.commit()
        logger.info(f'Создан счет id={order.id} для пользователя {user.name} id={user.id}')
        return order

def delete_order(order_id):
    with session_maker() as session:
        session.query(Order).filter(Order.id == order_id).delete()
        session.commit()

def get_order(order_id):
    with session_maker() as session:
        return session.query(Order).filter(Order.id == order_id).first()

def get_user_pending_orders(user_id):
    with session_maker() as session:
        orders = session.query(Order).filter(
            Order.user_id == user_id,
            Order.status == 'pending'
            ).all()
        return orders

def get_user_orders(user_id):
    with session_maker() as session:
        orders = session.query(Order).filter(
            Order.user_id == user_id,
            ).all()
        return orders

def get_pending_orders():
    with session_maker() as session:
        orders = session.query(Order).filter(
            Order.status == 'pending',
            ).all()
        return orders