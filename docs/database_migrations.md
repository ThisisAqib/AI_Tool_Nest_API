# Database Migrations Guide

This guide explains how to manage database migrations in the AI Tool Nest API project using Alembic with SQLModel and FastAPI.

## Overview

We use Alembic for managing database schema changes (migrations). Alembic provides:
- Version control for your database schema
- Automatic migration generation based on model changes
- Ability to upgrade and downgrade database schemas
- Support for async PostgreSQL operations

## Project Structure

```
alembic/
├── env.py              # Migration environment configuration
├── script.py.mako      # Template for migration files
└── versions/           # Directory containing migration files
    └── .gitkeep       # Placeholder for git
```

## Prerequisites

1. Make sure your database settings are configured in `.env`:
```env
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_database
```

## Common Migration Commands

### 1. Create a New Migration

To create a new migration after modifying models:

```bash
alembic revision --autogenerate -m "Description of changes"
```

This will:
- Compare your SQLModel models with the current database state
- Generate a new migration file in `alembic/versions/`
- Include both `upgrade()` and `downgrade()` operations

### 2. Apply Migrations

To apply all pending migrations:

```bash
alembic upgrade head
```

To apply a specific number of migrations:

```bash
alembic upgrade +1  # Apply next migration
```

### 3. Rollback Migrations

To undo the last migration:

```bash
alembic downgrade -1
```

To rollback to a specific migration:

```bash
alembic downgrade <revision_id>
```

### 4. View Migration Status

To see current migration status:

```bash
alembic current  # Show current revision
alembic history  # Show migration history
```

## Best Practices

1. **Always Review Migrations**
   - After generating a migration, review the file in `alembic/versions/`
   - Make sure the changes match your expectations
   - Test upgrades and downgrades in development first

2. **Meaningful Messages**
   - Use descriptive messages in your migration commands:
   ```bash
   alembic revision --autogenerate -m "Add user email verification fields"
   ```

3. **One Change Per Migration**
   - Keep migrations focused on a single change
   - Makes it easier to troubleshoot and rollback if needed

4. **Test Migration Flow**
   ```bash
   # Test cycle
   alembic upgrade head     # Apply migrations
   alembic downgrade -1     # Rollback one step
   alembic upgrade head     # Reapply
   ```

## Common Scenarios

### Adding a New Field

1. Add the field to your SQLModel model:
```python
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str  # Existing field
    verified: bool = Field(default=False)  # New field
```

2. Generate and apply migration:
```bash
alembic revision --autogenerate -m "Add user verification field"
alembic upgrade head
```

### Modifying a Field

1. Update the field in your model
2. Generate migration
3. Review the migration file carefully
4. Apply the migration

### Handling Errors

If you encounter errors:

1. Check the error message and migration file
2. Rollback if needed: `alembic downgrade -1`
3. Fix the issue in your models or migration file
4. Regenerate or modify the migration
5. Try upgrading again

## Production Considerations

1. **Backup First**
   - Always backup your database before applying migrations in production
   - Have a rollback plan ready

2. **Testing**
   - Test migrations on a copy of production data
   - Verify both upgrade and downgrade operations

3. **Deployment**
   - Include migration commands in your deployment process
   - Consider using migration scripts in your CI/CD pipeline

## Troubleshooting

### Common Issues

1. **"Target database is not up to date"**
   - Run `alembic current` to check status
   - Apply pending migrations: `alembic upgrade head`

2. **Autogenerate not detecting changes**
   - Ensure models are imported in `env.py`
   - Check if model inherits from SQLModel
   - Verify table=True is set on model

3. **Conflicts in migrations**
   - Rollback to last known good state
   - Regenerate migration with current state
   - Apply new migration

For more help, consult:
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/) 