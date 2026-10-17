# THREADS

Lead-thread registry. Edit only through checkpoint (`files` map, expected hash).
Keep the active thread and the last two handed-over ones; history is in git.

thread-id | role | status (active/handed-over) | since | checkpoint UUID
--- | --- | --- | --- | ---
lead-1 | lead | active | YYYY-MM-DD | UUID-of-registering-checkpoint
