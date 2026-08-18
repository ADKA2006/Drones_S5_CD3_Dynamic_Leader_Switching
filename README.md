<div align="center">
  <figure>
    <img src="Misc/Images/Amritalogo.png" alt="AmritaLogo" width="500"> <br>
  </figure>
</div>

# IDDCD_CD3_Dynamic_Leader_Switching

# Group & Team Members
<table>
  <tr>
 <td colspan="3">Group - 2</td>

  </tr>
  <tr class="header">
    <td>Name</td>
    <td>Roll No</td>
    <td>Email-Id</td>
  </tr>
  <tr>
    <td>Advaith Krishna</td>
    <td>CB.SC.U4AIE24203</td>
    <td>cb.sc.u4aie24203@cb.students.amrita.edu</td>
  </tr>
  <tr>
    <td>Amudala Jashwanth</td>
    <td>CB.SC.U4AIE24204</td>
    <td>cb.sc.u4aie24204@cb.students.amrita.edu</td>
  </tr>
  <tr>
    <td>Bhuvan Rajasekar</td>
    <td>CB.SC.U4AIE24209</td>
    <td>cb.sc.u4aie24209@cb.students.amrita.edu</td>
  </tr>
  <tr>
    <td>Sachcith G N</td>
    <td>CB.SC.U4AIE24251</td>
    <td>cb.sc.u4aie24251@cb.students.amrita.edu</td>
  </tr>
</table>

## Abstract

Cooperative navigation of multiple Unmanned Aerial Vehicles (UAVs) commonly relies on a fixed leader-follower architecture, where one UAV continuously performs the leader role while the other follows its navigation commands. Although simple, this approach can reduce mission reliability when the leader experiences battery depletion, degraded positioning, communication loss, strong wind disturbances, or reduced environmental awareness.

This project proposes an Adaptive Dynamic Leader Switching framework for dual-UAV cooperative navigation, where leadership is dynamically assigned according to the real-time operational health of each UAV. A Multi-Criteria Health Assessment model evaluates battery level, GPS confidence, obstacle visibility, communication quality, mission progress, and wind stability. These factors are normalized and combined to generate a leadership score for each UAV. The UAV with the more favorable operational condition is selected as the leader.

To prevent unnecessary switching caused by measurement fluctuations, the framework incorporates score hysteresis(switching threshold/margin) and a minimum leader dwell time. When leadership changes, the new leader continues the mission trajectory while the previous leader transitions to follower mode, maintaining formation continuity. The system is implemented and evaluated in a multi-UAV simulation environment using position control, quaternion-based attitude control, and motor-level dynamics.

## Base Paper Metadata

- Journal: IEEE Transactions on Systems, Man, and Cybernetics: Systems
- Volume: 47
- Issue: 7
- Year: 2017
- Pages: 1217–1228
- DOI: 10.1109/TSMC.2016.2564931
- Publisher: IEEE
- Authors: Feng Li, Yongsheng Ding, MengChu Zhou, Lei Chen

## Base Paper Discussion

The paper proposes a dynamic leader-selection mechanism to overcome the limitations of fixed leader–follower formation control. The system uses a Fuzzy Inference System (FIS) to evaluate the status of individual robots and an affection-based model to determine when the current leader should be replaced. Followers generate unsatisfied signals based on their perception of the leader, and leader reselection is triggered when the accumulated dissatisfaction exceeds a predefined threshold. A swap-greedy algorithm is then used to establish the new leader–follower relationships while reducing overall travel distance.

The paper demonstrates through simulations that the proposed approach can autonomously recover from leader failures and continue mission execution. It also shows that delaying leader switching helps prevent excessive switching and instability.

However, the approach is designed for general multirobot systems and its leader-selection decision is primarily based on the affection/status model rather than an explicit, physically interpretable multi-criteria UAV health assessment. Furthermore, the paper assumes unrestricted communication and identifies limited communication and switching topology as future research challenges.

Our project extends this concept to dual-UAV cooperative navigation by replacing the affection-based selection mechanism with a measurable leadership score based on battery level, GPS confidence, communication quality, obstacle visibility, mission progress, and wind stability.

## Problem Statement
Conventional dual-UAV leader-follower systems use a fixed leader, creating a single point of failure when its battery, localization, communication, sensing, or stability deteriorates.
A dynamic mechanism is required to evaluate both UAVs using multiple operational criteria and identify the most suitable leader during the mission.
The system must switch leadership reliably without unnecessary chattering while maintaining formation and mission continuity.

## Novelty

| **No.** | **Novelty of Proposed Project**            | **Difference from Previous Paper**                                                                                                                                                        |
| ------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Multi-criteria UAV health assessment   | Uses battery, GPS confidence, obstacle visibility, communication quality, mission progress, and wind stability for leader selection.                                                      |
| 2   | Health-based adaptive leadership score | Replaces the previous affection/fuzzy-based selection concept with a quantitative weighted leadership score.                                                                              |
| 3   | Stable leader switching                | Introduces hysteresis and minimum dwell time to prevent unnecessary leader switching and chattering.                                                                                  |
| 4   | UAV-specific cooperative navigation    | Integrates dynamic leader switching with quaternion attitude control, position control, quadrotor dynamics, and Webots simulation while maintaining formation and mission continuity. |

## Project Objectives

1. To Develop a drone controlling python script which controls the attitude of the Drone.
2. Formulate an adaptive leadership score using battery level, position accuracy, communication status, and mission progress.
3. Design a hysteresis-based dynamic leader-selection mechanism with a minimum dwell time.
4. Integrate dynamic leader switching with dual-UAV leader-follower cooperative navigation.

## Brief Project Explanation

This project proposes an adaptive dynamic leader-switching system for two UAVs in cooperative navigation. Unlike a conventional fixed leader-follower system, the proposed method continuously evaluates the UAVs using information already available from the simulation and flight-control system, such as battery level, GPS/position accuracy, communication status, and mission progress.

A leadership score is calculated for each UAV based on these parameters. When the current leader becomes less suitable and the other UAV has a sufficiently higher score, leadership is transferred. Hysteresis and minimum dwell time are used to avoid unnecessary or rapid switching.

After switching, the new leader continues following the mission trajectory, while the previous leader automatically becomes the follower and maintains the required formation relative to the new leader.

## Methodology

### 1. UAV State

For UAV \(i\):

\[
\mathbf{x}_i =
\begin{bmatrix}
\mathbf{p}_i\\
\mathbf{v}_i\\
\mathbf{q}_i\\
\boldsymbol{\omega}_i
\end{bmatrix}
\]

where:

- \(\mathbf{p}_i\): position
- \(\mathbf{v}_i\): velocity
- \(\mathbf{q}_i\): attitude quaternion
- \(\boldsymbol{\omega}_i\): angular velocity

---
