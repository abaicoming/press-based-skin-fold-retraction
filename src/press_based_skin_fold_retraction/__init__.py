"""Task-level interfaces for press-based robotic skin-fold retraction."""

from .action_semantics import (
    ACTION_DIMENSION,
    ACTION_LABELS,
    ContactState,
    InterpretedAction,
    interpret_action,
)

__all__ = [
    "ACTION_DIMENSION",
    "ACTION_LABELS",
    "ContactState",
    "InterpretedAction",
    "interpret_action",
]
