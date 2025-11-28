# registered-learners-bulk-upload

This script will read users information from the `csrs` and `identity` schemas in `MySql DB` and bulk insert
the records into the `registered_learners` table of the reporting schema in `PostgreSQL DB`.

## Setup

Requires: python (version 3)

Install the required dependencies:
- run `pip install -r requirements.txt`
- or for Macbook run `pip install -r requirements-macbook.txt`

Set the following properties in a `.env` file (or as system env vars):

- MYSQL_HOST
- MYSQL_USER
- MYSQL_PASSWORD
- PG_HOST
- PG_PASSWORD
- PG_USER
- PAGE_SIZE (page size to use when fetching users)

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
