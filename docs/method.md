# Method overview

## Problem formulation

Press-based skin-fold retraction aims to create an exposed working region on a deformable, skin-like surface by pressing and moving the tissue laterally. Unlike grasp-based retraction, the robot does not depend on pinching an edge. The task is contact-rich: appearance can be ambiguous, the surface geometry changes during the motion, and excessive normal or tangential force can invalidate an otherwise plausible trajectory.

The system therefore separates high-level task decisions from low-level contact regulation. A learned policy proposes normalized task actions, while a phase-aware controller determines which action dimensions are physically meaningful at each stage of interaction.

## System components

### Passive compliance

The pressing end effector provides mechanical compliance at the contact interface. This reduces sensitivity to small surface-normal and calibration errors and complements the software force controller. Mechanical compliance does not replace force limits, workspace bounds, or emergency-stop supervision.

### Contact-aware shared control

A sigma.7 haptic master supplies robot-frame motion commands for demonstrations and online interventions. The operator and learned policy use the same task-level action representation, so intervention transitions remain compatible with the policy replay buffer.

The execution layer uses three phases:

1. `FREE_SPACE`: 6D position and orientation motion brings the tool to the task region.
2. `PRECONTACT_Z_ONLY`: lateral motion and orientation are locked while the tool approaches the surface.
3. `CONTACT_HYBRID`: tangential position commands remain active and the normal direction switches to force control.

Contact detection uses force/torque measurements with hysteresis to prevent rapid phase oscillation around a single threshold.

### Multimodal success estimation

The reward estimator receives two complementary signals:

- wrist and side RGB views describe fold geometry and the exposed region;
- a history of wrist force and torque describes contact quality, loading, slip, and unstable interactions.

This combination distinguishes visually similar states whose contact conditions differ. In particular, force history provides evidence for hard negatives such as excessive pressing, local sticking, or an unstable exposure.

### Human-in-the-loop reinforcement learning

The training workflow combines demonstrations, online actor experience, and human interventions. The actor executes the learned policy by default. When the operator intervenes through the haptic interface, the intervention action replaces the policy action and the transition is recorded as additional corrective experience. An asynchronous learner updates the policy from the mixed replay sources and periodically synchronizes parameters back to the actor.

## Observation and action spaces

The task observation contains multi-view images and robot proprioception:

```text
images = {wrist_rgb, side_rgb}
state  = {tcp_pose, tcp_velocity, tcp_force, tcp_torque}
```

The normalized 7D action preserves a conventional 6D delta-pose prefix and appends a normal-force increment:

```text
action[0:3] = Cartesian position increment
action[3:6] = Cartesian rotation-vector increment
action[6]   = normal-force increment
```

Inactive components are projected to zero according to the current phase. The projection is deterministic and independently testable in [`action_semantics.py`](../src/press_based_skin_fold_retraction/action_semantics.py).

## Evaluation dimensions

Task success alone does not capture contact quality. The evaluation protocol therefore includes completion time, peak normal and tangential forces, contact duration, intervention counts, phase transitions, and hard safety violations. Reward-classifier evaluation additionally tracks F1, AUROC, and false-positive rate on visually ambiguous hard negatives.
