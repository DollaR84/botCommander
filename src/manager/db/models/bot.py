from typing import Optional

from barsik.db.mixins import TimeCreateMixin, TimeUpdateMixin
from barsik.db.models.base import Base

import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.dialects.postgresql import JSONB

from services.types import ImageType, RestartPolicyType


class Bot(TimeCreateMixin, TimeUpdateMixin, Base):

    url: so.Mapped[str] = so.mapped_column(nullable=False, unique=True)
    token: so.Mapped[str] = so.mapped_column(nullable=False, unique=True)
    branch: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False, default="main")
    bot_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=True)
    image_type: so.Mapped[ImageType] = so.mapped_column(
        sa.Enum(ImageType, name="image_type", create_constraint=True, validate_strings=True),
        default=ImageType.BASE,
        nullable=False,
    )

    mem_reservation: so.Mapped[int] = so.mapped_column(nullable=False, default=20)
    mem_limit: so.Mapped[int] = so.mapped_column(nullable=False, default=64)

    cpu_quota_percents: so.Mapped[int] = so.mapped_column(nullable=False, default=20)
    cpu_period_percents: so.Mapped[int] = so.mapped_column(nullable=False, default=100)

    restart_policy: so.Mapped[RestartPolicyType] = so.mapped_column(
        sa.Enum(RestartPolicyType, name="restart_policy_type", create_constraint=True, validate_strings=True),
        default=RestartPolicyType.UNLESS_STOPPED,
        nullable=False,
    )

    is_active: so.Mapped[bool] = so.mapped_column(nullable=False, default=True)
    extra_env: so.Mapped[dict[str, str]] = so.mapped_column(
        JSONB,
        default=dict,
        server_default="{}",
        nullable=False,
    )

    chat_id: so.Mapped[Optional[int]] = so.mapped_column(sa.BigInteger, nullable=True)
    username: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=True)

    __table_args__ = (
        sa.CheckConstraint("mem_reservation >= 10", name="check_mem_reservation_min"),
        sa.CheckConstraint("mem_limit >= mem_reservation", name="check_mem_limit_ge_reservation"),
        sa.CheckConstraint("mem_limit <= 512", name="check_mem_limit_max"),
    )
