from sqlalchemy.orm import relationship
import sqlalchemy as sql
from .connect import Base


class User(Base):
    __tablename__ = 'user'

    id = sql.Column(sql.Integer, primary_key=True)
    telegram_id = sql.Column(sql.BigInteger, nullable=False)
    name = sql.Column(sql.String(30))
    status = sql.Column(sql.String(10), default='created')
    created_at = sql.Column(sql.DateTime)
    updated_at = sql.Column(sql.DateTime)

    vpn = relationship('Vpn', backref='user', )

    
class Vpn(Base):
    __tablename__ = 'vpn'

    id = sql.Column(sql.Integer, primary_key=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('user.id'), nullable=False)
    server_id = sql.Column(sql.Integer, sql.ForeignKey('server.id'))
    ip = sql.Column(sql.String(18))
    public_key = sql.Column(sql.String(50))
    status = sql.Column(sql.String(10))
    created_at = sql.Column(sql.DateTime)
    updated_at = sql.Column(sql.DateTime)
    expires_at = sql.Column(sql.DateTime)


class Server(Base):
    __tablename__ = 'server'

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(30))
    lan = sql.Column(sql.String(18))
    lan_ip = sql.Column(sql.String(18))
    wan_ip = sql.Column(sql.String(15))
    users_cnt = sql.Column(sql.Integer(), default=0)

    vpn = relationship('Vpn', backref='server')

    def __repr__(self) -> str:
        return f'{self.name}'