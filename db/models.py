from sqlalchemy.orm import relationship
import sqlalchemy as sql
from .connect import Base


class User(Base):
    __tablename__ = 'user'

    id = sql.Column(sql.Integer, primary_key=True)
    telegram_id = sql.Column(sql.BigInteger, nullable=False)
    name = sql.Column(sql.String(30))
    status = sql.Column(sql.String(10), default='created')
    ip = sql.Column(sql.String(18))
    public_key = sql.Column(sql.String(50))
    server_id = sql.Column(sql.Integer, sql.ForeignKey('server.id'))
    created_at = sql.Column(sql.DateTime)
    updated_at = sql.Column(sql.DateTime)
    vpn_created_at = sql.Column(sql.DateTime)

    request = relationship('Request', backref='user')


class Request(Base):
    __tablename__ = 'request'

    id = sql.Column(sql.Integer, primary_key=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('user.id'), nullable=False)
    status = sql.Column(sql.String(15))


class Server(Base):
    __tablename__ = 'server'

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(30))
    lan = sql.Column(sql.String(18))
    lan_ip = sql.Column(sql.String(18))
    wan_ip = sql.Column(sql.String(15))
    users_cnt = sql.Column(sql.Integer(), default=0)

    user = relationship('User', backref='server')

    def __repr__(self) -> str:
        return f'{self.name}'