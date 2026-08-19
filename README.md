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

For UAV $i$:

$$
\mathbf{x}_i =
\begin{bmatrix}
\mathbf{p}_i\\
\mathbf{v}_i\\
\mathbf{q}_i\\
\boldsymbol{\omega}_i
\end{bmatrix}
$$

where:

- $\mathbf{p}_i$: position
- $\mathbf{v}_i$: velocity
- $\mathbf{q}_i$: attitude quaternion
- $\boldsymbol{\omega}_i$: angular velocity

---

### 2. Position Dynamics

$$
\dot{\mathbf{p}}_i = \mathbf{v}_i
$$

$$
m_i\dot{\mathbf{v}}_i = \mathbf{F}_i^W + m_i\mathbf{g} + \mathbf{d}_i
$$

where:

- $\mathbf{p}_i$: position of UAV $i$
- $\mathbf{v}_i$: velocity of UAV $i$
- $m_i$: mass of UAV $i$
- $\mathbf{F}_i^W$: total force acting on UAV $i$ in the world frame
- $\mathbf{g}$: gravitational acceleration vector
- $\mathbf{d}_i$: external disturbance acting on UAV $i$

--- 

### 3. Position Controller

The desired tilt (interpreted as acceleration) is obtained using a PD controller:

$$ 
\mathbf{\theta}_d = K_p(\mathbf{p}_d-\mathbf{p}) + K_d(\mathbf{v}_d-\mathbf{v})
$$

$K_p$ — Proportional gain: Determines how strongly the UAV responds to the position error.
Higher $K_p$ → UAV moves more aggressively toward the desired position.
Too high → may cause overshoot or oscillation.

$K_d$ — Derivative gain: Determines how strongly the UAV responds to the velocity error. It helps reduce overshoot and stabilize the motion.
Higher $K_d$ → more damping/smoother response.
Too high → response can become slow or sensitive to noise.

---

### 4. Quaternion Attitude Control

UAV orientation is represented using a unit quaternion:

$$
q=[q_0,q_1,q_2,q_3]
$$

The desired UAV orientation is represented by the desired quaternion $q_d$.\
The quaternion tracking error between the desired and current orientations is calculated as:

$$
q_e=q_d\otimes q^{-1}
$$

where:

- $q_e$: quaternion attitude error
- $q_d$: desired attitude quaternion

And Desired Thrust $T$

$$
\boldsymbol{\T} = \T_{hover} + K_{p}e_{z} - K_{d}v_{z}
$$

The attitude controller generates the desired torque:

$$
\boldsymbol{\tau} = K_q\mathbf{e}_q - K_\omega\boldsymbol{\omega} 
$$

- $\boldsymbol{\tau}$: desired control torque
- $K_q$: attitude-error proportional gain
- $\mathbf{e}_q$: vector part of the quaternion attitude error
- $K_\omega$: angular-velocity damping gain
- $\boldsymbol{\omega}$: current angular velocity

where 
- $K_q\mathbf{e}_q$ generates a corrective torque that drives the UAV toward the desired orientation and
- $-K_\omega\boldsymbol{\omega}$ provides damping and reduces excessive rotational motion.

---

### 5. Motor Mixing

The position and attitude controllers generate the required total thrust and body torques:

$$
\mathbf{u}=
\begin{bmatrix}
T\\
\tau_x\\
\tau_y\\
\tau_z
\end{bmatrix}
$$

where:

- $T$: total thrust
- $\tau_x$: roll torque
- $\tau_y$: pitch torque
- $\tau_z$: yaw torque

These control inputs are converted into individual motor commands using a motor-mixing matrix:

$$
\begin{bmatrix} \omega_1\\ \omega_2\\ \omega_3\\ \omega_4 \end{bmatrix} = M 
\begin{bmatrix}
T\\
\tau_x\\
\tau_y\\
\tau_z
\end{bmatrix}
$$

where:

- $\omega_1,\omega_2,\omega_3,\omega_4$: commanded angular speeds of the four motors
- $M$: motor-mixing matrix determined by the quadrotor configuration and motor arrangement

The motor mixer distributes the required thrust and torques among the four motors. Differences in motor speeds generate the required **roll, pitch, and yaw torques**, while the combined motor thrust controls the UAV's vertical motion.

