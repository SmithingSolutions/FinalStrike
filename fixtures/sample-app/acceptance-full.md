> **Fixture status:** Tier 1–2 implemented (create, complete, delete). Tier 3
> interactions (search, settings, wizard) remain planned in `capabilities.yaml`.

## Feature: Task list (Tier 1)

### Acceptance Criteria

- Tasks page loads at http://localhost:8080/tasks/ with page title "Sample App - Tasks"
- User can open the Tasks page and see the task list
- User can click "New Task", fill title and description, and save
- New task appears in the list with correct title
- API returns 200 on GET /api/tasks with a JSON array of tasks
- API returns 201 on POST /api/tasks with JSON body `{"title": "<title>", "description": "<optional>"}`

## Feature: Task management (Tier 2)

### Acceptance Criteria

- User can click "Mark Done" on a task and see a Done badge with strikethrough title
- User can click "Mark Active" to clear the done state
- User can click "Delete", confirm with "Confirm Delete" in the modal, and the task is removed from the list
- User can click "Cancel" or press Escape to dismiss the delete modal without deleting
- User can click "Load Demo Tasks" to seed 15 tasks and scroll the task list
- API returns 200 on PATCH /api/tasks/{id} with JSON body `{"completed": true}` or `{"completed": false}`
- API returns 204 on DELETE /api/tasks/{id}
