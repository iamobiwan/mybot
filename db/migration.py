from curses import echo
from sqlalchemy.orm import relationship, backref
import sqlalchemy as sql
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()

engine = create_engine(f'postgresql://endurance:qwerty@127.0.0.1:5432/endurance_db', echo=True)

session_maker = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'user'

    id = sql.Column(sql.Integer, primary_key=True)
    telegram_id = sql.Column(sql.BigInteger, nullable=False)
    name = sql.Column(sql.String(30))
    status = sql.Column(sql.String(10), default='created')
    created_at = sql.Column(sql.DateTime)
    updated_at = sql.Column(sql.DateTime)

    vpn = relationship('Vpn', backref='user')

    
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

class Vpn(Base):
    __tablename__ = 'vpn'

    id = sql.Column(sql.Integer, primary_key=True)
    user_id = sql.Column(sql.Integer, sql.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    server_id = sql.Column(sql.Integer, sql.ForeignKey('server.id', ondelete='cascade'))
    ip = sql.Column(sql.String(18))
    public_key = sql.Column(sql.String(50))
    status = sql.Column(sql.String(10))
    created_at = sql.Column(sql.DateTime)
    updated_at = sql.Column(sql.DateTime)
    expires_at = sql.Column(sql.DateTime)

    bill = relationship('Bill', backref='vpn')


class Tariff(Base):
    __tablename__ = 'tariff'

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(30))
    days = sql.Column(sql.Integer)
    price = sql.Column(sql.Integer)

    bill = relationship('Bill', backref='tariff')


class Bill(Base):
    __tablename__ = 'bill'

    id = sql.Column(sql.Integer, primary_key=True)
    status = sql.Column(sql.String(10))
    vpn_id = sql.Column(sql.Integer, sql.ForeignKey('vpn.id'))
    tariff_id = sql.Column(sql.Integer, sql.ForeignKey('tariff.id'))
    pay_url = sql.Column(sql.String(200))
    created_at = sql.Column(sql.DateTime)
    updated_at = sql.Column(sql.DateTime)
    expires_at = sql.Column(sql.DateTime)

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

with session_maker() as session:
    server = Server(
        name='loki',
        lan='172.16.1.0/24',
        lan_ip='172.16.1.1',
        wan_ip='185.103.254.12',
        users_cnt='0'
    )
    tariff1 = Tariff(
        name='Месяц',
        days=30,
        price=400
    )
    tariff2 = Tariff(
        name='Четверть',
        days=90,
        price=800
    ) 
    tariff3 = Tariff(
        name='Полгода',
        days=180,
        price=1200
    )  
    session.add(server)
    session.add(tariff1)
    session.add(tariff2)
    session.add(tariff3)
    session.commit()

# with session_maker() as session:
#     user = session.query(User).filter(User.id == 1).first()
#     vpn = session.query(Vpn).filter(Vpn.id == 1).first()
#     # print(user.vpn.status)
#     print(vpn.user)

