"""empty message

Revision ID: 4df7d244c774
Revises: 221b3f4dd7c4
Create Date: 2013-12-30 16:49:13.293448

"""

# revision identifiers, used by Alembic.
revision = '4df7d244c774'
down_revision = '221b3f4dd7c4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('received_noticed_glance', 'receiver_twitter_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=255),
               existing_nullable=False,
               existing_server_default="nextval('received_noticed_glance_receiver_twitter_id_seq'::regclass)")
    op.alter_column('received_noticed_glance', 'sender_twitter_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=255),
               existing_nullable=False)
    op.alter_column('received_unnoticed_glance', 'receiver_twitter_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=255),
               existing_nullable=False,
               existing_server_default="nextval('received_unnoticed_glance_receiver_twitter_id_seq'::regclass)")
    op.alter_column('sent_glance', 'twitter_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=255),
               existing_nullable=False,
               existing_server_default="nextval('sent_glance_twitter_id_seq'::regclass)")
    op.alter_column('twitter_friends_cache', 'friend_twitter_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=255),
               existing_nullable=False)
    op.alter_column('twitter_friends_cache', 'twitter_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=255),
               existing_nullable=False,
               existing_server_default="nextval('twitter_friends_cache_twitter_id_seq'::regclass)")
    op.drop_constraint(u'twitter_friends_cache_twitter_id_friend_twitter_id_key', 'twitter_friends_cache')
    op.create_unique_constraint(None, 'twitter_friends_cache', ['twitter_id', 'friend_twitter_id'])
    op.alter_column('twitter_friends_cache_last_updated', 'twitter_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=255),
               existing_nullable=False,
               existing_server_default="nextval('twitter_friends_cache_last_updated_twitter_id_seq'::regclass)")
    op.drop_constraint(u'whoyoulookinat_user_id_looking_at_twitter_display_name_key', 'whoyoulookinat')
    op.create_unique_constraint(None, 'whoyoulookinat', ['user_id', 'looking_at_twitter_display_name'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'whoyoulookinat')
    op.create_unique_constraint(u'whoyoulookinat_user_id_looking_at_twitter_display_name_key', 'whoyoulookinat', [u'looking_at_twitter_display_name', u'user_id'])
    op.alter_column('twitter_friends_cache_last_updated', 'twitter_id',
               existing_type=sa.String(length=255),
               type_=sa.INTEGER(),
               existing_nullable=False,
               existing_server_default="nextval('twitter_friends_cache_last_updated_twitter_id_seq'::regclass)")
    op.drop_constraint(None, 'twitter_friends_cache')
    op.create_unique_constraint(u'twitter_friends_cache_twitter_id_friend_twitter_id_key', 'twitter_friends_cache', [u'friend_twitter_id', u'twitter_id'])
    op.alter_column('twitter_friends_cache', 'twitter_id',
               existing_type=sa.String(length=255),
               type_=sa.INTEGER(),
               existing_nullable=False,
               existing_server_default="nextval('twitter_friends_cache_twitter_id_seq'::regclass)")
    op.alter_column('twitter_friends_cache', 'friend_twitter_id',
               existing_type=sa.String(length=255),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('sent_glance', 'twitter_id',
               existing_type=sa.String(length=255),
               type_=sa.INTEGER(),
               existing_nullable=False,
               existing_server_default="nextval('sent_glance_twitter_id_seq'::regclass)")
    op.alter_column('received_unnoticed_glance', 'receiver_twitter_id',
               existing_type=sa.String(length=255),
               type_=sa.INTEGER(),
               existing_nullable=False,
               existing_server_default="nextval('received_unnoticed_glance_receiver_twitter_id_seq'::regclass)")
    op.alter_column('received_noticed_glance', 'sender_twitter_id',
               existing_type=sa.String(length=255),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.alter_column('received_noticed_glance', 'receiver_twitter_id',
               existing_type=sa.String(length=255),
               type_=sa.INTEGER(),
               existing_nullable=False,
               existing_server_default="nextval('received_noticed_glance_receiver_twitter_id_seq'::regclass)")
    ### end Alembic commands ###