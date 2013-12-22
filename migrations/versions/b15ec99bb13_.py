"""empty message

Revision ID: b15ec99bb13
Revises: b4abab3e4d2
Create Date: 2013-12-22 23:12:29.687403

"""

# revision identifiers, used by Alembic.
revision = 'b15ec99bb13'
down_revision = 'b4abab3e4d2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('noticed_glance',
    sa.Column('receiver_user_id', sa.Integer(), nullable=False),
    sa.Column('sender_twitter_display_name', sa.String(length=255), nullable=False),
    sa.Column('when', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['receiver_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('receiver_user_id', 'sender_twitter_display_name'),
    sa.UniqueConstraint('receiver_user_id','sender_twitter_display_name')
    )
    op.drop_table(u'noticed_glances')
    op.drop_constraint(u'whoyoulookinat_user_id_looking_at_twitter_display_name_key', 'whoyoulookinat')
    op.create_unique_constraint(None, 'whoyoulookinat', ['user_id', 'looking_at_twitter_display_name'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'whoyoulookinat')
    op.create_unique_constraint(u'whoyoulookinat_user_id_looking_at_twitter_display_name_key', 'whoyoulookinat', [u'looking_at_twitter_display_name', u'user_id'])
    op.create_table(u'noticed_glances',
    sa.Column(u'receiver_user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column(u'sender_twitter_display_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column(u'when', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['receiver_user_id'], [u'users.id'], name=u'noticed_glances_receiver_user_id_fkey'),
    sa.PrimaryKeyConstraint(u'receiver_user_id', u'sender_twitter_display_name', name=u'noticed_glances_pkey')
    )
    op.drop_table('noticed_glance')
    ### end Alembic commands ###
