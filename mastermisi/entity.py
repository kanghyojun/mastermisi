import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import DateTime, Unicode

from .orm import Base

__all__ = 'Account', 'Approval', 'Customer',


def uuid4():
    """랜덤한 UUID를 반환합니다."""
    return uuid.uuid4()


def utcnow():
    """UTC 기준의 현재 시각을 반환합니다."""
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


class Customer(Base):
    """서비스를 사용하는 유저. 자신의 여러 계정 정보들을 등록할 수 있습니다."""
    __tablename__ = 'customer'
    # 기본 키
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    # 생성 시각
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    # 유저 이름 (일반적으로 아이디라고 부르는 값)
    name = Column(Unicode, unique=True, nullable=False)
    # 유저 비밀번호
    passphrase = Column(Unicode, nullable=False)
    # 소유한 계정 목록
    accounts = relationship(
        'Account', back_populates='customer',
        cascade="save-update, merge, delete, delete-orphan"
    )


class Account(Base):
    """계정 정보. 정보 접근 승인을 시도할 때마다 승인 정보가 생성됩니다."""
    __tablename__ = 'account'
    # 기본 키
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    # 생성 시각
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    # 소유한 유저의 UUID
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customer.id'))
    # 계정의 호스트 정보
    host = Column(Unicode, nullable=False)
    # 계정의 이름 (일반적으로 아이디라고 부르는 값)
    name = Column(Unicode, nullable=False)
    # 계정의 비밀번호
    passphrase = Column(Unicode, nullable=False)
    # 계정의 주인 유저
    customer = relationship('Customer', back_populates='accounts')
    # 관련된 승인 요청 목록
    approvals = relationship(
        'Approval', back_populates='account',
        cascade="save-update, merge, delete, delete-orphan"
    )


class Approval(Base):
    """승인 정보. 퀴즈 정답을 맞혀야 승인 대상 계정에 접근할 수 있습니다."""
    __tablename__ = 'approval'
    # 기본 키
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    # 생성 시각
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )
    # 승인 대상 계정의 UUID
    account_id = Column(UUID(as_uuid=True), ForeignKey('account.id'))
    # 승인 만료 시각
    expired_at = Column(DateTime(timezone=True), nullable=False)
    # 승인된 시각
    approved_at = Column(DateTime(timezone=True), nullable=True)
    # 승인에 필요한 퀴즈 정답
    quiz_answer = Column(Unicode, nullable=False)
    # 승인 대상 계정
    account = relationship('Account', back_populates='approvals')
