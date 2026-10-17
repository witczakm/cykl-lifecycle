# NOW draft

The writer renders canonical docs/NOW.md and supplies identity/hash fields.
Pass this JSON as checkpoint --input after replacing generic identity and goal:

```json
{
  "repo": "example/project",
  "branch": "work",
  "goal": "Deliver the agreed outcome",
  "position": "Offline; authority has not been refreshed",
  "next": "Verify the next task against its acceptance criteria",
  "preserve": [],
  "work": {},
  "risks": [],
  "references": []
}
```

Use --expected absent only for a new lifecycle root. For updates, pass the current
NOW content_sha256. A checkpoint card is emitted only after validation and persistence.
