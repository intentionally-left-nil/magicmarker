from typing import Any, Literal
from packaging.markers import Marker
from packaging._parser import Op, Variable, Value

from .node import Node, OperatorNode, ExpressionNode


def parse(marker_str: str) -> Node:
    """
    Parse a PEP 508 marker string into a Node tree.

    Args:
        marker_str: A string containing a PEP 508 marker expression

    Returns:
        A Node representing the parsed marker expression

    Raises:
        packaging.markers.InvalidMarker: If the marker string is invalid
    """
    marker = Marker(marker_str)
    return _parse_marker(marker._markers)


def _parse_marker(marker: Any) -> Node:
    print(marker)
    if isinstance(marker, tuple) or isinstance(marker, list):
        if len(marker) == 1:
            return _parse_marker(marker[0])
        if len(marker) == 3:
            lhs, comparator, rhs = marker
            if comparator == "and" or comparator == "or":
                return OperatorNode(
                    operator=comparator,
                    _left=_parse_marker(lhs),
                    _right=_parse_marker(rhs),
                )
            if (
                isinstance(lhs, Variable)
                and isinstance(rhs, Value)
                and isinstance(comparator, Op)
                and (
                    comparator.value == "=="
                    or comparator.value == "!="
                    or comparator.value == ">"
                    or comparator.value == "<"
                    or comparator.value == ">="
                    or comparator.value == "<="
                )
            ):
                return ExpressionNode(
                    lhs=lhs.value,
                    comparator=comparator.value,
                    rhs=rhs.value,
                )

    raise NotImplementedError(f"Unknown marker {type(marker)}: {marker}")

    raise NotImplementedError(f"Unknown marker {type(marker)}: {marker}")
