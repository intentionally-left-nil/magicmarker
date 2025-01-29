import re

import pytest
from packaging.version import Version

from markerpry.node import BooleanNode, Environment, ExpressionNode, Node, OperatorNode
from markerpry.parser import parse

# Basic string comparison tests
string_testdata = [
    (
        "string_equality_true",
        ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
        {"os_name": ["posix"]},
        BooleanNode(True),
    ),
    (
        "string_equality_false",
        ExpressionNode(lhs="os_name", comparator="==", rhs="nt"),
        {"os_name": ["posix"]},
        BooleanNode(False),
    ),
    (
        "string_inequality_true",
        ExpressionNode(lhs="os_name", comparator="!=", rhs="nt"),
        {"os_name": ["posix"]},
        BooleanNode(True),
    ),
    (
        "string_inequality_false",
        ExpressionNode(lhs="os_name", comparator="!=", rhs="posix"),
        {"os_name": ["posix"]},
        BooleanNode(False),
    ),
    (
        "string_invalid_operator",
        ExpressionNode(lhs="os_name", comparator=">", rhs="posix"),
        {"os_name": ["posix"]},
        ExpressionNode(lhs="os_name", comparator=">", rhs="posix"),
    ),
    (
        "string_in_operator",
        ExpressionNode(lhs="os_name", comparator="in", rhs="posix"),
        {"os_name": ["posix"]},
        BooleanNode(True),
    ),
    (
        "string_not_in_operator",
        ExpressionNode(lhs="os_name", comparator="not in", rhs="posix"),
        {"os_name": ["posix"]},
        BooleanNode(False),
    ),
]


@pytest.mark.parametrize(
    "name,expr,env,expected",
    string_testdata,
    ids=[x[0] for x in string_testdata],
)
def test_string_evaluate(name: str, expr: ExpressionNode, env: Environment, expected: Node):
    result = expr.evaluate(env)
    assert result == expected


# Resolved attribute tests
resolved_testdata = [
    (
        "string_equality_true",
        ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
        {"os_name": ["posix"]},
        True,
    ),
    (
        "string_equality_false",
        ExpressionNode(lhs="os_name", comparator="==", rhs="nt"),
        {"os_name": ["posix"]},
        True,
    ),
    (
        "string_equality_incomplete",
        ExpressionNode(lhs="os_name", comparator="==", rhs="nt"),
        {"python_version": [Version("3.7")]},
        False,
    ),
]


@pytest.mark.parametrize(
    "name,expr,env,expected",
    resolved_testdata,
    ids=[x[0] for x in resolved_testdata],
)
def test_resolved_attribute_on_evaluate(name: str, expr: ExpressionNode, env: Environment, expected: bool):
    result = expr.evaluate(env)
    assert result.resolved == expected


# Version comparison tests
version_testdata = [
    (
        "version_greater_than_true",
        ExpressionNode(lhs="python_version", comparator=">", rhs="3.7"),
        {"python_version": [Version("3.8")]},
        BooleanNode(True),
    ),
    (
        "version_greater_than_false",
        ExpressionNode(lhs="python_version", comparator=">", rhs="3.8"),
        {"python_version": [Version("3.7")]},
        BooleanNode(False),
    ),
    (
        "version_greater_equal_true",
        ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
        {"python_version": [Version("3.8")]},
        BooleanNode(True),
    ),
    (
        "version_less_than_true",
        ExpressionNode(lhs="python_version", comparator="<", rhs="3.8"),
        {"python_version": [Version("3.7")]},
        BooleanNode(True),
    ),
    (
        "version_less_equal_true",
        ExpressionNode(lhs="python_version", comparator="<=", rhs="3.8"),
        {"python_version": [Version("3.8")]},
        BooleanNode(True),
    ),
    (
        "version_in_true",
        ExpressionNode(lhs="python_version", comparator="in", rhs="2.7"),
        {"python_version": [Version("2.7")]},
        BooleanNode(True),
    ),
    (
        "version_not_in_false",
        ExpressionNode(lhs="python_version", comparator="not in", rhs="2.7"),
        {"python_version": [Version("2.7")]},
        BooleanNode(False),
    ),
]


