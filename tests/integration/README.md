# Integration Tests

End-to-end integration tests for git-storyteller.

## Test Files

### `test_watch_list_e2e.py`

Tests the complete watch list workflow:

1. **Visit Each Repo Test**
   - Loads `config/watch_list.yaml`
   - Analyzes each enabled repository
   - Records the most recent commit hash
   - Saves to `output/e2e_history/watch_list_history.json`

2. **History Persistence Test**
   - Verifies commit history is saved between runs
   - Tracks first seen / last seen timestamps
   - Maintains list of all tracked commits

3. **Tweet Generation Test**
   - Generates tweet content for each repo
   - Validates tweet formatting
   - Ensures GitHub references are included

### `test_analyze_and_tweet.py`

Tests local repository analysis and tweet generation.

## History File Format

`output/e2e_history/watch_list_history.json`:
```json
{
  "repo_name": {
    "url": "https://github.com/owner/repo",
    "first_seen": "2026-02-17T...",
    "last_seen": "2026-02-17T...",
    "latest_commit": {
      "hash": "abc123...",
      "message": "Commit message",
      "date": "2026-02-17T...",
      "author": "Author Name"
    },
    "commits": [
      {
        "hash": "abc123...",
        "message": "Commit message",
        "date": "2026-02-17T...",
        "author": "Author Name",
        "first_seen": "2026-02-17T..."
      }
    ]
  }
}
```

## Running Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test
pytest tests/integration/test_watch_list_e2e.py -v

# Run directly
python3.12 tests/integration/test_watch_list_e2e.py
```

## Output

- **History file**: `output/e2e_history/watch_list_history.json`
- **Run results**: `output/e2e_history/run_YYYYMMDD_HHMMSS.json`

## Cleanup

To reset e2e history:
```bash
rm -rf output/e2e_history/
```
