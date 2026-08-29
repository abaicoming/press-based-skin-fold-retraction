# Robot-safety notes

This project involves real-time Cartesian motion and force control on a physical robot. Use it only in a controlled robotics workspace with trained operators and an independently accessible emergency stop. The software is a research artifact, not a safety-rated controller or medical device.

## Before hardware operation

- Validate all coordinate frames, quaternion conventions, wrench signs, and units in simulation or with the robot disabled.
- Confirm that the commanded normal-force direction points into the intended contact surface.
- Set conservative workspace, Cartesian-step, force, torque, velocity, and slew-rate limits in the lowest applicable control layer.
- Verify force/torque bias and noise with the tool unloaded before choosing contact hysteresis thresholds.
- Exercise each control phase at reduced speed, beginning with free-space motion and a compliant test surface.
- Keep the robot workspace clear of people and use a physical phantom or test fixture suitable for repeated contact.

## Runtime safeguards

The hardware deployment should enforce safeguards below the learned policy:

- Cartesian workspace clipping;
- per-step translation and rotation limits;
- normal and tangential force limits;
- wrench and setpoint slew-rate limits;
- command timeouts that return to a safe hold behavior;
- episode termination on safety violations;
- an emergency-stop path independent of the learning process.

Treat policy outputs and haptic commands as untrusted high-level requests. The low-level controller must remain responsible for phase constraints and actuator-safe commands.

## Data handling

Do not commit raw camera recordings, participant information, robot-network addresses, device serial numbers, demonstrations, checkpoints, or authentication material. The repository `.gitignore` excludes common experiment-artifact paths, but operators remain responsible for reviewing every staged file before pushing it.
