"""Database operations for freelancer bot."""

import sqlite3

# Initialize database
conn = sqlite3.connect("bidded_projects.db")
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id TEXT UNIQUE
    )
""")
conn.commit()

def project_id_exists(project_id):
    """Check if project ID exists in database."""
    c.execute("SELECT 1 FROM keys WHERE project_id = ?", (project_id,))
    return c.fetchone() is not None

def store_project_keys(project_id):
    """Store project ID in database."""
    c.execute("INSERT OR IGNORE INTO keys (project_id) VALUES (?)",
            (project_id,))
    conn.commit()

def get_all_project_ids():
    """Retrieve all project IDs from the database."""
    c.execute("SELECT project_id FROM keys")
    return [row[0] for row in c.fetchall()]

def delete_project_by_id(project_id):
    """Delete a project from the database by its project ID."""
    c.execute("DELETE FROM keys WHERE project_id = ?", (project_id,))
    conn.commit()