@pytest.mark.parametrize(
    "name,expr,env,expected",
    version_testdata,
    ids=[x[0] for x in version_testdata],
)
def test_version_evaluate(name: str, expr: ExpressionNode, env: Environment, expected: Node):
    result = expr.evaluate(env)
    assert result == expected


# Multiple value tests
multiple_value_testdata = [
    (
        "multiple_values_match_first",
        ExpressionNode(lhs="python_version", comparator="==", rhs="3.8"),
        {"python_version": [Version("3.7"), Version("3.8"), Version("3.9")]},
        BooleanNode(True),
    ),
    (
        "multiple_values_match_none",
        ExpressionNode(lhs="python_version", comparator="==", rhs="3.6"),
        {"python_version": [Version("3.7"), Version("3.8"), Version("3.9")]},
        BooleanNode(False),
    ),
]


@pytest.mark.parametrize(
    "name,expr,env,expected",
    multiple_value_testdata,
    ids=[x[0] for x in multiple_value_testdata],
)
def test_multiple_values_evaluate(name: str, expr: ExpressionNode, env: Environment, expected: Node):
    result = expr.evaluate(env)
    assert result == expected


# Missing environment tests
missing_env_testdata = [
    (
        "missing_key",
        ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
        {},
        ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
    ),
    (
        "empty_value_list",
        ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
        {"python_version": []},
        ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
    ),
    (
        "different_key_present",
        ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
        {"os_name": ["posix"]},
        ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
    ),
]


@pytest.mark.parametrize(
    "name,expr,env,expected",
    missing_env_testdata,
    ids=[x[0] for x in missing_env_testdata],
)
def test_missing_env_evaluate(name: str, expr: ExpressionNode, env: Environment, expected: Node):
    result = expr.evaluate(env)
    assert result == expected


# Regex pattern tests
regex_testdata = [
    (
        "regex_exact_match_true",
        ExpressionNode(lhs="sys_platform", comparator="==", rhs="linux"),
        {"sys_platform": [re.compile("linux")]},
        BooleanNode(True),
    ),
    (
        "regex_exact_match_false",
        ExpressionNode(lhs="sys_platform", comparator="==", rhs="darwin"),
        {"sys_platform": [re.compile("linux")]},
        BooleanNode(False),
    ),
    (
        "regex_pattern_match_true",
        ExpressionNode(lhs="sys_platform", comparator="==", rhs="linux2"),
        {"sys_platform": [re.compile("linux.*")]},
        BooleanNode(True),
    ),
    (
        "regex_pattern_match_false",
        ExpressionNode(lhs="sys_platform", comparator="==", rhs="darwin"),
        {"sys_platform": [re.compile("linux.*")]},
        BooleanNode(False),
    ),
    (
        "regex_inequality_true",
        ExpressionNode(lhs="sys_platform", comparator="!=", rhs="darwin"),
        {"sys_platform": [re.compile("linux.*")]},
        BooleanNode(True),
    ),
    (
        "regex_inequality_false",
        ExpressionNode(lhs="sys_platform", comparator="!=", rhs="linux2"),
        {"sys_platform": [re.compile("linux.*")]},
        BooleanNode(False),
    ),
    (
        "regex_invalid_operator",
        ExpressionNode(lhs="sys_platform", comparator=">", rhs="linux"),
        {"sys_platform": [re.compile("linux.*")]},
        ExpressionNode(lhs="sys_platform", comparator=">", rhs="linux"),
    ),
    (
        "regex_multiple_patterns",
        ExpressionNode(lhs="sys_platform", comparator="==", rhs="linux2"),
        {
            "sys_platform": [
                re.compile("darwin.*"),
                re.compile("linux.*"),
                re.compile("win32"),
            ]
        },
        BooleanNode(True),
    ),
]


@pytest.mark.parametrize(
    "name,expr,env,expected",
    regex_testdata,
    ids=[x[0] for x in regex_testdata],
)
def test_regex_evaluate(name: str, expr: ExpressionNode, env: Environment, expected: Node):
    result = expr.evaluate(env)
    assert result == expected


