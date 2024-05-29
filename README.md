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
  poetry run python -m mail_actions
  ```

## TODO

- Implement Rule Engine
- Implement Actions
  - Mark as Read
  - Mark as Unread
  - Move to Folder
  - Delete
  - Archive
- Error Handling all over the app
- Fallback & Retry Mechanism on Service API errors
- Save Sync State to resume on exit
- Implement Incremental Sync
- Throttling of Mailbox Full Sync
