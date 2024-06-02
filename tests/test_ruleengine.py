import pytest
from mail_actions.ruleengine import (
    is_relative_date,
    build_date_filter_clause,
    build_string_filter_clause,
    build_sql,
)


def test_is_relative_date():
    # Test with valid relative dates
    assert is_relative_date("2 days") == True
    assert is_relative_date("2 months") == True
    assert is_relative_date("1 year") == True
    assert is_relative_date("3 hours") == True
    assert is_relative_date("30 minutes") == True
    assert is_relative_date("10 seconds") == True

    # Test with invalid relative dates
    assert is_relative_date("2 days ago") == False
    assert is_relative_date("2") == False
    assert is_relative_date("2d") == False
    # Test with non relative date
    assert is_relative_date("2022-12-23") == False

    # Test with empty value
    assert is_relative_date("") == False

    # Test with whitespace value
    assert is_relative_date("   ") == False


def test_build_date_filter_clause():
    # Test with valid filter
    filter = {"field": "date_received", "operator": "gt", "value": "2 days"}
    clause, values = build_date_filter_clause(filter)
    assert clause == "\"internalDate\" > datetime('now', ?)"
    assert values == ["-2 days"]

    # Test with invalid field
    filter = {"field": "invalid_field", "operator": "gt", "value": "2 days"}
    with pytest.raises(Exception):
        build_date_filter_clause(filter)

    # Test with invalid operator
    filter = {
        "field": "date_received",
        "operator": "invalid_operator",
        "value": "2 days",
    }
    with pytest.raises(Exception):
        build_date_filter_clause(filter)

    # Test with invalid value
    filter = {"field": "date_received", "operator": "gt"}
    with pytest.raises(Exception):
        build_date_filter_clause(filter)

    # Test with non relative Date

    filter = {"field": "date_received", "operator": "gt", "value": "2022-12-23"}

    clause, values = build_date_filter_clause(filter)
    assert clause == '"internalDate" > ?'
    assert values == ["2022-12-23"]

    # Test date_sent field to have labelIds LIKE %"SENT"%

    filter = {"field": "date_sent", "operator": "gt", "value": "2 days"}

    clause, values = build_date_filter_clause(filter)
    assert (
        clause == '( "internalDate" > datetime(\'now\', ?) AND labelIds LIKE %"SENT"% )'
    )
    assert values == ["-2 days"]


def test_build_string_filter_clause():
    # Test with valid filter
    filter = {"field": "subject", "operator": "contains", "value": "important"}
    clause, values = build_string_filter_clause(filter)
    assert clause == '"subject" LIKE ?'
    assert values == ["%important%"]

    # Test with invalid field
    filter = {"field": "invalid_field", "operator": "contains", "value": "important"}
    with pytest.raises(Exception):
        build_string_filter_clause(filter)

    # Test with invalid operator
    filter = {"field": "subject", "operator": "invalid_operator", "value": "important"}
    with pytest.raises(Exception):
        build_string_filter_clause(filter)

    # Test with empty value
    filter = {"field": "subject", "operator": "contains", "value": ""}
    clause, values = build_string_filter_clause(filter)
    assert clause == '"subject" LIKE ?'
    assert values == ["%%"]

    # Test with whitespace value
    filter = {"field": "subject", "operator": "contains", "value": "   "}
    clause, values = build_string_filter_clause(filter)
    assert clause == '"subject" LIKE ?'
    assert values == ["%   %"]


def test_build_sql():
    # Test with valid filters and match criteria "all"
    rule = {
        "filters": [
            {"field": "subject", "operator": "contains", "value": "important"},
            {"field": "date_received", "operator": "gt", "value": "2 days"},
        ],
        "match": "all",
    }
    sql, options = build_sql(rule)
    assert (
        sql
        == 'SELECT "id", "threadId", "historyId", "internalDate", "internalTimestamp", "from", "to", "subject", "labelIds", "payload__body__data", "payload__body__size", "payload__body__attachmentId", "payload__filename", "payload__mimeType", "payload__partId", "payload__parts", "raw", "sizeEstimate", "snippet" FROM messages WHERE "subject" LIKE ? AND "internalDate" > datetime(\'now\', ?)'
    )
    assert options == ["%important%", "-2 days"]

    # Test with valid filters and match criteria "any"
    rule = {
        "filters": [
            {"field": "subject", "operator": "contains", "value": "important"},
            {"field": "date_received", "operator": "gt", "value": "2 days"},
        ],
        "match": "any",
    }
    sql, options = build_sql(rule)
    assert (
        sql
        == 'SELECT "id", "threadId", "historyId", "internalDate", "internalTimestamp", "from", "to", "subject", "labelIds", "payload__body__data", "payload__body__size", "payload__body__attachmentId", "payload__filename", "payload__mimeType", "payload__partId", "payload__parts", "raw", "sizeEstimate", "snippet" FROM messages WHERE "subject" LIKE ? OR "internalDate" > datetime(\'now\', ?)'
    )
    assert options == ["%important%", "-2 days"]

    # Test with invalid filter match criteria
    rule = {
        "filters": [
            {"field": "subject", "operator": "contains", "value": "important"},
            {"field": "date_received", "operator": "gt", "value": "2 days"},
        ],
        "match": "invalid",
    }
    with pytest.raises(Exception):
        build_sql(rule)

    # Test with empty filters
    rule = {"filters": [], "match": "all"}
    sql, options = build_sql(rule)
    assert (
        sql
        == 'SELECT "id", "threadId", "historyId", "internalDate", "internalTimestamp", "from", "to", "subject", "labelIds", "payload__body__data", "payload__body__size", "payload__body__attachmentId", "payload__filename", "payload__mimeType", "payload__partId", "payload__parts", "raw", "sizeEstimate", "snippet" FROM messages WHERE '
    )
    assert options == []
