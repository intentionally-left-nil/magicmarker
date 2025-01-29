from markerpry.node import FALSE, TRUE, BooleanNode, ExpressionNode, OperatorNode
import pytest


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
    """Test boolean node equality with both BooleanNodes and Python bools."""
    assert BooleanNode(True) == BooleanNode(True)
    assert BooleanNode(True) != BooleanNode(False)
    assert TRUE == TRUE
    assert BooleanNode(True) == TRUE
    # New tests for bool comparison
    assert TRUE == True  # type: ignore
    assert FALSE == False  # type: ignore
    assert TRUE != False  # type: ignore
    assert FALSE != True  # type: ignore


def test_boolean_coercion():
    """Test that BooleanNode can be used in boolean contexts."""
    assert bool(TRUE) is True
    assert bool(FALSE) is False
    # Test in if statement
    if TRUE:
        assert True
    else:
        assert False
    if FALSE:
        assert False
    else:
        assert True
    # Test with and/or
    assert TRUE and True
    assert not (FALSE and True)
    assert TRUE or False
    assert not (FALSE or False)


def test_non_boolean_node_coercion():
    """Test that non-boolean nodes cannot be coerced to bool."""
    expr = ExpressionNode("python_version", ">=", "3.7")
    op = OperatorNode(
        "and",
        ExpressionNode("os_name", "==", "posix"),
        ExpressionNode("python_version", ">=", "3.7"),
    )

    with pytest.raises(TypeError, match="Cannot convert ExpressionNode to bool"):
        bool(expr)
    
    with pytest.raises(TypeError, match="Cannot convert OperatorNode to bool"):
        bool(op)
    
    # Test in if statement
    with pytest.raises(TypeError, match="Cannot convert ExpressionNode to bool"):
        if expr:
            pass
    
    with pytest.raises(TypeError, match="Cannot convert OperatorNode to bool"):
        if op:
            pass
