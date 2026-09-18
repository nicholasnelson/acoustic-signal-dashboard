"""ORM models. Import this module wherever ``Base.metadata`` must know every table."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from acoustic_dashboard.db.base import Base


class Organisation(Base):
    """A tenant. Everything a customer owns is linked to an organisation via ``org_id``."""

    __tablename__ = "organisations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    #: Short URL-safe identifier, unique across all organisations
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"Organisation(slug={self.slug!r})"
