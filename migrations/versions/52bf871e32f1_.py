"""empty message

Revision ID: 52bf871e32f1
Revises: 4df7d244c774
Create Date: 2013-12-31 14:15:35.651523

"""

# revision identifiers, used by Alembic.
revision = '52bf871e32f1'
down_revision = '4df7d244c774'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('twitter_friends_cache', sa.Column('is_mutual', sa.Boolean(), nullable=False))
    op.drop_constraint(u'twitter_friends_cache_twitter_id_friend_twitter_id_key', 'twitter_friends_cache')
    op.create_unique_constraint(None, 'twitter_friends_cache', ['twitter_id', 'friend_twitter_id'])
    op.drop_constraint(u'whoyoulookinat_user_id_looking_at_twitter_display_name_key', 'whoyoulookinat')
    op.create_unique_constraint(None, 'whoyoulookinat', ['user_id', 'looking_at_twitter_display_name'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'whoyoulookinat')
    op.create_unique_constraint(u'whoyoulookinat_user_id_looking_at_twitter_display_name_key', 'whoyoulookinat', [u'looking_at_twitter_display_name', u'user_id'])
    op.drop_constraint(None, 'twitter_friends_cache')
    op.create_unique_constraint(u'twitter_friends_cache_twitter_id_friend_twitter_id_key', 'twitter_friends_cache', [u'friend_twitter_id', u'twitter_id'])
    op.drop_column('twitter_friends_cache', 'is_mutual')
    ### end Alembic commands ###