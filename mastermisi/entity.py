import base64
import datetime
import hashlib
import random
from typing import Optional
import uuid

from cryptography.fernet import Fernet
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import CheckConstraint, Column, ForeignKey
from sqlalchemy.sql.functions import now
from sqlalchemy.types import DateTime, LargeBinary, Unicode

from .orm import Base

__all__ = 'Account', 'Approval', 'Customer'


def uuid4():
    """랜덤한 UUID를 반환합니다."""
    return uuid.uuid4()


def utcnow():
    """UTC 기준의 현재 시각을 반환합니다."""
    return datetime.datetime.now(datetime.timezone.utc)


def span_bytes(bytes_: bytes, length: int = 32):
    """바이트열을 암호화 키로 사용하기 위해 특정 크기로 조절합니다."""
    if not (bytes_ and isinstance(bytes_, bytes)):
        raise ValueError('bytes_는 1바이트 이상의 바이트열이어야 합니다.')
    if len(bytes_) < 32:
        return span_bytes(bytes_ * 2, length)
    else:
        return bytes_[:32]


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
    passphrase = Column(LargeBinary, nullable=False)
    # 소유한 계정 목록
    accounts = relationship(
        'Account', back_populates='customer',
        cascade="save-update, merge, delete, delete-orphan"
    )

    @classmethod
    def create_passphrase(cls, plain: str) -> bytes:
        return hashlib.sha256(plain.encode('utf-8')).digest()

    def encrypt(self, plain_text: str, *, passphrase: str) -> bytes:
        assert self.match_passphrase(passphrase)
        key = base64.urlsafe_b64encode(span_bytes(passphrase.encode('utf-8')))
        f = Fernet(key)
        return f.encrypt(plain_text.encode('utf-8'))

    def create_account(self, host: str, name: str, plain_pass: str,
                       *, passphrase: str) -> 'Account':
        return Account(
            host=host,
            name=name,
            passphrase=self.encrypt(plain_pass, passphrase=passphrase),
            customer=self
        )

    def match_passphrase(self, plain: str) -> bool:
        pw = self.create_passphrase(plain)
        return pw == self.passphrase

    @property
    def token(self) -> str:
        return self.id.hex


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
    # 계정의 비밀번호. 유저의 비밀번호를 키로 사용하여 암호화하여 생성합니다.
    passphrase = Column(LargeBinary, nullable=False)
    # 계정의 주인 유저
    customer = relationship('Customer', back_populates='accounts')
    # 관련된 승인 요청 목록
    approvals = relationship(
        'Approval', back_populates='account',
        cascade="save-update, merge, delete, delete-orphan"
    )

    def decrypt(self, *, passphrase: str) -> str:
        assert self.customer.match_passphrase(passphrase)
        key = base64.urlsafe_b64encode(span_bytes(passphrase.encode('utf-8')))
        f = Fernet(key)
        return f.decrypt(self.passphrase).decode('utf-8')

    def create_approval(self, *,
                        now: Optional[datetime.datetime] = None) -> 'Approval':
        t = 'abcdefghijklmnopqrstuwxyzABCDEFGHIJKLMNOPQRSTUWXY0123456789'
        if not now:
            now = utcnow()
        return Approval(
            account=self,
            quiz_answer=''.join(random.sample(t, 6)),
            expired_at=now + datetime.timedelta(seconds=60 * 5)
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

    __table_args__ = (
        CheckConstraint('created_at < expired_at', name='ck_expired_at'),
    )

    def approve(self, *, passphrase: str,
                now: Optional[datetime.datetime] = None) -> str:
        if now is None:
            now = utcnow()
        assert self.approved_at is None
        assert self.expired_at < now
        self.approved_at = now
        return self.account.decrypt(passphrase)

    @hybrid_property
    def activated(self) -> bool:
        return self.expired_at >= utcnow()

    @activated.expression
    def activated(cls):
        return cls.expired_at >= now()
