"""Migrations and the Organisation model, against real Postgres."""

import asyncio
from pathlib import Path

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError

from acoustic_dashboard.api.deps import Session
from acoustic_dashboard.config import Settings
from acoustic_dashboard.db import migrate
from acoustic_dashboard.db.models import Organisation
from acoustic_dashboard.db.session import make_engine, make_sessionmaker
from acoustic_dashboard.main import create_app


async def current_revision(url: str) -> str | None:
    engine = make_engine(url)
    try:
        async with engine.connect() as conn:
            return await conn.scalar(text("select version_num from alembic_version"))
    finally:
        await engine.dispose()


def test_app_startup_migrates_to_head(test_database_url: str):
    """Lifespan runs `alembic upgrade head`, so a fresh DB comes up fully migrated."""
    migrate.downgrade(test_database_url)
    app = create_app(Settings(database_url=test_database_url))

    with TestClient(app) as client:
        assert client.get("/api/health").status_code == 200

    assert asyncio.run(current_revision(test_database_url)) == migrate.head_revision(
        test_database_url
    )


async def test_organisations_schema(migrated_db: str):
    engine = make_engine(migrated_db)
    try:
        async with engine.connect() as conn:
            columns = await conn.run_sync(
                lambda c: {col["name"]: col for col in inspect(c).get_columns("organisations")}
            )
            uniques = await conn.run_sync(
                lambda c: inspect(c).get_unique_constraints("organisations")
            )
    finally:
        await engine.dispose()

    assert set(columns) == {"id", "name", "slug", "created_at"}
    assert all(not col["nullable"] for col in columns.values())
    assert [u["column_names"] for u in uniques] == [["slug"]]


async def test_organisation_round_trip(migrated_db: str):
    engine = make_engine(migrated_db)
    sessions = make_sessionmaker(engine)
    try:
        async with sessions() as session:
            session.add(Organisation(name="Acme Pumps", slug="acme"))
            await session.commit()

        async with sessions() as session:
            org = (
                await session.execute(select(Organisation).where(Organisation.slug == "acme"))
            ).scalar_one()
            assert org.name == "Acme Pumps"
            assert org.id is not None
            assert org.created_at.tzinfo is not None

        async with sessions() as session:
            session.add(Organisation(name="Acme again", slug="acme"))
            with pytest.raises(IntegrityError):
                await session.commit()
    finally:
        async with engine.begin() as conn:
            await conn.execute(text("delete from organisations"))
        await engine.dispose()


def test_session_dependency(migrated_db: str, tmp_path: Path):
    """`get_session` hands routes a working session bound to the app's engine."""
    probe = APIRouter()

    @probe.get("/probe")
    async def count_orgs(session: Session) -> int:
        return len((await session.execute(select(Organisation))).scalars().all())

    # No static dir: the SPA catch-all would otherwise shadow a router added late.
    app = create_app(
        Settings(database_url=migrated_db, run_migrations=False, static_dir=tmp_path / "none")
    )
    app.include_router(probe, prefix="/api")

    with TestClient(app) as client:
        assert client.get("/api/probe").json() == 0
