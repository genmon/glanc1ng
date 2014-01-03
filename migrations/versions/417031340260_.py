"""empty message

Revision ID: 417031340260
Revises: 166cff6f6e9c
Create Date: 2014-01-03 11:50:54.260038

"""

# revision identifiers, used by Alembic.
revision = '417031340260'
down_revision = '166cff6f6e9c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bergcloud_device',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('device_address', sa.String(length=255), nullable=False),
    sa.Column('is_online', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.drop_table(u'berg_cloud_device')
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
    op.create_table(u'berg_cloud_device',
    sa.Column(u'user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column(u'device_address', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column(u'is_online', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], [u'users.id'], name=u'berg_cloud_device_user_id_fkey'),
    sa.PrimaryKeyConstraint(u'user_id', name=u'berg_cloud_device_pkey')
    )
    op.drop_table('bergcloud_device')
    ### end Alembic commands ###
