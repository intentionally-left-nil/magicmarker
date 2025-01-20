from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal
from typing_extensions import override, assert_never
from packaging.version import Version
from packaging.specifiers import SpecifierSet, InvalidSpecifier
import re


Environment = dict[str, list[str | Version | re.Pattern[str]]]


class Node(ABC):
    """Base class for all nodes in the marker expression tree."""

    left: "Node | None" = None
    right: "Node | None" = None

    @abstractmethod
    def value(self) -> str:
        """Return a string representation of this node's value."""
        pass

    @abstractmethod
    def evaluate(self, environment: Environment) -> "Node":
        """Partially or fully evaluates the node based on the environment"""
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

    @override
    def evaluate(self, environment: Environment) -> "Node":
        return BooleanNode(self.state)


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

    @override
    def evaluate(self, environment: Environment) -> "Node":
        if not self.lhs in environment:
            return self.copy()
        values = environment[self.lhs]
        result: bool | None = None
        for value in values:
            if isinstance(value, str):
                eval = self._evaluate_string(value)
                result = result if eval is None else result or eval
            elif isinstance(value, re.Pattern):
                eval = self._evaluate_pattern(value)
                result = result if eval is None else result or eval
            elif isinstance(value, Version):
                eval = self._evaluate_version(value)
                result = result if eval is None else result or eval
            else:
                assert_never(value)
        return self.copy() if result is None else BooleanNode(result)

    def _evaluate_string(self, value: str) -> "bool | None":
        if self.comparator == "==":
            return value == self.rhs
        elif self.comparator == "!=":
            return value != self.rhs
        else:
            return None

    def _evaluate_pattern(self, value: re.Pattern[str]) -> "bool | None":
        if self.comparator == "==":
            return value.match(self.rhs) is not None
        elif self.comparator == "!=":
            return not value.match(self.rhs)
        else:
            return None

    def _evaluate_version(self, value: Version) -> "bool | None":
        try:
            specifier = SpecifierSet(f"{self.comparator} {self.rhs}")
        except InvalidSpecifier:
            return None
        return specifier.contains(value)

    def copy(self) -> "ExpressionNode":
        return ExpressionNode(self.lhs, self.comparator, self.rhs)


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

    @override
    def evaluate(self, environment: Environment) -> "Node":
        left = self._left.evaluate(environment)
        right = self._right.evaluate(environment)

        if self.operator == "or":
            if isinstance(left, BooleanNode):
                return BooleanNode(True) if left.state else right
            if isinstance(right, BooleanNode):
                return BooleanNode(True) if right.state else left
            return OperatorNode(self.operator, left, right)
        elif self.operator == "and":
            if isinstance(left, BooleanNode):
                return right if left.state else BooleanNode(False)
            if isinstance(right, BooleanNode):
                return left if right.state else BooleanNode(False)
            return OperatorNode(self.operator, left, right)
        else:
            assert_never(self.operator)
