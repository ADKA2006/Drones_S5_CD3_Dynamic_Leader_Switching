# Adaptive Dynamic Leader Switching for Dual-UAV Cooperative Navigation

## Abstract

This project presents an **Adaptive Dynamic Leader Switching framework for dual-UAV cooperative navigation**.

Instead of assigning a permanent leader to one UAV, the system continuously evaluates the operational condition of both UAVs and dynamically selects the most suitable leader.

The leader selection is based on multiple factors such as:

* Battery level
* GPS confidence
* Obstacle visibility
* Communication quality
* Mission progress
* Wind stability

When the current leader becomes less suitable due to battery degradation, poor GPS quality, communication problems, wind disturbance, or other operational conditions, leadership is transferred to the better-performing UAV.

The system is developed and evaluated using the **Webots robotics simulator** with a dual-UAV cooperative navigation setup.

---

# 1. Problem Statement

Traditional leader-follower UAV systems generally assume that one UAV remains the leader throughout the mission.

This creates a potential failure point:

* The leader may experience low battery.
* GPS accuracy may degrade.
* Communication quality may decrease.
* Wind disturbances may affect stability.
* Obstacle visibility may become poor.
* The leader may become less suitable for continuing the mission.

If the leader is no longer reliable, a fixed-leader system can experience degraded formation performance or mission failure.

This project addresses this problem by introducing an **adaptive leader selection mechanism** that continuously evaluates UAV health and allows leadership to switch between UAVs when required.

---

# 2. Research Gap

The project focuses on the following limitations in conventional leader-follower systems.

### 2.1 Fixed Leader Assumption

Many formation-control approaches assume that the leader remains fixed throughout the mission.

### 2.2 Lack of Multi-Criteria UAV Health Assessment

Leader selection is often not explicitly based on a combination of operational factors such as battery, GPS confidence, communication, wind stability, and mission progress.

### 2.3 Unstable or Unnecessary Switching

If leadership is changed whenever a small difference occurs between UAV conditions, frequent switching can occur.

This project therefore introduces:

* Multi-criteria UAV health assessment
* Adaptive leader selection
* Hysteresis
* Minimum leader dwell time

to achieve more stable leader transitions.

---

# 3. Objectives

The main objectives of the project are:

1. Develop a functional single-UAV flight controller in Webots.
2. Extend the system to dual-UAV cooperative navigation.
3. Develop a multi-criteria UAV health assessment system.
4. Dynamically select the most suitable UAV as the leader.
5. Implement stable leader switching using hysteresis and minimum dwell time.
6. Evaluate the proposed approach under different UAV degradation and environmental conditions.

---

# 4. Proposed System

The proposed system consists of two UAVs operating cooperatively in a simulated environment.

At every decision interval, the condition of each UAV is evaluated.

The following factors are considered:

| Parameter             | Purpose                                                   |
| --------------------- | --------------------------------------------------------- |
| Battery Level         | Determines remaining energy availability                  |
| GPS Confidence        | Represents navigation reliability                         |
| Obstacle Visibility   | Represents the UAV's ability to perceive its surroundings |
| Communication Quality | Represents communication reliability                      |
| Mission Progress      | Represents progress toward the mission objective          |
| Wind Stability        | Represents the effect of environmental disturbance        |

These parameters are combined to obtain a **leader suitability score** for each UAV.

The UAV with the better overall condition is selected as the leader.

---

# 5. Dynamic Leader Switching

The system does not permanently assign one UAV as the leader.

For example:

```text
Initial Mission

UAV A → Leader
UAV B → Follower
```

If the condition of UAV A deteriorates:

```text
UAV A
Battery ↓
GPS Confidence ↓
Stability ↓
        ↓
Leader suitability decreases
        ↓
Leader switching condition satisfied
        ↓
UAV B → New Leader
UAV A → Follower
```

The mission continues without restarting the entire navigation process.

This allows the system to adapt to changing UAV conditions.

---

# 6. Stable Switching Mechanism

Directly switching the leader whenever the scores change can result in **leader chattering**.

For example:

```text
Time     UAV A     UAV B
-------------------------
t1       0.81      0.79
t2       0.80      0.81
t3       0.82      0.80
t4       0.79      0.82
```

Without additional control logic, leadership could repeatedly change.

To prevent this, the proposed system uses:

### Hysteresis

A new UAV must have a sufficiently better score than the current leader before switching occurs.

### Minimum Dwell Time

After a leader switch, the system keeps the new leader for a minimum amount of time before another switch is allowed.

This improves switching stability and avoids unnecessary transitions.

---

# 7. Project Methodology

The project is divided into four main implementation phases.

## Phase 1 — Single-UAV Webots Control Foundation

Develop and stabilize the basic UAV controller.

Implemented components include:

* Webots UAV simulation
* GPS
* IMU
* Gyroscope
* Position control
* Altitude control
* Quaternion attitude representation
* Quaternion-based attitude error
* Attitude control
* Torque generation
* Motor mixing
* Basic UAV stabilization

---

## Phase 2 — Dual-UAV Cooperative Navigation

Extend the working single-UAV system to two UAVs.

Main tasks:

* Spawn two UAVs in Webots.
* Establish UAV-to-UAV state exchange.
* Define leader and follower roles.
* Generate a common mission trajectory.
* Implement leader navigation.
* Implement follower formation control.
* Maintain a predefined relative formation.
* Ensure both UAVs can navigate cooperatively.

Expected structure:

```text
             Mission Trajectory
                    |
                    v
             +-------------+
             |   Leader    |
             |    UAV      |
             +-------------+
                    |
          Position / State
                    |
                    v
             +-------------+
             |  Follower   |
             |    UAV      |
             +-------------+
```

