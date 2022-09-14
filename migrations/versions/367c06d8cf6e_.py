"""empty message

Revision ID: 367c06d8cf6e
Revises: 9b5f44616153
Create Date: 2022-09-13 23:43:26.512871

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '367c06d8cf6e'
down_revision = '9b5f44616153'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('course', sa.Column('course_institute_english', sa.String(length=140), nullable=True))
    op.add_column('course', sa.Column('discord_channel_id', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('course', 'discord_channel_id')
    op.drop_column('course', 'course_institute_english')
    # ### end Alembic commands ###
