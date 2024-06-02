from gmail.mailbox import MailBox
from gmail.service import GMailService
from ruleparser import Rule, RuleFilter


class RuleEngine:

    def __init__(self, mailbox: MailBox, mailService: GMailService):
        self.mailbox = mailbox
        self.mailService = mailService

    def apply_rule(self, rule: Rule):
        (sql, opts) = build_sql(rule)

        for message in self.mailbox.get_messages_sql(sql, opts):
            print(
                f'{message.get("internalDate")} - {message.get("from_")}\n\t {message.get("subject")}'
            )
            self.mailbox.apply_action(rule["actions"], message)
        pass


def build_sql(rule: Rule) -> tuple[str, dict]:
    options = []
    clauses = []
    columns = [
        "id",
        "threadId",
        "historyId",
        "internalDate",
        "internalTimestamp",
        "from",
        "to",
        "subject",
        "labelIds",
        "payload__body__data",
        "payload__body__size",
        "payload__body__attachmentId",
        "payload__filename",
        "payload__mimeType",
        "payload__partId",
        "payload__parts",
        "raw",
        "sizeEstimate",
        "snippet",
    ]
    columns = [f'"{column}"' for column in columns]
    sql = "SELECT " + ", ".join(columns) + " FROM messages WHERE "
    for filter in rule.get("filters", []):
        if (filter.get("field") == "date_received") or (
            filter.get("field") == "date_sent"
        ):
            (clause, opt) = build_date_filter_clause(filter)
            clauses.append(clause)
            options.extend(opt)
        else:
            (clause, opt) = build_string_filter_clause(filter)
            clauses.append(clause)
            options.extend(opt)

    if rule.get("match") == "all":
        sql += " AND ".join(clauses)
    elif rule.get("match") == "any":
        sql += " OR ".join(clauses)
    else:
        raise Exception(f"Invalid filter match: {rule.get('match')}")

    return sql, options
    pass


def build_string_filter_clause(filter: RuleFilter) -> tuple[str, list]:
    columnMap = {
        "date_received": "date_received",
        "date_sent": "date_sent",
        "from": "from",
        "to": "to",
        "subject": "subject",
    }
    operatorMap = {
        "contains": "LIKE",
        "ncontains": "NOT LIKE",
        "eq": "=",
        "ne": "!=",
        "gt": ">",
        "lt": "<",
        "gte": ">=",
        "lte": "<=",
    }
    field = filter.get("field", "")
    column = columnMap.get(field, None)
    if column is None:
        raise Exception(f"Invalid field: {field}")

    operator = operatorMap.get(filter["operator"], None)
    if operator is None:
        raise Exception(f"Invalid operator: {filter['operator']}")

    value = filter.get("value", "")
    if operator in ["LIKE", "NOT LIKE"]:
        value = f"%{value}%"

    return f'"{column}" {operator} ?', [value]


def build_date_filter_clause(filter: RuleFilter) -> tuple[str, list]:
    columnMap = {
        "date_received": "internalDate",
        "date_sent": "internalDate",
        "from": "from",
        "to": "to",
        "subject": "subject",
    }
    operatorMap = {
        "eq": "=",
        "ne": "!=",
        "gt": ">",
        "lt": "<",
        "gte": ">=",
        "lte": "<=",
    }
    field = filter.get("field", "")
    column = columnMap.get(field, None)
    if column is None:
        raise Exception(f"Invalid field: {field}")

    operator = operatorMap.get(filter["operator"], None)
    if operator is None:
        raise Exception(f"Invalid operator: {filter['operator']}")

    value = filter["value"].strip()

    rhs = "?"
    if is_relative_date(value):
        rhs = f"datetime('now', ?)"
        value = f"-{value}"

    if field == "date_sent":
        # same column name for both date_received and date_sent, but the labelIds should include SENT for date_sent
        return f'( {column} {operator} {rhs} AND labelIds LIKE %"SENT"% )', [value]
    return f'"{column}" {operator} {rhs}', [value]


def is_relative_date(value: str) -> bool:
    if not value or value.strip() == "":
        return False
    parts = value.strip().split(" ")
    if len(parts) != 2:
        return False
    if not parts[0].isnumeric():
        return False
    return parts[1] in [
        "days",
        "months",
        "years",
        "hours",
        "minutes",
        "seconds",
        "day",
        "month",
        "year",
        "hour",
        "minute",
        "second",
    ]
