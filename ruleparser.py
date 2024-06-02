from typing import TypedDict
import yaml as yaml
from jsonschema import validate


class RuleFilter(TypedDict):
    field: str
    operator: str
    value: str


class RuleAction(TypedDict):
    type: str
    value: str


class Rule(TypedDict):
    name: str
    match: str
    filters: list[RuleFilter]
    actions: list[RuleAction]


SCHEMA_FILE = "schema.json"


def load_rules(rules_file) -> list[Rule]:
    """
    Load rules from the 'rules.yaml' file and validate them against the 'schema.json' file.

    Returns:
        A list of Rule objects representing the loaded rules.

    Raises:
        Exception: If the rules file is invalid.
    """
    schema = None
    with open(SCHEMA_FILE, "r") as stream:
        schema = yaml.safe_load(stream)
    rules = []
    with open(rules_file, "r") as stream:
        rules = yaml.safe_load(stream)
        try:
            validate(rules, schema)
        except Exception as e:
            raise Exception(f"Invalid rules file")
    return rules["rules"]
