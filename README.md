# Mail Actions

Mail Actions is a Python CLI tool to perform actions on Gmail messages based on
Rules. It syncs the Inbox to a local SQLite Database and performs actions based
on the rules defined in the configuration file.

## Development

### Pre-requisites

- Poetry (Python Package Manager)
  [Install Poetry](https://python-poetry.org/docs/#installation)
- Python 3.11
- Gmail API Credentials
  - Create a Project in Google Cloud Console
  - Enable Gmail API
  - Create OAuth2 Credentials
  - Download Credentials JSON
  - Save it as `credentials.json` in the root of the project

### Setup

- Install Poetry
- Install Dependencies
  ```bash
  poetry install
  ```
- Run the App
  ```bash
  make run
  ```

## TODO

- Error Handling all over the app
- Fallback & Retry Mechanism on Service API errors
- Save Sync State to resume on exit
- Implement Incremental Sync
- Throttling of Mailbox Full Sync
- Implement Actions
  - Delete
  - Archive

## Rules Configuration

Rules are defined in the `rules.yaml` file. The file is structured as follows:

```yaml
rules:
  - name: "Rule 1"
    conditions:
      - field: "from"
        operator: "contains"
        value: "noreply"
    actions:
      - type: "read"
      - type: "move"
        value: "INBOX"
```

- `name`: Name of the Rule
- `conditions`: List of Conditions
  - `field`: Field to match against (from, to, subject, date_received,
    date_sent)
  - `operator`: Operator to use for matching (contains, equals, starts_with,
    ends_with)
  - `value`: Value to match against the field. For Date fields, it should be in
    the format `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS` or relative time like
    `2 days` or `1 month`.
- `actions`: List of Actions to perform if the conditions are met
  - `type`: Type of Action (read, unread, move)
  - `value`: Value for the Action (Folder Name for move) - Not required for
    `read` and `unread` actions

#### Relative Time

Relative Time can be used in the `value` field for Date fields. The following
formats are supported:

- `2 days` or `1 day`
- `2 months` or `1 months`
- `3 hours` or `1 hour`
- `5 minutes` or `1 minute`
- `1 years` or `1 year`
- `10 seconds` or `1 second`

Relative time is calculated from the current time when the rule is executed. for
example, `2 days` will calculate the time now - 2days
