#!/usr/bin/env python3
"""Print how one normalized action is interpreted in each control phase."""

from dataclasses import asdict
import json

from press_based_skin_fold_retraction import ControlPhase, decode_action


def main() -> None:
    action = (0.25, -0.20, -0.10, 0.05, 0.00, -0.05, 0.30)

    for phase in ControlPhase:
        command = decode_action(
            action,
            phase,
            position_scale=0.01,
            rotation_scale=0.02,
            normal_force_scale=2.0,
        )
        payload = asdict(command)
        payload["phase"] = command.phase.value
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
