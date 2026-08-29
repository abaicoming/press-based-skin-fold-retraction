#!/usr/bin/env python3
"""Show how one task action is interpreted before and during contact."""

from dataclasses import asdict
import json

from press_based_skin_fold_retraction import ContactState, interpret_action


def print_action(action, state, **kwargs) -> None:
    interpreted = interpret_action(action, state, **kwargs)
    payload = asdict(interpreted)
    payload["contact_state"] = interpreted.contact_state.name
    print(json.dumps(payload, indent=2))


def main() -> None:
    action = (0.01, -0.005, -0.01, 0.02, 0.0, -0.01, 12.0)
    print_action(action, ContactState.NON_CONTACT)
    print_action(action, ContactState.CONTACT, tool_normal=(0.0, 0.0, 1.0))


if __name__ == "__main__":
    main()
