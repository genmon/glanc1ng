"""empty message

Revision ID: 4bbdaaa6c835
Revises: 504fad35f337
Create Date: 2013-12-30 09:35:07.790625

"""

# revision identifiers, used by Alembic.
revision = '4bbdaaa6c835'
down_revision = '504fad35f337'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'received_unnoticed_glance', ['receiver_twitter_id', 'hour'])
    op.drop_constraint(u'twitter_friends_cache_twitter_id_friend_twitter_id_key', 'twitter_friends_cache')
    op.create_unique_constraint(None, 'twitter_friends_cache', ['twitter_id', 'friend_twitter_id'])
    op.drop_constraint(u'unnoticed_glance_receiver_user_id_hour_key', 'unnoticed_glance')
    op.create_unique_constraint(None, 'unnoticed_glance', ['receiver_user_id', 'hour'])
    op.drop_constraint(u'whoyoulookinat_user_id_looking_at_twitter_display_name_key', 'whoyoulookinat')
    op.create_unique_constraint(None, 'whoyoulookinat', ['user_id', 'looking_at_twitter_display_name'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'whoyoulookinat')
    op.create_unique_constraint(u'whoyoulookinat_user_id_looking_at_twitter_display_name_key', 'whoyoulookinat', [u'looking_at_twitter_display_name', u'user_id'])
    op.drop_constraint(None, 'unnoticed_glance')
    op.create_unique_constraint(u'unnoticed_glance_receiver_user_id_hour_key', 'unnoticed_glance', [u'hour', u'receiver_user_id'])
    op.drop_constraint(None, 'twitter_friends_cache')
    op.create_unique_constraint(u'twitter_friends_cache_twitter_id_friend_twitter_id_key', 'twitter_friends_cache', [u'friend_twitter_id', u'twitter_id'])
    op.drop_constraint(None, 'received_unnoticed_glance')
    ### end Alembic commands ###
