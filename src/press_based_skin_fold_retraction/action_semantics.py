"""Minimal reference for the paper's contact-aware action semantics.

The unified action is ``[delta_position, delta_orientation,
desired_normal_force]``. Autonomous execution has two contact states:

* non-contact: execute position and orientation increments;
* contact: execute only the tangential position increment and desired normal
  force while discarding normal position and orientation increments.

This module contains no robot I/O or low-level safety controller.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from math import isfinite, sqrt
from typing import Iterable


ACTION_DIMENSION = 7
ACTION_LABELS = (
    "delta_position_x",
    "delta_position_y",
    "delta_position_z",
    "delta_orientation_x",
    "delta_orientation_y",
    "delta_orientation_z",
    "desired_normal_force",
)


class ContactState(IntEnum):
    """Force-estimated autonomous contact state."""

    NON_CONTACT = 0
    CONTACT = 1


@dataclass(frozen=True)
class InterpretedAction:
    """Task action after contact-aware semantic interpretation."""

    contact_state: ContactState
    position_increment: tuple[float, float, float]
    orientation_increment: tuple[float, float, float]
    desired_normal_force: float | None


def _coerce_action(action: Iterable[float]) -> tuple[float, ...]:
    values = tuple(float(value) for value in action)
    if len(values) != ACTION_DIMENSION:
        raise ValueError(
            f"Expected {ACTION_DIMENSION} action values, received {len(values)}"
        )
    if not all(isfinite(value) for value in values):
        raise ValueError("Action values must be finite")
    return values


def _coerce_contact_state(state: ContactState | int | bool) -> ContactState:
    if isinstance(state, ContactState):
        return state
    try:
        return ContactState(int(state))
    except (TypeError, ValueError) as exc:
        raise ValueError("Contact state must be 0 (non-contact) or 1 (contact)") from exc


def _unit_vector(vector: Iterable[float]) -> tuple[float, float, float]:
    values = tuple(float(value) for value in vector)
    if len(values) != 3:
        raise ValueError(f"Expected a 3D tool normal, received {len(values)} values")
    if not all(isfinite(value) for value in values):
        raise ValueError("Tool-normal values must be finite")

    norm = sqrt(sum(value * value for value in values))
    if norm <= 1e-12:
        raise ValueError("Tool normal must have non-zero magnitude")
    return tuple(value / norm for value in values)


def interpret_action(
    action: Iterable[float],
    contact_state: ContactState | int | bool,
    *,
    tool_normal: Iterable[float] | None = None,
) -> InterpretedAction:
    """Interpret the unified action according to the force-estimated state.

    ``tool_normal`` is required in contact and is expressed in the same frame
    as the position increment. The returned contact position increment is the
    tangential projection ``(I - n n^T) delta_position``.
    """

    values = _coerce_action(action)
    state = _coerce_contact_state(contact_state)
    position = values[:3]
    orientation = values[3:6]

    if state is ContactState.NON_CONTACT:
        return InterpretedAction(
            contact_state=state,
            position_increment=position,
            orientation_increment=orientation,
            desired_normal_force=None,
        )

    if tool_normal is None:
        raise ValueError("tool_normal is required in contact")
    normal = _unit_vector(tool_normal)
    normal_component = sum(normal[index] * position[index] for index in range(3))
    tangential_position = tuple(
        position[index] - normal[index] * normal_component for index in range(3)
    )

    return InterpretedAction(
        contact_state=state,
        position_increment=tangential_position,
        orientation_increment=(0.0, 0.0, 0.0),
        desired_normal_force=values[6],
    )
