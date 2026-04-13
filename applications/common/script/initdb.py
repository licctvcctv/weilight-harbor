import click
from flask.cli import with_appcontext


def init_db():
    """Initialize SQLite database with all tables."""
    from applications.extensions import db
    db.create_all()
    click.echo('Database tables created successfully!')
