"""Increase MediaLink description

Revision ID: 9ac58cc15e7e
Revises: c1a898452b47
Create Date: 2022-08-25 00:29:26.095329

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9ac58cc15e7e'
down_revision = 'c1a898452b47'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('media_link', 'description',
               existing_type=mysql.VARCHAR(collation='utf8_bin', length=150),
               type_=sa.String(length=2000),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('media_link', 'description',
               existing_type=sa.String(length=2000),
               type_=mysql.VARCHAR(collation='utf8_bin', length=150),
               existing_nullable=True)
    # ### end Alembic commands ###