from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal
from typing_extensions import override


class Node(ABC):
    """Base class for all nodes in the marker expression tree."""

    left: "Node | None" = None
    right: "Node | None" = None

    @abstractmethod
    def value(self) -> str:
        """Return a string representation of this node's value."""
        pass


@dataclass
class BooleanNode(Node):
    """A node representing a boolean literal value."""

    state: bool

    @override
    def value(self) -> str:
        return str(self.state)

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BooleanNode):
            return NotImplemented
        return self.state == other.state


@dataclass
class ExpressionNode(Node):
    """A node representing a comparison expression (e.g., python_version > '3.7')."""

    lhs: str
    comparator: Literal["==", "!=", ">", "<", ">=", "<="]
    rhs: str

    @override
    def value(self) -> str:
        return f"{self.lhs} {self.comparator} {self.rhs}"

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExpressionNode):
            return NotImplemented
        return (
            self.lhs == other.lhs
            and self.comparator == other.comparator
            and self.rhs == other.rhs
        )


@dataclass
class OperatorNode(Node):
    """A node representing a boolean operation (and/or) between two child nodes."""

    operator: Literal["and", "or"]
    _left: Node
    _right: Node
    left: "Node | None" = None
    right: "Node | None" = None

    def __post_init__(self):
        self.left = self._left
        self.right = self._right

    @override
    def value(self) -> str:
        return f"{self._left.value()} {self.operator} {self._right.value()}"

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OperatorNode):
            return NotImplemented
        return (
            self.operator == other.operator
            and self._left == other._left
            and self._right == other._right
        )
