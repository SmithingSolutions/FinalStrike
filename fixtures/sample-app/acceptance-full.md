> **Fixture status:** Tier 1 implemented (task list + create). Tier 2 actions
> (complete, delete) remain planned in `capabilities.yaml`.

## Feature: Task list

### Acceptance Criteria

- Tasks page loads at http://localhost:8080/tasks/ with page title "Sample App - Tasks"
- User can open the Tasks page and see the task list
- User can click "New Task", fill title and description, and save
- New task appears in the list with correct title
- API returns 200 on GET /api/tasks with a JSON array of tasks
- API returns 201 on POST /api/tasks with JSON body `{"title": "<title>", "description": "<optional>"}`
