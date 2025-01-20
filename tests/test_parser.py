import pytest
from magic_marker.parser import parse
from magic_marker.node import Node, ExpressionNode, OperatorNode, BooleanNode


def assert_nodes_equal(left: Node, right: Node) -> None:
    """Assert that two marker nodes are structurally equivalent."""
    assert type(left) == type(
        right
    ), f"Node types differ: {type(left)} != {type(right)}"

    if isinstance(left, BooleanNode) and isinstance(right, BooleanNode):
        assert left.state == right.state

    elif isinstance(left, ExpressionNode) and isinstance(right, ExpressionNode):
        assert left.lhs == right.lhs, "LHS differs"
        assert left.comparator == right.comparator, "Comparator differs"
        assert left.rhs == right.rhs, "RHS differs"

    elif isinstance(left, OperatorNode) and isinstance(right, OperatorNode):
        assert left.operator == right.operator, "Operator differs"
        assert_nodes_equal(left._left, right._left)
        assert_nodes_equal(left._right, right._right)

    else:
        pytest.fail(f"Unknown node type comparison: {type(left)} vs {type(right)}")


testdata = [
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
        ExpressionNode(
            lhs="platform_python_implementation", comparator="==", rhs="CPython"
        ),
    ),
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
    (
        "python_version > '3.7'",
        ExpressionNode(lhs="python_version", comparator=">", rhs="3.7"),
    ),
    (
        "python_version < '4.0'",
        ExpressionNode(lhs="python_version", comparator="<", rhs="4.0"),
    ),
    (
        "python_version >= '3.6'",
        ExpressionNode(lhs="python_version", comparator=">=", rhs="3.6"),
    ),
    (
        "python_version <= '4.0'",
        ExpressionNode(lhs="python_version", comparator="<=", rhs="4.0"),
    ),
    (
        "python_version != '3.7'",
        ExpressionNode(lhs="python_version", comparator="!=", rhs="3.7"),
    ),
    ('extra == "test"', ExpressionNode(lhs="extra", comparator="==", rhs="test")),
    (
        'python_version == "3.8"',
        ExpressionNode(lhs="python_version", comparator="==", rhs="3.8"),
    ),
    (
        "python_version == '3.8'",
        ExpressionNode(lhs="python_version", comparator="==", rhs="3.8"),
    ),
]


@pytest.mark.parametrize(
    "marker_str,expected",
    testdata,
    ids=[x[0] for x in testdata],
)
def test_parse_markers(marker_str: str, expected):
    result = parse(marker_str)
    assert_nodes_equal(result, expected)


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
]


@pytest.mark.parametrize("marker_str", invalid_markers, ids=invalid_markers)
def test_invalid_markers(marker_str: str):
    with pytest.raises((ValueError, SyntaxError)):
        parse(marker_str)
