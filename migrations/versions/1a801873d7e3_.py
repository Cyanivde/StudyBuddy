"""empty message

Revision ID: 1a801873d7e3
Revises: 7c4ea0b6a2e4
Create Date: 2023-01-08 20:27:12.870225

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a801873d7e3'
down_revision = '7c4ea0b6a2e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('course', sa.Column('show_scans', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('course', 'show_scans')
    # ### end Alembic commands ###
