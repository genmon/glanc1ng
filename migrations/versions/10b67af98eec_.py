"""empty message

Revision ID: 10b67af98eec
Revises: 1e2cf5acc8c1
Create Date: 2013-12-12 18:30:17.141195

"""

# revision identifiers, used by Alembic.
revision = '10b67af98eec'
down_revision = '1e2cf5acc8c1'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=120), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('last_login_at', sa.DateTime(), nullable=True),
    sa.Column('current_login_at', sa.DateTime(), nullable=True),
    sa.Column('last_login_ip', sa.String(length=100), nullable=True),
    sa.Column('current_login_ip', sa.String(length=100), nullable=True),
    sa.Column('login_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('connections',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('provider_id', sa.String(length=255), nullable=True),
    sa.Column('provider_user_id', sa.String(length=255), nullable=True),
    sa.Column('access_token', sa.String(length=255), nullable=True),
    sa.Column('secret', sa.String(length=255), nullable=True),
    sa.Column('display_name', sa.String(length=255), nullable=True),
    sa.Column('profile_url', sa.String(length=512), nullable=True),
    sa.Column('image_url', sa.String(length=512), nullable=True),
    sa.Column('rank', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles_users',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint()
    )
    op.drop_table(u'post')
    op.drop_table(u'user')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(u'user',
    sa.Column(u'id', sa.INTEGER(), server_default="nextval('user_id_seq'::regclass)", nullable=False),
    sa.Column(u'nickname', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column(u'email', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column(u'role', sa.SMALLINT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint(u'id', name=u'user_pkey')
    )
    op.create_table(u'post',
    sa.Column(u'id', sa.INTEGER(), server_default="nextval('post_id_seq'::regclass)", nullable=False),
    sa.Column(u'body', sa.VARCHAR(length=140), autoincrement=False, nullable=True),
    sa.Column(u'timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column(u'user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], [u'user.id'], name=u'post_user_id_fkey'),
    sa.PrimaryKeyConstraint(u'id', name=u'post_pkey')
    )
    op.drop_table('roles_users')
    op.drop_table('connections')
    op.drop_table('roles')
    op.drop_table('users')
    ### end Alembic commands ###
