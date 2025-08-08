"""Switch money to Numeric(12,2), dates to DateTime, add FKs & indexes

Revision ID: 3f9d1b7a4a6c
Revises: 82f4e758ad31
Create Date: 2025-08-08 12:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "3f9d1b7a4a6c"
down_revision = "82f4e758ad31"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    # --- 0) SQLite safety: убираем хвосты от упавших батчей
    if bind.dialect.name == "sqlite":
        insp = sa.inspect(bind)
        for tmp in ("_alembic_tmp_users", "_alembic_tmp_item_values"):
            if tmp in insp.get_table_names():
                op.execute(sa.text(f'DROP TABLE "{tmp}"'))

    # --- 1) Дедупликация item_values перед добавлением UNIQUE(item_name, value)
    # Оставляем запись с минимальным id в каждой группе (item_name, value), остальные удаляем.
    # учитываем NULL в value через COALESCE, чтобы NULL==NULL для группировки.
    op.execute(sa.text("""
        DELETE FROM item_values
        WHERE EXISTS (
          SELECT 1
          FROM item_values iv2
          WHERE iv2.item_name = item_values.item_name
            AND COALESCE(iv2.value,'') = COALESCE(item_values.value,'')
            AND iv2.id < item_values.id
        )
    """))

    op.execute("""
            UPDATE users
            SET registration_date = CURRENT_TIMESTAMP
            WHERE registration_date IS NULL OR registration_date = ''
        """)
    op.execute("""
            UPDATE users
            SET registration_date = CURRENT_TIMESTAMP
            WHERE typeof(registration_date) NOT IN ('text', 'null')
        """)


    # --- 2) USERS (batch, FK строго ВНУТРИ batch!)
    with op.batch_alter_table("users", schema=None) as batch:
        batch.alter_column(
            "registration_date",
            existing_type=sa.VARCHAR(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
        batch.alter_column(
            "balance",
            existing_type=sa.BigInteger(),
            type_=sa.Numeric(12, 2),
            existing_nullable=False,
            server_default="0",
        )
        batch.create_index("ix_users_role_id", ["role_id"], unique=False)
        batch.create_index("ix_users_referral_id", ["referral_id"], unique=False)

        batch.create_foreign_key(
            "fk_users_referral_id_users",
            referent_table="users",
            local_cols=["referral_id"],
            remote_cols=["telegram_id"],
            ondelete="SET NULL",
        )
        batch.create_foreign_key(
            "fk_users_role_id_roles",
            referent_table="roles",
            local_cols=["role_id"],
            remote_cols=["id"],
            ondelete="RESTRICT",
        )

    # GOODS
    with op.batch_alter_table("goods", schema=None) as batch:
        batch.alter_column(
            "price",
            existing_type=sa.BigInteger(),
            type_=sa.Numeric(12, 2),
            existing_nullable=False,
        )
        batch.create_index("ix_goods_category_name", ["category_name"], unique=False)

    # ITEM_VALUES
    with op.batch_alter_table("item_values", schema=None) as batch:
        batch.create_unique_constraint("uq_item_value_per_item", ["item_name", "value"])
        batch.create_index("ix_item_values_item_inf", ["item_name", "is_infinity"], unique=False)

    # BOUGHT_GOODS
    with op.batch_alter_table("bought_goods", schema=None) as batch:
        batch.alter_column(
            "bought_datetime",
            existing_type=sa.VARCHAR(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
        batch.alter_column(
            "price",
            existing_type=sa.BigInteger(),
            type_=sa.Numeric(12, 2),
            existing_nullable=False,
        )
        batch.create_index("ix_bought_goods_buyer_id", ["buyer_id"], unique=False)
    # составной индекс под запросы
    op.create_index(
        "ix_bought_goods_buyer_time",
        "bought_goods",
        ["buyer_id", sa.text("bought_datetime DESC")],
        unique=False,
    )

    # OPERATIONS
    with op.batch_alter_table("operations", schema=None) as batch:
        batch.alter_column(
            "operation_time",
            existing_type=sa.VARCHAR(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
        batch.alter_column(
            "operation_value",
            existing_type=sa.BigInteger(),
            type_=sa.Numeric(12, 2),
            existing_nullable=False,
        )
        batch.create_index("ix_operations_user_id", ["user_id"], unique=False)
    op.create_index(
        "ix_operations_user_time",
        "operations",
        ["user_id", sa.text("operation_time DESC")],
        unique=False,
    )

    # UNFINISHED_OPERATIONS
    with op.batch_alter_table("unfinished_operations", schema=None) as batch:
        batch.alter_column(
            "operation_value",
            existing_type=sa.BigInteger(),
            type_=sa.Numeric(12, 2),
            existing_nullable=False,
        )
        batch.alter_column(
            "operation_id",
            existing_type=sa.String(length=500),
            type_=sa.String(length=128),
            existing_nullable=False,
        )
        # created_at (если поля не было)
        batch.add_column(
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            )
        )
        batch.create_index(
            "ix_unfinished_operations_user_id", ["user_id"], unique=False
        )
        batch.create_index(
            "ix_unfinished_operations_operation_id", ["operation_id"], unique=True
        )


def downgrade():
    # UNFINISHED_OPERATIONS
    with op.batch_alter_table("unfinished_operations", schema=None) as batch:
        batch.drop_index("ix_unfinished_operations_operation_id")
        batch.drop_index("ix_unfinished_operations_user_id")
        batch.drop_column("created_at")
        batch.alter_column(
            "operation_id",
            existing_type=sa.String(length=128),
            type_=sa.String(length=500),
            existing_nullable=False,
        )
        batch.alter_column(
            "operation_value",
            existing_type=sa.Numeric(12, 2),
            type_=sa.BigInteger(),
            existing_nullable=False,
        )

    # OPERATIONS
    op.drop_index("ix_operations_user_time", table_name="operations")
    with op.batch_alter_table("operations", schema=None) as batch:
        batch.drop_index("ix_operations_user_id")
        batch.alter_column(
            "operation_value",
            existing_type=sa.Numeric(12, 2),
            type_=sa.BigInteger(),
            existing_nullable=False,
        )
        batch.alter_column(
            "operation_time",
            existing_type=sa.DateTime(timezone=True),
            type_=sa.VARCHAR(),
            existing_nullable=False,
        )

    # BOUGHT_GOODS
    op.drop_index("ix_bought_goods_buyer_time", table_name="bought_goods")
    with op.batch_alter_table("bought_goods", schema=None) as batch:
        batch.drop_index("ix_bought_goods_buyer_id")
        batch.alter_column(
            "price",
            existing_type=sa.Numeric(12, 2),
            type_=sa.BigInteger(),
            existing_nullable=False,
        )
        batch.alter_column(
            "bought_datetime",
            existing_type=sa.DateTime(timezone=True),
            type_=sa.VARCHAR(),
            existing_nullable=False,
        )

    # ITEM_VALUES
    with op.batch_alter_table("item_values", schema=None) as batch:
        batch.drop_index("ix_item_values_item_inf")
        batch.drop_constraint("uq_item_value_per_item", type_="unique")

    # GOODS
    with op.batch_alter_table("goods", schema=None) as batch:
        batch.drop_index("ix_goods_category_name")
        batch.alter_column(
            "price",
            existing_type=sa.Numeric(12, 2),
            type_=sa.BigInteger(),
            existing_nullable=False,
        )

    # USERS
    op.drop_constraint("fk_users_role_id_roles", "users", type_="foreignkey")
    op.drop_constraint("fk_users_referral_id_users", "users", type_="foreignkey")
    with op.batch_alter_table("users", schema=None) as batch:
        batch.drop_index("ix_users_referral_id")
        batch.drop_index("ix_users_role_id")
        batch.alter_column(
            "balance",
            existing_type=sa.Numeric(12, 2),
            type_=sa.BigInteger(),
            existing_nullable=False,
        )
        batch.alter_column(
            "registration_date",
            existing_type=sa.DateTime(timezone=True),
            type_=sa.VARCHAR(),
            existing_nullable=False,
        )
