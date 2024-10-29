#!/usr/bin/env python3

import argparse
import psycopg2
import os
import json

# Database connection details (update as necessary)
DB_NAME = "your_db_name"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"
DB_HOST = "localhost"
DB_PORT = "5432"

# Fallback JSON file path
JSON_FILE = "tasks.json"

# Check for database availability
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        print("Database unavailable. Falling back to JSON file storage.")
        return None

# JSON-based storage functions
def read_tasks_from_json():
    """Read tasks from JSON file."""
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as f:
            return json.load(f)
    return []

def write_tasks_to_json(tasks):
    """Write tasks to JSON file."""
    with open(JSON_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def add_task(description, use_db=True):
    """Add a new task to the database or JSON file."""
    if use_db:
        conn = get_db_connection()
        if conn:
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "INSERT INTO tasks (description) VALUES (%s) RETURNING id",
                            (description,)
                        )
                        task_id = cur.fetchone()[0]
                        print(f'Task added successfully (ID: {task_id})')
            finally:
                conn.close()
            return
    # Fallback to JSON
    tasks = read_tasks_from_json()
    task_id = tasks[-1]["id"] + 1 if tasks else 1
    tasks.append({"id": task_id, "description": description, "status": "todo"})
    write_tasks_to_json(tasks)
    print(f'Task added successfully (ID: {task_id})')

def update_task(task_id, new_description, use_db=True):
    """Update an existing task's description in the database or JSON file."""
    if use_db:
        conn = get_db_connection()
        if conn:
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "UPDATE tasks SET description = %s WHERE id = %s",
                            (new_description, task_id)
                        )
                        if cur.rowcount > 0:
                            print(f"Task {task_id} updated successfully.")
                        else:
                            print(f"Task with ID {task_id} does not exist.")
            finally:
                conn.close()
            return
    # Fallback to JSON
    tasks = read_tasks_from_json()
    for task in tasks:
        if task["id"] == task_id:
            task["description"] = new_description
            write_tasks_to_json(tasks)
            print(f"Task {task_id} updated successfully.")
            return
    print(f"Task with ID {task_id} does not exist.")

def delete_task(task_id, use_db=True):
    """Delete a task by ID from the database or JSON file."""
    if use_db:
        conn = get_db_connection()
        if conn:
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                        if cur.rowcount > 0:
                            print(f"Task {task_id} deleted successfully.")
                        else:
                            print(f"Task with ID {task_id} does not exist.")
            finally:
                conn.close()
            return
    # Fallback to JSON
    tasks = read_tasks_from_json()
    updated_tasks = [task for task in tasks if task["id"] != task_id]
    if len(updated_tasks) < len(tasks):
        write_tasks_to_json(updated_tasks)
        print(f"Task {task_id} deleted successfully.")
    else:
        print(f"Task with ID {task_id} does not exist.")

def mark_task_status(task_id, status, use_db=True):
    """Mark a task with a specific status in the database or JSON file."""
    if use_db:
        conn = get_db_connection()
        if conn:
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "UPDATE tasks SET status = %s WHERE id = %s",
                            (status, task_id)
                        )
                        if cur.rowcount > 0:
                            print(f"Task {task_id} marked as {status}.")
                        else:
                            print(f"Task with ID {task_id} does not exist.")
            finally:
                conn.close()
            return
    # Fallback to JSON
    tasks = read_tasks_from_json()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = status
            write_tasks_to_json(tasks)
            print(f"Task {task_id} marked as {status}.")
            return
    print(f"Task with ID {task_id} does not exist.")

def list_tasks(status=None, use_db=True):
    """List all tasks or filter by status from the database or JSON file."""
    if use_db:
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    if status:
                        cur.execute(
                            "SELECT id, description, status FROM tasks WHERE status = %s ORDER BY id",
                            (status,)
                        )
                    else:
                        cur.execute("SELECT id, description, status FROM tasks ORDER BY id")
                    tasks = cur.fetchall()

                    if tasks:
                        print("Tasks:")
                        for task in tasks:
                            print(f"{task[0]}. {task[1]} [{task[2]}]")
                    else:
                        print("No tasks found.")
            finally:
                conn.close()
            return
    # Fallback to JSON
    tasks = read_tasks_from_json()
    filtered_tasks = tasks if not status else [task for task in tasks if task["status"] == status]
    if filtered_tasks:
        print("Tasks:")
        for task in filtered_tasks:
            print(f"{task['id']}. {task['description']} [{task['status']}]")
    else:
        print("No tasks found.")

def main():
    parser = argparse.ArgumentParser(description="Task management CLI with PostgreSQL and JSON fallback")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Define the commands
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("task", type=str, help="The task description")

    update_parser = subparsers.add_parser("update", help="Update an existing task's description")
    update_parser.add_argument("task_id", type=int, help="The ID of the task to update")
    update_parser.add_argument("new_description", type=str, help="The new task description")

    delete_parser = subparsers.add_parser("delete", help="Delete a task by ID")
    delete_parser.add_argument("task_id", type=int, help="The ID of the task to delete")

    in_progress_parser = subparsers.add_parser("mark-in-progress", help="Mark a task as in-progress")
    in_progress_parser.add_argument("task_id", type=int, help="The ID of the task to mark as in-progress")

    done_parser = subparsers.add_parser("mark-done", help="Mark a task as done")
    done_parser.add_argument("task_id", type=int, help="The ID of the task to mark as done")

    list_parser = subparsers.add_parser("list", help="List all tasks or filter by status")
    list_parser.add_argument("status", type=str, choices=["todo", "in-progress", "done"], nargs="?", help="Filter tasks by status")

    args = parser.parse_args()
    use_db = get_db_connection() is not None  # Determine storage method based on DB availability

    # Dispatch commands
    if args.command == "add":
        add_task(args.task, use_db)
    elif args.command == "update":
        update_task(args.task_id, args.new_description, use_db)
    elif args.command == "delete":
        delete_task(args.task_id, use_db)
    elif args.command == "mark-in-progress":
        mark_task_status(args.task_id, "in-progress", use_db)
    elif args.command == "mark-done":
        mark_task_status(args.task_id, "done", use_db)
    elif args.command == "list":
        list_tasks(args.status, use_db)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
