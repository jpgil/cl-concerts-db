"""changed collation of person to something accent mark unsensitive

Revision ID: ed897abe8a53
Revises: 8e0447a4542f
Create Date: 2020-10-12 19:12:48.963059

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.types as ty


# revision identifiers, used by Alembic.
revision = 'ed897abe8a53'
down_revision = '8e0447a4542f'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('person','first_name', type_=ty.VARCHAR(80, collation='utf8_general_ci'))
    op.alter_column('person','last_name', type_=ty.VARCHAR(80, collation='utf8_general_ci'))


def downgrade():
    op.alter_column('person','first_name', type_=ty.VARCHAR(80, collation='utf8_bin'))
    op.alter_column('person','last_name', type_=ty.VARCHAR(80, collation='utf8_bin'))
    
