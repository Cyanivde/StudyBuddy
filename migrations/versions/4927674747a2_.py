"""empty message

Revision ID: 4927674747a2
Revises: 4bb61a073aa9
Create Date: 2022-06-27 21:20:54.981698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4927674747a2'
down_revision = '4bb61a073aa9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('resource_to_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('resource_id', sa.Integer(), nullable=True),
    sa.Column('done', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('resource_to_user')
    # ### end Alembic commands ###