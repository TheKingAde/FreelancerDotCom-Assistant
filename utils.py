"""Utility functions for the freelancer bot."""

import asyncio
import config
import json
import os

PROJECTS_FILE = "projects.json"

def load_projects():
    """Load projects from JSON file."""
    if not os.path.exists(PROJECTS_FILE):
        return []
    with open(PROJECTS_FILE, "r") as f:
        return json.load(f)

def save_projects(projects):
    """Save projects list back to JSON file."""
    with open(PROJECTS_FILE, "w") as f:
        json.dump(projects, f, indent=4)

def add_project(project_id, data, amount):
    """Add a project to JSON store."""
    projects = load_projects()
    # Avoid duplicates
    if any(p["id"] == project_id for p in projects):
        return False
    projects.append({"id": project_id, "data": data, "amount": amount})
    save_projects(projects)
    return True

def delete_project(project_id):
    """Delete a project by ID."""
    projects = load_projects()
    projects = [p for p in projects if p["id"] != project_id]
    save_projects(projects)

def get_project(project_id):
    """Retrieve a project by ID."""
    projects = load_projects()
    for p in projects:
        if p["id"] == project_id:
            return p
    return None

async def interruptible_sleep(hours, check_interval=60, shut_down_flag=lambda: False):
    """
    Sleeps for `hours` hours, but checks `shut_down_flag()` every `check_interval` seconds.
    If `shut_down_flag()` returns True, exits early.
    """
    total_seconds = int(hours * 3600)
    slept = 0
    while slept < total_seconds:
        if config.shutdown_flag:
            raise KeyboardInterrupt("Shutdown requested")
        await asyncio.sleep(min(check_interval, total_seconds - slept))
        slept += check_interval
