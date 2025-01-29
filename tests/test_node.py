from markerpry.node import FALSE, TRUE, BooleanNode, ExpressionNode, OperatorNode


def test_boolean_node_contains():
    """Test that BooleanNode never contains any keys."""
    node = BooleanNode(True)
    assert "python_version" not in node
    assert "os_name" not in node
    assert "" not in node


def test_expression_node_contains():
    """Test that ExpressionNode contains only its lhs key."""
    expr = ExpressionNode("python_version", ">=", "3.7")
    
    assert "python_version" in expr
    assert "os_name" not in expr
    assert "python_implementation" not in expr
    assert "" not in expr


def test_operator_node_contains():
    """Test that OperatorNode contains keys from both its children."""
    expr1 = ExpressionNode("python_version", ">=", "3.7")
    expr2 = ExpressionNode("os_name", "==", "posix")
    and_node = OperatorNode("and", expr1, expr2)
    
    assert "python_version" in and_node
    assert "os_name" in and_node
    assert "python_implementation" not in and_node
    assert "" not in and_node


def test_operator_node_nested_contains():
    """Test that OperatorNode correctly checks deeply nested expressions."""
    expr1 = ExpressionNode("python_version", ">=", "3.7")
    expr2 = ExpressionNode("os_name", "==", "posix")
    and_node = OperatorNode("and", expr1, expr2)
    expr3 = ExpressionNode("implementation_name", "==", "cpython")
    or_node = OperatorNode("or", and_node, expr3)
    
    assert "python_version" in or_node
    assert "os_name" in or_node
    assert "implementation_name" in or_node
    assert "platform_machine" not in or_node
    assert "" not in or_node


def test_operator_node_with_boolean_contains():
    """Test that OperatorNode with boolean children still checks remaining expressions."""
    expr = ExpressionNode("python_version", ">=", "3.7")
    true_node = BooleanNode(True)
    and_node = OperatorNode("and", true_node, expr)
    
    assert "python_version" in and_node
    assert "os_name" not in and_node
    assert "" not in and_node


def test_boolean_equality():
    assert BooleanNode(True) == BooleanNode(True)
    assert BooleanNode(True) != BooleanNode(False)
    assert TRUE == TRUE
    assert BooleanNode(True) == TRUE