---

## Phase 3 — Adaptive Dynamic Leader Switching

Introduce the main contribution of the project.

For each UAV, estimate:

* Battery condition
* GPS confidence
* Obstacle visibility
* Communication quality
* Mission progress
* Wind stability

These parameters are used to calculate the overall suitability of each UAV for leadership.

The system then:

1. Monitors both UAVs.
2. Updates their health information.
3. Calculates leader suitability.
4. Compares the current leader with the alternative UAV.
5. Checks the hysteresis condition.
6. Checks the minimum dwell-time condition.
7. Switches leadership when required.
8. Transfers the navigation responsibility to the new leader.
9. Continues the mission.

---

## Phase 4 — Robustness Evaluation and Comparison

The final stage evaluates the proposed system under different operating conditions.

### Normal Operation

Both UAVs operate normally without degradation.

### Battery Degradation

The current leader gradually loses battery capacity.

Expected behavior:

```text
UAV A → Leader
Battery degradation
       ↓
UAV B becomes more suitable
       ↓
UAV B → Leader
```

### GPS Degradation

GPS confidence of the current leader is reduced.

The system should identify the other UAV as a more reliable navigation source.

### Communication Degradation

Communication quality between UAVs is degraded.

The system evaluates the effect on leader selection and cooperative navigation.

### Wind Disturbance

Environmental disturbance is introduced to evaluate UAV stability.

The UAV maintaining better navigation performance should become more suitable for leadership.

### Obstacle/Visibility Degradation

Obstacle visibility or perception quality is reduced for one UAV.

The other UAV can become the preferred leader if its operational condition is better.

### Combined Degradation

Multiple factors are degraded simultaneously to evaluate the robustness of the complete system.

---
# 8. Implementation Status

## Completed

The following components have been implemented and tested at the current stage:

* Webots UAV simulation
* Single-UAV flight simulation
* GPS integration
* IMU integration
* Gyroscope integration
* Position control
* Altitude control
* Quaternion attitude representation
* Quaternion attitude error calculation
* Quaternion-based attitude control
* Torque generation
* Motor mixing
* Basic UAV stabilization

The current implementation establishes the basic flight-control foundation required for the cooperative navigation layer.

---

## Currently Being Implemented

The next development stage focuses on:

* Mission trajectory generation
* Dual-UAV simulation
* Leader-follower formation
* UAV-to-UAV state communication
* Relative position maintenance
* Multi-criteria health estimation
* Leader suitability scoring
* Dynamic leader selection
* Hysteresis mechanism
* Minimum dwell-time mechanism
* Seamless leader transition

---

## Final Implementation

The completed system will include:

```text
Single UAV Control
        ↓
Dual UAV Formation
        ↓
Health Monitoring
        ↓
Leader Suitability Evaluation
        ↓
Dynamic Leader Selection
        ↓
Hysteresis + Dwell Time
        ↓
Leader Transition
        ↓
Mission Continuation
```

---

# 9. Expected Evaluation Metrics

The system will be evaluated using the following metrics:

### Mission Completion

Whether the UAV team successfully completes the assigned mission.

### Formation Error

Difference between the desired and actual relative UAV positions.

### Position Tracking Error

Measures how accurately the UAV follows its assigned trajectory.

### Leader Switching Frequency

Number of leader changes during a mission.

### Leader Switching Response Time

Time required to detect a degraded leader and perform the transition.

### Mission Continuity

Measures whether the mission continues smoothly after a leader transition.

### Robustness

Measures system performance under battery, GPS, communication, wind, and obstacle-related degradation.

### Stability

Evaluates whether the system avoids excessive or unnecessary leader switching.

---

# 10. Experimental Scenarios

The following experiments will be considered:

| Experiment | Condition                                  |
| ---------- | ------------------------------------------ |
| E1         | Normal dual-UAV operation                  |
| E2         | Leader battery degradation                 |
| E3         | Leader GPS degradation                     |
| E4         | Leader communication degradation           |
| E5         | Wind disturbance                           |
| E6         | Obstacle visibility degradation            |
| E7         | Combined UAV degradation                   |
| E8         | Fixed leader vs adaptive leader comparison |

The final experiment compares the proposed adaptive approach against a conventional fixed-leader configuration.

---

# 11. Expected Contribution

The primary contribution of this project is an **adaptive leader-selection mechanism for dual-UAV cooperative navigation**.

The proposed system moves away from the conventional assumption of a permanently fixed leader and instead considers the changing operational condition of each UAV.

The project combines:

* Multi-criteria UAV health assessment
* Adaptive leader selection
* Hysteresis-based switching
* Minimum dwell-time protection
* Dual-UAV cooperative navigation
* Webots-based simulation
* Robustness evaluation under UAV and environmental degradation

The goal is to enable the UAV team to maintain mission continuity even when the current leader becomes less suitable for the mission.

---

# 12. Project Status

**Current Stage:** Webots simulation and single-UAV flight controller are operational.

**Next Major Milestone:** Integrate the dual-UAV leader-follower layer and implement the multi-criteria dynamic leader-switching mechanism.

**Final Goal:** Demonstrate that adaptive leader switching can provide better mission continuity and robustness than a conventional fixed-leader approach under different UAV degradation scenarios.

---

# 13. Conclusion

This project develops a Webots-based dual-UAV cooperative navigation system with adaptive dynamic leader switching.

By continuously evaluating UAV operational conditions and transferring leadership when necessary, the system aims to reduce dependence on a single fixed leader and improve mission continuity and robustness under changing conditions.
