"""Database layer: SQLAlchemy 2 (async) models and Alembic migrations.

- ``base``        declarative base + constraint naming convention
- ``models``      ORM tables
- ``session``     engine / session factories
- ``migrate``     run Alembic programmatically (used at app startup)
- ``migrations``  the Alembic environment and versioned scripts

Every table that belongs to an organisation must carry a non-null ``org_id``
(see issue #4). Reviewers: reject migrations that add a tenant table without one.
"""
