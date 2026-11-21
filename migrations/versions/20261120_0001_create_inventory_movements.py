"""Create inventory movements with stock traceability.

Revision ID: 20261120_0001
Revises:
Create Date: 2026-11-20
"""

from alembic import op
import sqlalchemy as sa


revision = "20261120_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "inventory_movements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("movement_type", sa.String(length=10), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("stock_before", sa.Integer(), nullable=False),
        sa.Column("stock_after", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_inventory_movement_quantity_positive",
        ),
        sa.CheckConstraint(
            "movement_type IN ('entry', 'exit')",
            name="ck_inventory_movement_type_valid",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_inventory_movements_product_id_products",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_inventory_movements_product_id",
        "inventory_movements",
        ["product_id"],
    )
    op.create_index(
        "ix_inventory_movements_movement_type",
        "inventory_movements",
        ["movement_type"],
    )


def downgrade():
    op.drop_index(
        "ix_inventory_movements_movement_type",
        table_name="inventory_movements",
    )
    op.drop_index(
        "ix_inventory_movements_product_id",
        table_name="inventory_movements",
    )
    op.drop_table("inventory_movements")
