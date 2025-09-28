"""Utility functions for the freelancer bot."""

import asyncio
import config
import json
import os

PROJECTS_FILE = "lookup_projects.json"

def lookup_load_projects():
    """Load projects from JSON file."""
    if not os.path.exists(PROJECTS_FILE):
        return []
    with open(PROJECTS_FILE, "r") as f:
        return json.load(f)

def lookup_save_projects(projects):
    """Save projects list back to JSON file."""
    with open(PROJECTS_FILE, "w") as f:
        json.dump(projects, f, indent=4)

def lookup_add_project(project_id):
    """Add a project to JSON store."""
    projects = lookup_load_projects()
    # Avoid duplicates
    if any(p["id"] == project_id for p in projects):
        return False
    projects.append({"id": project_id})
    lookup_save_projects(projects)
    return True

def lookup_delete_project(project_id):
    """Delete a project by ID."""
    projects = lookup_load_projects()
    projects = [p for p in projects if p["id"] != project_id]
    lookup_save_projects(projects)

def lookup_get_project(project_id):
    """Retrieve a project by ID."""
    projects = lookup_load_projects()
    for p in projects:
        if p["id"] == project_id:
            return p
    return None