from typing import Any
from packaging.markers import Marker
from packaging._parser import Op, Variable, Value

from .node import Node, ExpressionNode


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
    if isinstance(marker, tuple) or isinstance(marker, list) and len(marker) == 1:
        return _parse_item(marker)
    raise NotImplementedError(f"Unknown marker type: {type(marker)}")


def _parse_item(marker: list[Any] | tuple[Any, ...]) -> Node:
    if isinstance(marker, tuple) or isinstance(marker, list):
        if len(marker) == 1:
            return _parse_item(marker[0])
        if len(marker) == 3:
            lhs, comparator, rhs = marker
            if isinstance(lhs, Variable) and isinstance(rhs, Value):
                return ExpressionNode(
                    lhs=lhs.value, comparator=comparator.value, rhs=rhs.value
                )
    raise NotImplementedError(f"Unknown marker type: {type(marker)}")
