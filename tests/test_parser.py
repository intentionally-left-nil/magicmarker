import pytest
from packaging.markers import Marker

from markerpry.node import BooleanNode, ExpressionNode, Node, OperatorNode
from markerpry.parser import parse

# Basic comparison tests
basic_markers = [
    ("os_name == 'nt'", ExpressionNode(lhs="os_name", comparator="==", rhs="nt")),
    (
        "sys_platform == 'win32'",
        ExpressionNode(lhs="sys_platform", comparator="==", rhs="win32"),
    ),
    (
        "platform_machine == 'x86_64'",
        ExpressionNode(lhs="platform_machine", comparator="==", rhs="x86_64"),
    ),
    (
        "platform_python_implementation == 'CPython'",
        ExpressionNode(lhs="platform_python_implementation", comparator="==", rhs="CPython"),
    ),
]


@pytest.mark.parametrize("marker_str,expected", basic_markers, ids=[x[0] for x in basic_markers])
def test_basic_markers(marker_str: str, expected):
    result = parse(marker_str)
    assert result == expected


# Version comparison tests
version_markers = [
    (
        "python_version >= '3.8'",
        ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
    ),
    (
        "python_full_version < '3.9.7'",
        ExpressionNode(lhs="python_full_version", comparator="<", rhs="3.9.7"),
    ),
    (
        "implementation_version == '3.8.10'",
        ExpressionNode(lhs="implementation_version", comparator="==", rhs="3.8.10"),
    ),
]


@pytest.mark.parametrize("marker_str,expected", version_markers, ids=[x[0] for x in version_markers])
def test_version_markers(marker_str: str, expected):
    result = parse(marker_str)
    assert result == expected


# Simple boolean operation tests
boolean_markers = [
    (
        "python_version >= '3.8' and os_name == 'posix'",
        OperatorNode(
            operator="and",
            _left=ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
            _right=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
        ),
    ),
    (
        "os_name == 'nt' or os_name == 'posix'",
        OperatorNode(
            operator="or",
            _left=ExpressionNode(lhs="os_name", comparator="==", rhs="nt"),
            _right=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
        ),
    ),
]


@pytest.mark.parametrize("marker_str,expected", boolean_markers, ids=[x[0] for x in boolean_markers])
def test_boolean_markers(marker_str: str, expected):
    result = parse(marker_str)
    assert result == expected


# Nested AND operation tests
nested_and_markers = [
    (
        "python_version >= '3.8' and (os_name == 'posix' and platform_machine == 'x86_64')",
        OperatorNode(
            operator="and",
            _left=ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
            _right=OperatorNode(
                operator="and",
                _left=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
                _right=ExpressionNode(lhs="platform_machine", comparator="==", rhs="x86_64"),
            ),
        ),
    ),
    (
        "(python_version >= '3.8' and os_name == 'posix') and platform_machine == 'x86_64'",
        OperatorNode(
            operator="and",
            _left=OperatorNode(
                operator="and",
                _left=ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
                _right=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
            ),
            _right=ExpressionNode(lhs="platform_machine", comparator="==", rhs="x86_64"),
        ),
    ),
]


@pytest.mark.parametrize("marker_str,expected", nested_and_markers, ids=[x[0] for x in nested_and_markers])
def test_nested_and_markers(marker_str: str, expected):
    result = parse(marker_str)
    assert result == expected


# Complex nested AND operation tests
complex_and_markers = [
    (
        "python_version >= '3.8' and (os_name == 'posix' and platform_machine == 'x86_64') and python_version < '4.0'",
        OperatorNode(
            operator="and",
            _left=ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
            _right=OperatorNode(
                operator="and",
                _right=ExpressionNode(lhs="python_version", comparator="<", rhs="4.0"),
                _left=OperatorNode(
                    operator="and",
                    _left=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
                    _right=ExpressionNode(lhs="platform_machine", comparator="==", rhs="x86_64"),
                ),
            ),
        ),
    ),
    (
        "(python_version >= '3.8' and os_name == 'posix') and (platform_machine == 'x86_64' and python_version < '4.0')",
        OperatorNode(
            operator="and",
            _left=OperatorNode(
                operator="and",
                _left=ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
                _right=ExpressionNode(lhs="os_name", comparator="==", rhs="posix"),
            ),
            _right=OperatorNode(
                operator="and",
                _left=ExpressionNode(lhs="platform_machine", comparator="==", rhs="x86_64"),
                _right=ExpressionNode(lhs="python_version", comparator="<", rhs="4.0"),
            ),
        ),
    ),
]