---
## To be Implemented 
---

### 6. UAV Health Vector

For each UAV $i$, the operational health vector is defined as:

$$
\mathbf{h}_i=
[B_i,C_i,M_i]^T
$$

where:

| Symbol | Parameter |
|---|---|
| $B_i$ | Battery health |
| $C_i$ | Communication quality |
| $M_i$ | Mission progress |

These parameters are selected based on information available within the UAV simulation and control system, without requiring additional external environmental sensors.

All parameters are normalized to the range:

$$
0\leq h_{ik}\leq1
$$

where $h_{ik}$ represents the normalized value of the $k$-th health parameter for UAV $i$. A higher value indicates better suitability for performing the leader role.

---

### 7. Battery Health

The battery level of UAV $i$ is normalized with respect to its maximum available energy:

$$
b_i=\frac{E_i}{E_{\max}}
$$

where:

- $E_i$: current battery energy of UAV $i$
- $E_{\max}$: maximum battery energy

To account for the minimum safe operating battery level, the battery health score is defined as:

$$
B_i=
clip
\left(
\frac{b_i-B_{\min}}
{1-B_{\min}},0,1
\right)
$$

where:

- $B_{\min}$: minimum safe normalized battery level
- $B_i$: normalized battery health score
- $clip(x,0,1)$: limits the value of $x$ to the range $[0,1]$

A higher $B_i$ indicates better battery suitability for the leader role. When the battery level approaches the minimum safe threshold, $B_i$ approaches zero, reducing the UAV's likelihood of being selected as the leader.

---

### 8. Communication Quality

Communication quality is evaluated using the communication information already available between the two UAVs. The quality score can combine packet delivery ratio and communication delay:

$$
C_i=
\alpha PDR_i+
\beta(1-D_i)
$$

where:

- $C_i$: communication quality score of UAV $i$
- $PDR_i$: packet delivery ratio
- $D_i$: normalized communication delay
- $\alpha$: weight assigned to packet delivery
- $\beta$: weight assigned to communication delay

The weights satisfy:

$$
\alpha+\beta=1
$$

The packet delivery ratio is calculated as:

$$
PDR_i=
\frac{N_{\text{received}}}
{N_{\text{sent}}}
$$

where:

- $N_{\text{received}}$: number of successfully received packets
- $N_{\text{sent}}$: total number of transmitted packets

The communication delay is normalized to the range $[0,1]$, where a lower delay produces a higher communication-quality contribution. Therefore, a higher $C_i$ indicates a more reliable communication link and greater suitability for the leader role.

---

### 9. Mission Progress

Mission progress represents how much of the assigned mission has been completed by UAV $i$. It can be calculated using the completed mission distance relative to the total mission distance:

$$
M_i =
\frac{d_{\text{completed},i}}
{d_{\text{mission}}}
$$

where:

- $M_i$: normalized mission progress of UAV $i$
- $d_{\text{completed},i}$: distance covered by UAV $i$ along the mission
- $d_{\text{mission}}$: total mission distance

The value of $M_i$ is limited to the range:

$$
0\leq M_i\leq1
$$

A higher $M_i$ indicates that the UAV has made greater progress along the mission and may be more suitable to continue as the leader. Since both UAVs operate within the same mission, this parameter can be used together with battery, GPS confidence, and communication quality to determine the overall leadership score.

---

### Leadership Score

The overall leadership score for UAV $i$ is calculated as a weighted combination of its battery health, communication quality, and mission progress:

$$
\boxed{
S_i=
w_BB_i+
w_CC_i+
w_MM_i
}
$$

where:

- $S_i$: overall leadership score of UAV $i$
- $B_i$: battery health
- $C_i$: communication quality
- $M_i$: mission progress
- $w_B$: weight assigned to battery health
- $w_C$: weight assigned to communication quality
- $w_M$: weight assigned to mission progress

The weights satisfy:

$$
w_B+w_C+w_M=1
$$

and each parameter is normalized to:

$$
0\leq B_i,C_i,M_i\leq1
$$

Therefore, the resulting leadership score satisfies:

$$
0\leq S_i\leq1
$$

A higher $S_i$ indicates that the UAV is more suitable to perform the leader role. The UAV with the highest suitable leadership score is selected as the preferred leader, subject to the dynamic switching conditions defined in the following section.

