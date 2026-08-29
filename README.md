# Learning Press-Based Robotic Skin-Fold Retraction

[![CI](https://github.com/abaicoming/press-based-skin-fold-retraction/actions/workflows/ci.yml/badge.svg)](https://github.com/abaicoming/press-based-skin-fold-retraction/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

This repository accompanies **“Learning Press-Based Robotic Skin-Fold Retraction with Passive Compliance and Contact-Aware Action Semantics.”**

The project studies robotic retraction of skin-like deformable surfaces without relying on a pinch grasp. A passively compliant pressing tool, contact-aware hybrid position–force control, multimodal success estimation, and human-in-the-loop reinforcement learning are combined to create and maintain an exposed working region.

## Code release status

The manuscript is currently under review. This repository provides a **partial research release** containing the task-level interfaces and documentation needed to describe the contact-aware action design.

The current release includes:

- a self-contained implementation of the phase-aware 7D action semantics;
- a runnable action-decoding example and unit tests;
- a machine-readable task specification covering observations, actions, control phases, learning inputs, and evaluation metrics;
- method, system-architecture, and robot-safety documentation;
- continuous-integration checks for the released Python interface.

The full research code and experimental materials—including the KUKA/ROS 2 control stack, sigma.7 shared-control and haptic interface, complete HIL-SERL training pipeline, multimodal reward-classifier training code, robot experiment scripts, and release-ready configurations—will be made available after publication of the paper.

## Method at a glance

| Component | Role |
| --- | --- |
| Passive-compliance end effector | Conforms to the local surface while distributing contact during pressing and retraction. |
| Contact-aware action semantics | Interprets the same 7D policy action according to free-space, pre-contact, and contact phases. |
| Shared-control teleoperation | Uses a haptic master interface for demonstrations and online human intervention. |
| Multimodal reward estimation | Combines multi-view RGB observations with wrist force/torque history for success recognition. |
| Human-in-the-loop RL | Mixes demonstrations, online experience, and intervention transitions in an actor–learner workflow. |

## Contact-aware action interface

The normalized action is

```text
[dx, dy, dz, dRx, dRy, dRz, dF_normal]
```

Its active dimensions depend on the control phase:

| Control phase | Active action dimensions | Execution semantics |
| --- | --- | --- |
| `FREE_SPACE` | `dx, dy, dz, dRx, dRy, dRz` | 6D Cartesian pose motion |
| `PRECONTACT_Z_ONLY` | `dz` | Constrained approach with lateral position and orientation locked |
| `CONTACT_HYBRID` | `dx, dy, dF_normal` | Tangential position adjustment with normal-force control |

The self-contained reference implementation is in [`action_semantics.py`](src/press_based_skin_fold_retraction/action_semantics.py).

## Quick start

The reference action interface has no runtime dependencies beyond Python 3.10+.

```bash
python -m pip install -e .
python examples/inspect_action_semantics.py
python -m unittest discover -s tests -v
```

## Repository structure

```text
.
├── configs/        # Machine-readable task specification
├── docs/           # Method, architecture, and robot-safety notes
├── examples/       # Small runnable examples
├── src/            # Reusable task-level interfaces
└── tests/          # Unit tests for the reference interfaces
```

## Documentation

- [Method overview](docs/method.md)
- [System architecture](docs/system_architecture.md)
- [Robot safety](docs/safety.md)
- [Reference task specification](configs/task_spec.yaml)

## Research foundation

The learning workflow builds on [HIL-SERL](https://github.com/rail-berkeley/hil-serl), including its actor–learner organization, demonstration replay, online human intervention, and image-based reward-classifier pipeline. This project extends that foundation to a KUKA platform and contact-rich deformable-surface manipulation.

## Safety

Real-robot force control can cause equipment damage or injury when frames, signs, limits, or contact thresholds are incorrect. Read the [robot-safety notes](docs/safety.md) before connecting any component to hardware. The materials in this repository are intended for controlled robotics research and are not a medical device.
