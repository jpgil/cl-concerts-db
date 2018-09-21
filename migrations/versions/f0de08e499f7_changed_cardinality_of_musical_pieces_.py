"""Changed cardinality of musical pieces - instrument

Revision ID: f0de08e499f7
Revises: e00a198c270a
Create Date: 2018-09-21 20:30:46.562417

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0de08e499f7'
down_revision = 'e00a198c270a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('musicalpiece_instrument',
    sa.Column('instrument_id', sa.Integer(), nullable=False),
    sa.Column('musical_piece_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['instrument_id'], ['instrument.id'], ),
    sa.ForeignKeyConstraint(['musical_piece_id'], ['musical_piece.id'], ),
    sa.PrimaryKeyConstraint('instrument_id', 'musical_piece_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('musicalpiece_instrument')
    # ### end Alembic commands ###
