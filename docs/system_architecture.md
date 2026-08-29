# System architecture

## Runtime control path

```mermaid
flowchart LR
    RGB[Wrist and side RGB] --> OBS[Task observation]
    ROBOT[Robot pose and velocity] --> OBS
    FT[Wrist force and torque] --> OBS
    OBS --> POLICY[Learned policy]
    RGB --> REWARD[Multimodal success estimator]
    FT --> HISTORY[Wrench history]
    HISTORY --> REWARD

    SIGMA[sigma.7 haptic master] --> SHARED[Shared-control interface]
    POLICY --> ARBITER{Policy or intervention}
    SHARED --> ARBITER
    ARBITER --> ACTION[Normalized 7D action]
    ACTION --> PHASE[Phase-aware action projection]
    FT --> CONTACT[Contact detector]
    CONTACT --> PHASE
    PHASE --> HYBRID[Hybrid position-force controller]
    HYBRID --> KUKA[KUKA LBR]
    KUKA --> ROBOT
    KUKA --> FT
```

The learned policy and human operator share one action interface. Arbitration occurs before phase projection, so both command sources receive the same low-level safety and hybrid-control treatment.

## Control state machine

```mermaid
stateDiagram-v2
    [*] --> FREE_SPACE
    FREE_SPACE --> PRECONTACT_Z_ONLY: approach gate enabled
    PRECONTACT_Z_ONLY --> CONTACT_HYBRID: contact detected
    CONTACT_HYBRID --> PRECONTACT_Z_ONLY: contact released
    PRECONTACT_Z_ONLY --> FREE_SPACE: approach gate disabled
    CONTACT_HYBRID --> FREE_SPACE: reset or override
```

| State | Locked coordinates | Commanded coordinates |
| --- | --- | --- |
| `FREE_SPACE` | None | Cartesian position and orientation |
| `PRECONTACT_Z_ONLY` | Tangential position and orientation | Approach-axis position |
| `CONTACT_HYBRID` | Approach-axis position and orientation | Tangential position and normal force |

## Learning path

The actor collects robot transitions and sends them to an asynchronous learner. Demonstrations and interventions form additional replay sources. The learner samples from online and human-provided experience, updates the policy and critics, and periodically publishes policy parameters back to the actor. The multimodal success estimator supplies the task reward used in the transition stream.

This organization follows the HIL-SERL actor–learner pattern while changing the robot platform, teleoperation interface, action meaning, and reward inputs for deformable-surface contact.
