"""empty message

Revision ID: 447faf71e513
Revises: 5adef2feec53
Create Date: 2013-12-27 09:51:07.862365

"""

# revision identifiers, used by Alembic.
revision = '447faf71e513'
down_revision = '5adef2feec53'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('last_sent_glance', sa.Column('count', sa.Integer(), nullable=True))
    op.drop_constraint(u'whoyoulookinat_user_id_looking_at_twitter_display_name_key', 'whoyoulookinat')
    op.create_unique_constraint(None, 'whoyoulookinat', ['user_id', 'looking_at_twitter_display_name'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'whoyoulookinat')
    op.create_unique_constraint(u'whoyoulookinat_user_id_looking_at_twitter_display_name_key', 'whoyoulookinat', [u'looking_at_twitter_display_name', u'user_id'])
    op.drop_column('last_sent_glance', 'count')
    ### end Alembic commands ###
