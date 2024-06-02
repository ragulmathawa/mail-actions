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


def load_rules() -> list[Rule]:
    schema = None
    with open("schema.json", "r") as stream:
        schema = yaml.safe_load(stream)
    rules = []
    with open("rules.yaml", "r") as stream:
        rules = yaml.safe_load(stream)
        try:
            validate(rules, schema)
        except Exception as e:
            raise Exception(f"Invalid rules file")
    return rules["rules"]