# Boolean literal tests
boolean_literal_testdata = [
    (
        "boolean_literal_true",
        ExpressionNode("python_implementation", "==", "CPython"),
        {"python_implementation": [True]},
        BooleanNode(True),
    ),
    (
        "boolean_literal_false",
        ExpressionNode("python_implementation", "==", "CPython"),
        {"python_implementation": [False]},
        BooleanNode(False),
    ),
    (
        "boolean_true_with_other_values",
        ExpressionNode("python_implementation", "==", "CPython"),
        {"python_implementation": ["PyPy", True, "CPython"]},
        BooleanNode(True),
    ),
    (
        "boolean_false_with_other_values",
        ExpressionNode("python_implementation", "==", "CPython"),
        {"python_implementation": ["CPython", False, "CPython"]},
        BooleanNode(False),
    ),
    (
        "boolean_in_and_operator",
        OperatorNode(
            operator="and",
            _left=ExpressionNode("python_implementation", "==", "CPython"),
            _right=ExpressionNode("python_version", ">=", "3.7"),
        ),
        {
            "python_implementation": [True],
            "python_version": [Version("3.8")],
        },
        BooleanNode(True),
    ),
    (
        "boolean_in_or_operator",
        OperatorNode(
            operator="or",
            _left=ExpressionNode("python_implementation", "==", "CPython"),
            _right=ExpressionNode("python_version", ">=", "3.7"),
        ),
        {
            "python_implementation": [False],
            "python_version": [Version("3.6")],
        },
        BooleanNode(False),
    ),
]


@pytest.mark.parametrize(
    "name,expr,env,expected",
    boolean_literal_testdata,
    ids=[x[0] for x in boolean_literal_testdata],
)
def test_boolean_literal_evaluate(name: str, expr: Node, env: Environment, expected: Node):
    """Test evaluation of boolean literals in various contexts."""
    result = expr.evaluate(env)
    assert result == expected


operator_testdata = [
    # AND operations with partial evaluation
    (
        "and_right_true_left_unknown",
        OperatorNode(
            operator="and",
            _left=ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
            _right=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
        ),
        {"os_name": ["posix"]},  # right evaluates to True
        ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),  # Returns left expression
    ),
    (
        "and_left_true_right_unknown",
        OperatorNode(
            operator="and",
            _left=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
            _right=ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
        ),
        {"os_name": ["posix"]},  # left evaluates to True
        ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),  # Returns right expression
    ),
    (
        "and_left_false_shortcircuit",
        OperatorNode(
            operator="and",
            _left=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
            _right=ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
        ),
        {"os_name": ["nt"]},  # left evaluates to False
        BooleanNode(False),  # Short circuits to False
    ),
    # OR operations with partial evaluation
    (
        "or_right_false_left_unknown",
        OperatorNode(
            operator="or",
            _left=ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
            _right=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
        ),
        {"os_name": ["nt"]},  # right evaluates to False
        ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),  # Returns left expression
    ),
    (
        "or_left_false_right_unknown",
        OperatorNode(
            operator="or",
            _left=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
            _right=ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
        ),
        {"os_name": ["nt"]},  # left evaluates to False
        ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),  # Returns right expression
    ),
    (
        "or_left_true_shortcircuit",
        OperatorNode(
            operator="or",
            _left=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
            _right=ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
        ),
        {"os_name": ["posix"]},  # left evaluates to True
        BooleanNode(True),  # Short circuits to True
    ),
    # No evaluation possible
    (
        "both_operands_unknown",
        OperatorNode(
            operator="and",
            _left=ExpressionNode(lhs="key1", comparator="==", rhs="value1"),
            _right=ExpressionNode(lhs="key2", comparator="==", rhs="value2"),
        ),
        {},  # nothing can be evaluated
        OperatorNode(  # Returns unchanged node
            operator="and",
            _left=ExpressionNode(lhs="key1", comparator="==", rhs="value1"),
            _right=ExpressionNode(lhs="key2", comparator="==", rhs="value2"),
        ),
    ),
]


@pytest.mark.parametrize(
    "name,expr,env,expected",
    operator_testdata,
    ids=[x[0] for x in operator_testdata],
)
def test_operator_evaluate(name: str, expr: OperatorNode, env: Environment, expected: Node):
    result = expr.evaluate(env)
    assert result == expected


