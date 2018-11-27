from sqlalchemy.types import Integer

from .orm import Base

__all__ = 'Account', 'Approval', 'Customer'


class Customer(Base):
    """서비스를 사용하는 유저."""

    id = Column(Integer, primary_key=True)

    __tablename__ = 'customer'


class Account(Base):
    """패스워드와 계정 정보"""

    id = Column(Integer, primary_key=True)

    __tablename__ = 'account'


class Approval(Base):
    """패스워드 승인 정보"""

    __tablename__ = 'approval'
