"""Initial migration.

Revision ID: 695370dd866b
Revises: 
Create Date: 2025-03-25 21:32:36.119907

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '695370dd866b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('domain',
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('screener',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('disorder', sa.String(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=False),
    sa.Column('display_name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('question',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('domain', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['domain'], ['domain.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('screener_section',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('screener_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['screener_id'], ['screener.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('answer_option',
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.Column('screener_section_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['screener_section_id'], ['screener_section.id'], ),
    sa.PrimaryKeyConstraint('title')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('answer_option')
    op.drop_table('screener_section')
    op.drop_table('question')
    op.drop_table('screener')
    op.drop_table('domain')
    # ### end Alembic commands ###
