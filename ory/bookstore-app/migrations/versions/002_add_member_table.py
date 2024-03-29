"""add member table

Revision ID: 6a9c9c35154a
Revises: 6fd914b623ca
Create Date: 2023-02-13 18:05:13.019705

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6a9c9c35154a"
down_revision = "6fd914b623ca"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "members",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("subject_id", sa.String(), nullable=True),
        sa.Column("publisher_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["publisher_id"],
            ["publishers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_members_id"), "members", ["id"], unique=False)
    op.create_index(
        op.f("ix_members_subject_id"), "members", ["subject_id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_members_subject_id"), table_name="members")
    op.drop_index(op.f("ix_members_id"), table_name="members")
    op.drop_table("members")
    # ### end Alembic commands ###
