"""changed creation date for composition year

Revision ID: 4f19165fafed
Revises: 33e5a30f8cd3
Create Date: 2018-07-07 22:51:04.092374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f19165fafed'
down_revision = '33e5a30f8cd3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('musical_piece', sa.Column('composition_year', sa.Integer(), nullable=True))
    op.drop_column('musical_piece', 'creation_date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('musical_piece', sa.Column('creation_date', sa.DATE(), nullable=True))
    op.drop_column('musical_piece', 'composition_year')
    # ### end Alembic commands ###
