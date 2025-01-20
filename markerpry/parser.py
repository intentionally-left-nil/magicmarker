from typing import Any, cast

from packaging._parser import Op, Value, Variable
from packaging.markers import Marker

from markerpry.node import Comparator, ExpressionNode, Node, OperatorNode


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

    if isinstance(marker, tuple) or isinstance(marker, list):
        if len(marker) == 1:

            return _parse_marker(marker[0])
        if len(marker) == 3:
            # Leaf node base case
            lhs, comparator, rhs = marker
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
                    comparator=cast(Comparator, comparator.value),
                    rhs=rhs.value,
                )
        if len(marker) >= 3 and (marker[1] == "and" or marker[1] == "or"):
            rest = _parse_marker(marker[2:])
            return OperatorNode(
                operator=marker[1],
                _left=_parse_marker(marker[0]),
                _right=rest,
            )

    raise NotImplementedError(f"Unknown marker {type(marker)}: {marker}")
