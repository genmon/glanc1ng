"""empty message

Revision ID: 29ed890c3920
Revises: 3bc1292e9ccb
Create Date: 2013-12-22 20:55:13.230116

"""

# revision identifiers, used by Alembic.
revision = '29ed890c3920'
down_revision = '3bc1292e9ccb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'noticed_glances', ['receiver_user_id', 'sender_twitter_display_name'])
    op.drop_constraint(u'whoyoulookinat_user_id_looking_at_twitter_display_name_key', 'whoyoulookinat')
    op.create_unique_constraint(None, 'whoyoulookinat', ['user_id', 'looking_at_twitter_display_name'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'whoyoulookinat')
    op.create_unique_constraint(u'whoyoulookinat_user_id_looking_at_twitter_display_name_key', 'whoyoulookinat', [u'looking_at_twitter_display_name', u'user_id'])
    op.drop_constraint(None, 'noticed_glances')
    ### end Alembic commands ###