---

### Dynamic Leader Switching

A simple instantaneous leader-selection rule is:

$$
L=\arg\max_i S_i
$$

where $L$ represents the selected leader and $S_i$ is the leadership score of UAV $i$.

However, selecting the leader solely based on the instantaneous highest score may cause frequent switching when the scores fluctuate due to small changes in battery, communication quality, or mission progress.

To prevent unnecessary switching, a **hysteresis condition** is introduced.

If UAV $L$ is the current leader and UAV $j$ is the candidate leader, switching is allowed only when the candidate has a sufficiently higher leadership score:

$$
\boxed{
S_j>S_L+\Delta_S
}
$$

where:

- $S_j$: leadership score of the candidate UAV
- $S_L$: leadership score of the current leader
- $\Delta_S$: minimum score difference required to trigger a leader switch

A **minimum dwell time** is also imposed so that the current leader remains active for a minimum period before another switch can occur:

$$
t-t_{\text{switch}}>T_{\min}
$$

where:

- $t$: current simulation time
- $t_{\text{switch}}$: time at which the previous leader switch occurred
- $T_{\min}$: minimum required dwell time between consecutive leader switches

Therefore, a leadership transition occurs only when both conditions are satisfied:

$$
\boxed{
S_j>S_L+\Delta_S
\quad\land\quad
t-t_{\text{switch}}>T_{\min}
}
$$

When the conditions are satisfied, UAV $j$ becomes the new leader and the previous leader $L$ becomes the follower.

This hysteresis-based switching mechanism prevents **leader chattering**, avoids unnecessary role changes, and provides more stable cooperative navigation.

---

### Leader-Follower Navigation

The active leader follows the predefined mission trajectory:

$$
\mathbf{p}_L^d(t) = \mathbf{p}_{mission}(t)
$$

where:

- $\mathbf{p}_L^d(t)$: desired position of the leader
- $\mathbf{p}_{mission}(t)$: desired mission trajectory

The follower maintains a predefined relative position with respect to the leader:

$$
\mathbf{p}_F^d = \mathbf{p}_L+ R(\psi_L)\mathbf{r}_{LF}
$$

where:

- $\mathbf{p}_F^d$: desired position of the follower
- $\mathbf{p}_L$: current position of the leader
- $R(\psi_L)$: rotation matrix based on the leader's yaw angle
- $\psi_L$: leader yaw angle
- $\mathbf{r}_{LF}$: desired leader-to-follower formation offset

The follower's desired acceleration is calculated using the same PD position controller:

$$
\mathbf{a}_F^d = K_p(\mathbf{p}_F^d-\mathbf{p}_F) + K_d(\mathbf{v}_F^d-\mathbf{v}_F)
$$

where:

- $\mathbf{p}_F$: current follower position
- $\mathbf{v}_F^d$: desired follower velocity
- $\mathbf{v}_F$: current follower velocity
- $K_p$: proportional position gain
- $K_d$: derivative velocity gain

The resulting desired acceleration is passed to the existing low-level position and attitude control layers to generate the required motor commands.

---

# Seamless Leader Transition

When a leadership switch occurs, the roles of the two UAVs are exchanged without changing the overall mission trajectory.

```text
Before Switching

UAV 1 → Leader → Mission Trajectory
UAV 2 → Follower → Formation Offset

              ↓
       UAV 1 Score Decreases
              ↓
       UAV 2 Score Becomes Higher
              ↓
       Switching Conditions Satisfied
              ↓

After Switching

UAV 1 → Follower → Formation Offset
UAV 2 → Leader → Same Mission Trajectory
```

## Expected Results

- Stable UAV attitude control using a Python-based quaternion controller.
- Adaptive leader selection based on battery, position accuracy, communication, and mission progress.
- Reduced unnecessary leader switching using hysteresis and minimum dwell time.
- Continuous dual-UAV formation during leader transitions.
- Improved mission reliability compared with a fixed-leader system.

## Conclusion

The proposed system enables two UAVs to dynamically switch leadership based on their operating conditions. By combining adaptive leadership scoring, hysteresis, and minimum dwell time, the system is expected to provide stable leader selection and continuous cooperative navigation. The approach will be validated through Webots simulation under different UAV operating conditions.
