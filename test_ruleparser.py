import pytest
import ruleparser


def test_load_rules():

    # Test that the function raises an exception if the rules file is invalid

    with pytest.raises(Exception):
        ruleparser.load_rules("./tests/invalid_rules.yaml")

    # Test that the function raises an exception if the rules file is missing
    with pytest.raises(Exception):
        ruleparser.load_rules("./tests/missing_file.yaml")
