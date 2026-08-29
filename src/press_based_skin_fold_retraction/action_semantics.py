"""Reference semantics for the phase-aware 7D task action.

The first six components retain delta-pose semantics. The seventh component is
a normal-force increment used only during hybrid contact control. This module
contains no robot I/O; it makes the phase projection explicit and testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Iterable


ACTION_DIMENSION = 7
ACTION_LABELS = (
    "delta_x",
    "delta_y",
    "delta_z",
    "delta_rotation_x",
    "delta_rotation_y",
    "delta_rotation_z",
    "delta_normal_force",
)


class ControlPhase(str, Enum):
    """Contact-aware execution phases."""

    FREE_SPACE = "FREE_SPACE"
    PRECONTACT_Z_ONLY = "PRECONTACT_Z_ONLY"
    CONTACT_HYBRID = "CONTACT_HYBRID"


_ACTIVE_INDICES = {
    ControlPhase.FREE_SPACE: (0, 1, 2, 3, 4, 5),
    ControlPhase.PRECONTACT_Z_ONLY: (2,),
    ControlPhase.CONTACT_HYBRID: (0, 1, 6),
}


@dataclass(frozen=True)
class PhaseCommand:
    """A decoded command after phase projection and physical scaling."""

    phase: ControlPhase
    position_delta: tuple[float, float, float]
    rotation_delta: tuple[float, float, float]
    normal_force_delta: float
    active_dimensions: tuple[str, ...]


def _coerce_phase(phase: ControlPhase | str) -> ControlPhase:
    if isinstance(phase, ControlPhase):
        return phase
    try:
        return ControlPhase(str(phase).upper())
    except ValueError as exc:
        valid = ", ".join(item.value for item in ControlPhase)
        raise ValueError(f"Unknown control phase {phase!r}; expected one of: {valid}") from exc


def _coerce_action(action: Iterable[float]) -> tuple[float, ...]:
    values = tuple(float(value) for value in action)
    if len(values) != ACTION_DIMENSION:
        raise ValueError(
            f"Expected {ACTION_DIMENSION} action values, received {len(values)}"
        )
    if not all(isfinite(value) for value in values):
        raise ValueError("Action values must be finite")
    return values


def project_action(
    action: Iterable[float],
    phase: ControlPhase | str,
    *,
    clip: bool = True,
) -> tuple[float, ...]:
    """Project a normalized action onto the dimensions active in ``phase``.

    Args:
        action: Seven values ordered according to :data:`ACTION_LABELS`.
        phase: A :class:`ControlPhase` value or its case-insensitive name.
        clip: Clip active normalized values to ``[-1, 1]`` when true.

    Returns:
        A seven-element tuple with inactive dimensions set to zero.
    """

    values = _coerce_action(action)
    resolved_phase = _coerce_phase(phase)
    projected = [0.0] * ACTION_DIMENSION

    for index in _ACTIVE_INDICES[resolved_phase]:
        value = values[index]
        projected[index] = max(-1.0, min(1.0, value)) if clip else value

    return tuple(projected)


def decode_action(
    action: Iterable[float],
    phase: ControlPhase | str,
    *,
    position_scale: float,
    rotation_scale: float,
    normal_force_scale: float,
    clip: bool = True,
) -> PhaseCommand:
    """Project and scale a normalized task action into a structured command.

    Scales are expressed per control step: meters for ``position_scale``,
    radians for ``rotation_scale``, and newtons for ``normal_force_scale``.
    """

    scales = (position_scale, rotation_scale, normal_force_scale)
    if not all(isfinite(float(value)) and float(value) >= 0.0 for value in scales):
        raise ValueError("Action scales must be finite and non-negative")

    resolved_phase = _coerce_phase(phase)
    projected = project_action(action, resolved_phase, clip=clip)
    active_indices = _ACTIVE_INDICES[resolved_phase]

    return PhaseCommand(
        phase=resolved_phase,
        position_delta=tuple(
            projected[index] * float(position_scale) for index in range(3)
        ),
        rotation_delta=tuple(
            projected[index] * float(rotation_scale) for index in range(3, 6)
        ),
        normal_force_delta=projected[6] * float(normal_force_scale),
        active_dimensions=tuple(ACTION_LABELS[index] for index in active_indices),
    )
