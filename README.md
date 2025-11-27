# registered-learners-bulk-upload

This script will extract users from the csrs/identity databases and attempt to insert the records into the new
`registered_learners` database.

## Setup

As always, first run `pip install -r requirements.txt`

Set the following properties in a `.env` file (or as system env vars):

- MYSQL_HOST
- MYSQL_USER
- MYSQL_PASSWORD
- PG_HOST
- PG_PASSWORD
- PG_USER

Optionally set the following properties:

- `PAGE_SIZE` (page size to use when fetching users)

## Run

The script uses the following arguments:

| Argument     | Description                                               | Choices                         | Default  | Example Usage      |
|:-------------|:----------------------------------------------------------|:--------------------------------|:---------|:-------------------|
| **`action`** | Defines the operation to perform with the specified data. | `report`, `execute`, `teardown` | `report` | `--action execute` |                           

### Example usage

To report on migration:
`python3 script.py report`

To execute migration:
`python3 script.py execute`

To teardown the registered_learners table:
`python3 script.py teardown`
