# registered-learners-bulk-upload

This script will extract users from the csrs/identity databases and attempt to insert the records into the new
`registered_learners` database.

## Setup

Requires: python -version 3

As always, first run `pip install -r requirements.txt`
- On Macbook `pip install -r requirements-macbook.txt`

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

| Argument                        | Description                                               |
|:--------------------------------|:----------------------------------------------------------|
| `report`, `teardown`, `execute` | Defines the operation to perform with the specified data. |

### Usage

To report on migration:
`python script.py report`

To teardown the registered_learners table:
`python script.py teardown`

To execute migration:
`python script.py execute`
