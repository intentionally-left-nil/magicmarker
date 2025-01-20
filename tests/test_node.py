from markerpry.node import FALSE, TRUE, BooleanNode, ExpressionNode, OperatorNode


def test_boolean_node_contains():
    """Test that BooleanNode never contains any keys."""
    node = BooleanNode(True)
    assert not node.contains("python_version")
    assert not node.contains("os_name")
    assert not node.contains("")


def test_expression_node_contains():
    """Test that ExpressionNode contains only its lhs key."""
    expr = ExpressionNode("python_version", ">=", "3.7")

    assert expr.contains("python_version")
    assert not expr.contains("os_name")
    assert not expr.contains("python_implementation")
    assert not expr.contains("")


def test_operator_node_contains():
    """Test that OperatorNode contains keys from both its children."""
    expr1 = ExpressionNode("python_version", ">=", "3.7")
    expr2 = ExpressionNode("os_name", "==", "posix")
    and_node = OperatorNode("and", expr1, expr2)

    assert and_node.contains("python_version")
    assert and_node.contains("os_name")
    assert not and_node.contains("python_implementation")
    assert not and_node.contains("")


def test_operator_node_nested_contains():
    """Test that OperatorNode correctly checks deeply nested expressions."""
    expr1 = ExpressionNode("python_version", ">=", "3.7")
    expr2 = ExpressionNode("os_name", "==", "posix")
    and_node = OperatorNode("and", expr1, expr2)
    expr3 = ExpressionNode("implementation_name", "==", "cpython")
    or_node = OperatorNode("or", and_node, expr3)

    assert or_node.contains("python_version")
    assert or_node.contains("os_name")
    assert or_node.contains("implementation_name")
    assert not or_node.contains("platform_machine")
    assert not or_node.contains("")


def test_operator_node_with_boolean_contains():
    """Test that OperatorNode with boolean children still checks remaining expressions."""
    expr = ExpressionNode("python_version", ">=", "3.7")
    true_node = BooleanNode(True)
    and_node = OperatorNode("and", true_node, expr)

    assert and_node.contains("python_version")
    assert not and_node.contains("os_name")
    assert not and_node.contains("")


def test_boolean_equality():
    assert BooleanNode(True) == BooleanNode(True)
    assert BooleanNode(True) != BooleanNode(False)
    assert TRUE == TRUE
    assert BooleanNode(True) == TRUE
