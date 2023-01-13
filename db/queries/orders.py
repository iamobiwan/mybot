from ..connect import session_maker
from ..models import Order
from datetime import datetime
from loader import logger, config

def create_order(user, plan):
    order = Order(
        status='pending',
        user_status='ожидает',
        user_id=user.id,
        plan_days=plan.days,
        amount=plan.amount,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    with session_maker() as session:
        session.add(order)
        session.commit()
        label = f'{order.id}'
        donate_url = f'https://yoomoney.ru/quickpay/confirm.xml?receiver={config.donate.y_wallet}'\
                f'&quickpay-form=shop&sum={plan.amount}&label={label}'
        order.label = label
        order.donate_url = donate_url
        session.add(order)
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