def test_complex_partial_evaluation():
    """Test a complex tree where only part of it can be evaluated."""
    # "(python_version >= '3.8' and os_name == 'posix') or (sys_platform == 'linux' and implementation_name == 'cpython')"
    expr = parse(
        "(python_version >= '3.8' and os_name == 'posix') or "
        "(sys_platform == 'linux' and implementation_name == 'cpython')"
    )

    # Environment that:
    # - Doesn't have python_version or os_name (left tree can't evaluate)
    # - Has sys_platform as linux (first part of right tree evaluates to True)
    # - Has implementation_name as cpython (second part evaluates to True)
    env: Environment = {
        "sys_platform": ["linux"],
        "implementation_name": ["cpython"],
    }

    # Expected:
    # - Left side stays as is because environment is missing
    # - Right side evaluates to True because both parts are True
    # - Overall result is True because one side of OR is True
    expected = BooleanNode(True)

    result = expr.evaluate(env)
    assert result == expected


# OR short-circuit tests
or_shortcircuit_testdata = [
    (
        "or_left_true_shortcircuit",
        OperatorNode(
            operator="or",
            _left=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
            _right=ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
        ),
        {"os_name": ["posix"]},  # right side can't evaluate but not needed
        BooleanNode(True),
    ),
    (
        "or_right_true_shortcircuit",
        OperatorNode(
            operator="or",
            _left=ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
            _right=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
        ),
        {"os_name": ["posix"]},  # left side can't evaluate but not needed
        BooleanNode(True),
    ),
]


@pytest.mark.parametrize(
    "name,expr,env,expected",
    or_shortcircuit_testdata,
    ids=[x[0] for x in or_shortcircuit_testdata],
)
def test_or_shortcircuit_evaluate(name: str, expr: OperatorNode, env: Environment, expected: Node):
    result = expr.evaluate(env)
    assert result == expected


partial_eval_testdata = [
    (
        "or_left_not_bool",
        OperatorNode(
            operator="or",
            _left=ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
            _right=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
        ),
        {"os_name": ["nt"]},  # right evaluates to False
        ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
    ),
    (
        "or_right_not_bool",
        OperatorNode(
            operator="or",
            _left=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
            _right=ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
        ),
        {"os_name": ["nt"]},  # left evaluates to False
        ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
    ),
    (
        "and_left_not_bool",
        OperatorNode(
            operator="and",
            _left=ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
            _right=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
        ),
        {"os_name": ["posix"]},  # right evaluates to True
        ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
    ),
    (
        "and_right_not_bool",
        OperatorNode(
            operator="and",
            _left=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
            _right=ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
        ),
        {"os_name": ["posix"]},  # left evaluates to True
        ExpressionNode(lhs="missing_key", comparator="==", rhs="value"),
    ),
    (
        "neither_side_bool",
        OperatorNode(
            operator="and",
            _left=ExpressionNode(lhs="key1", comparator="==", rhs="value1"),
            _right=ExpressionNode(lhs="key2", comparator="==", rhs="value2"),
        ),
        {},  # nothing evaluates
        OperatorNode(
            operator="and",
            _left=ExpressionNode(lhs="key1", comparator="==", rhs="value1"),
            _right=ExpressionNode(lhs="key2", comparator="==", rhs="value2"),
        ),
    ),
]


@pytest.mark.parametrize(
    "name,expr,env,expected",
    partial_eval_testdata,
    ids=[x[0] for x in partial_eval_testdata],
)
def test_partial_evaluation(name: str, expr: OperatorNode, env: Environment, expected: Node):
    result = expr.evaluate(env)
    assert result == expected


# Full evaluation tests
full_eval_testdata = [
    (
        "and_both_true",
        OperatorNode(
            operator="and",
            _left=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
            _right=ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
        ),
        {"os_name": ["posix"], "python_version": [Version("3.8")]},
        BooleanNode(True),
    ),
    (
        "and_both_false",
        OperatorNode(
            operator="and",
            _left=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
            _right=ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
        ),
        {"os_name": ["nt"], "python_version": [Version("3.7")]},
        BooleanNode(False),
    ),
    (
        "or_both_false",
        OperatorNode(
            operator="or",
            _left=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
            _right=ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
        ),
        {"os_name": ["nt"], "python_version": [Version("3.7")]},
        BooleanNode(False),
    ),
]


@pytest.mark.parametrize(
    "name,expr,env,expected",
    full_eval_testdata,
    ids=[x[0] for x in full_eval_testdata],
)
def test_full_evaluation(name: str, expr: OperatorNode, env: Environment, expected: Node):
    result = expr.evaluate(env)
    assert result == expected
