import argparse

from csrs import get_all_users
from log import get_logger
from registered_learners import insert_registered_learners, delete_registered_learners

logger = get_logger("script")


def run(execute=False):
    logger.info("Fetching all users")
    users = get_all_users()
    logger.info(f"Found {len(users)} users. Creating registered learner DB rows.")
    if execute:
        insert_registered_learners(users)
    else:
        logger.info("execute flag not passed. Skipping.")


def get_args():
    parser = argparse.ArgumentParser(description="Process")
    valid_action_choices = ["report", "execute", "teardown"]
    parser.add_argument(
        "action",
        choices=valid_action_choices,
        default="report",
        help=f"Specify the action to perform: valid choices are {valid_action_choices}."
    )

    return parser.parse_args()


def teardown():
    logger.info("Tearing down data")
    delete_registered_learners()


if __name__ == "__main__":
    args = get_args()
    if args.action == "teardown":
        teardown()
    else:
        run(args.action == "execute")
