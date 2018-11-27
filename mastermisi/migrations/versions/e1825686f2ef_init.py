"""Init

Revision ID: e1825686f2ef
Revises:
Create Date: 2018-11-28 01:36:26.089499

"""
from alembic import op
import sqlalchemy as sa  # noqa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e1825686f2ef'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'customer',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('passphrase', sa.BINARY(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table(
        'account',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('host', sa.Unicode(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('passphrase', sa.BINARY(), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'approval',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('expired_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('quiz_answer', sa.Unicode(), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('approval')
    op.drop_table('account')
    op.drop_table('customer')
