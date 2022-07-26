"""empty message

Revision ID: e01ca27ce0c5
Revises: be55551c9b55
Create Date: 2022-07-25 17:40:35.042279

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e01ca27ce0c5'
down_revision = 'be55551c9b55'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('favorited',
    sa.Column('favorited_park_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('parks_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['parks_id'], ['parks.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('favorited_park_id')
    )
    op.create_table('visited',
    sa.Column('visited_park_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('parks_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['parks_id'], ['parks.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('visited_park_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('visited')
    op.drop_table('favorited')
    # ### end Alembic commands ###