@pytest.mark.parametrize("marker_str,expected", complex_and_markers, ids=[x[0] for x in complex_and_markers])
def test_complex_and_markers(marker_str: str, expected):
    result = parse(marker_str)
    assert result == expected


# Invalid marker tests
invalid_markers = [
    "python_version",  # Missing operator and value
    "python_version ==",  # Missing value
    "== '3.8'",  # Missing variable
    "python_version = '3.8'",  # Invalid operator (single =)
    'python_version == "3.8',  # Unclosed quote
    "python_version == '3.8",  # Unclosed quote
    "python_version == 3.8",  # Missing quotes
    "invalid_var == '3.8'",  # Unknown environment marker
    "PYTHON_VERSION == '3.8'",  # Case sensitive
    # Invalid boolean logic
    "python_version >= '3.8' and",  # Incomplete AND
    "and os_name == 'posix'",  # AND with missing left side
    "python_version >= '3.8' or",  # Incomplete OR
    "or os_name == 'posix'",  # OR with missing left side
    "python_version >= '3.8' and and os_name == 'posix'",  # Double AND
    "python_version >= '3.8' or or os_name == 'posix'",  # Double OR
]


@pytest.mark.parametrize("marker_str", invalid_markers, ids=invalid_markers)
def test_invalid_markers(marker_str: str):
    with pytest.raises((ValueError, SyntaxError)):
        parse(marker_str)


# Mixed AND/OR operation tests
mixed_op_markers = [
    (
        "os_name == 'nt' or python_version >= '3.8' and platform_machine == 'x86_64'",
        OperatorNode(
            operator="or",
            _left=ExpressionNode(lhs="os_name", comparator="==", rhs="nt"),
            _right=OperatorNode(
                operator="and",
                _left=ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
                _right=ExpressionNode(lhs="platform_machine", comparator="==", rhs="x86_64"),
            ),
        ),
    ),
    (
        "(os_name == 'nt' or python_version >= '3.8') and platform_machine == 'x86_64'",
        OperatorNode(
            operator="and",
            _left=OperatorNode(
                operator="or",
                _left=ExpressionNode(lhs="os_name", comparator="==", rhs="nt"),
                _right=ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
            ),
            _right=ExpressionNode(lhs="platform_machine", comparator="==", rhs="x86_64"),
        ),
    ),
    (
        "os_name == 'nt' and python_version >= '3.8' or platform_machine == 'x86_64'",
        OperatorNode(
            operator="and",
            _left=ExpressionNode(lhs="os_name", comparator="==", rhs="nt"),
            _right=OperatorNode(
                operator="or",
                _left=ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
                _right=ExpressionNode(lhs="platform_machine", comparator="==", rhs="x86_64"),
            ),
        ),
    ),
    (
        "os_name == 'nt' or python_version >= '3.8' or platform_machine == 'x86_64'",
        OperatorNode(
            operator="or",
            _left=ExpressionNode(lhs="os_name", comparator="==", rhs="nt"),
            _right=OperatorNode(
                operator="or",
                _left=ExpressionNode(lhs="python_version", comparator=">=", rhs="3.8"),
                _right=ExpressionNode(lhs="platform_machine", comparator="==", rhs="x86_64"),
            ),
        ),
    ),
]


@pytest.mark.parametrize("marker_str,expected", mixed_op_markers, ids=[x[0] for x in mixed_op_markers])
def test_mixed_op_markers(marker_str: str, expected):
    result = parse(marker_str)
    assert result == expected
