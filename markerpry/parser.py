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
        while len(marker) > 3 and 'and' in marker:
            operator_index = marker.index('and')
            before = marker[: operator_index - 1]
            term = marker[operator_index - 1 : operator_index + 2]
            after = marker[operator_index + 2 :]
            marker = list(before) + [term] + list(after)

        while len(marker) > 3 and 'or' in marker:
            operator_index = marker.index('or')
            before = marker[: operator_index - 1]
            term = marker[operator_index - 1 : operator_index + 2]
            after = marker[operator_index + 2 :]
            marker = list(before) + [term] + list(after)

        if len(marker) == 1:
            return _parse_marker(marker[0])
        if len(marker) == 3:
            lhs, comparator, rhs = marker
            if comparator in ('and', 'or'):
                return OperatorNode(
                    operator=marker[1],
                    _left=_parse_marker(lhs),
                    _right=_parse_marker(rhs),
                )
            if (
                isinstance(lhs, Variable)
                and isinstance(rhs, Value)
                and isinstance(comparator, Op)
                and (
                    comparator.value == "=="
                    or comparator.value == "==="
                    or comparator.value == "!="
                    or comparator.value == ">"
                    or comparator.value == "<"
                    or comparator.value == ">="
                    or comparator.value == "<="
                    or comparator.value == "in"
                    or comparator.value == "not in"
                    or comparator.value == "~="
                )
            ):
                return ExpressionNode(
                    lhs=lhs.value,
                    comparator=cast(Comparator, comparator.value),
                    rhs=rhs.value,
                )
            if (
                isinstance(lhs, Value)
                and isinstance(rhs, Variable)
                and isinstance(comparator, Op)
                and (comparator.value == "in" or comparator.value == "not in")
            ):
                return ExpressionNode(
                    lhs=lhs.value,
                    comparator=cast(Comparator, comparator.value),
                    rhs=rhs.value,
                )
    raise NotImplementedError(f"Unknown marker {type(marker)}: {marker}")
