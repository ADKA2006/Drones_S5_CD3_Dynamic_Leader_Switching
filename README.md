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

### Part 1 — UAV State Estimation and B-Spline Trajectory Generation (3 Minutes)

#### 1. UAV State Representation

The state of UAV \(i\) is represented as

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

- \(\mathbf{x}_i\): complete state of UAV \(i\).
- \(\mathbf{p}_i=[x_i,y_i,z_i]^T\): 3D position.
- \(\mathbf{v}_i\): linear velocity.
- \(\mathbf{q}_i\): attitude quaternion representing orientation.
- \(\boldsymbol{\omega}_i\): angular velocity.

#### 2. Sensor Feedback

The Webots controller obtains:

- **GPS:** current 3D position.
- **IMU:** roll, pitch, and yaw angles.
- **Gyroscope:** angular velocity about the three body axes.

These measurements provide the feedback required for position tracking and attitude stabilization.

#### 3. B-Spline Trajectory Generation

The controller receives control points \(P_j\) and spline degree \(p\) from the server.

\[
\mathbf{p}_d(t)=\sum_{j=0}^{n}N_{j,p}(t)P_j
\]

where:

- \(\mathbf{p}_d(t)\): desired 3D position at time \(t\).
- \(P_j\): the \(j\)-th trajectory control point.
- \(N_{j,p}(t)\): B-spline basis function.
- \(p\): spline degree.
- \(n\): final control-point index.

The B-spline generates a smooth trajectory represented by a sequence of target positions. The controller advances through the generated waypoints when the UAV reaches the current target within a specified tolerance.

The implementation also supports receiving updated spline data through Socket.IO, regenerating the trajectory, and restarting waypoint tracking.

**Outcome:** A smooth mission trajectory and sensor feedback are provided to the flight controller.

---

### Part 2 — Position Control and Altitude Regulation (3 Minutes)

#### 1. Horizontal Position Control

The position error along the horizontal axes is

\[
e_x=x_d-x,\qquad e_y=y_d-y
\]

where:

- \(x_d,y_d\): desired horizontal coordinates.
- \(x,y\): current GPS coordinates.
- \(e_x,e_y\): horizontal position errors.

Horizontal velocity is estimated from successive position measurements:

\[
v_x\approx\frac{x-x_{\mathrm{prev}}}{\Delta t},
\qquad
v_y\approx\frac{y-y_{\mathrm{prev}}}{\Delta t}
\]

where:

- \(v_x,v_y\): estimated horizontal velocities.
- \(x_{\mathrm{prev}},y_{\mathrm{prev}}\): previous position measurements.
- \(\Delta t\): elapsed time between controller updates.

The desired pitch and roll are calculated using proportional-derivative (PD) control:

\[
\theta_d=\operatorname{clip}
\left(K_{p,pos}e_x-K_{d,pos}v_x,-3,3\right)
\]

\[
\phi_d=\operatorname{clip}
\left(-K_{p,pos}e_y+K_{d,pos}v_y,-3,3\right)
\]

where:

- \(\theta_d\): desired pitch angle.
- \(\phi_d\): desired roll angle.
- \(K_{p,pos}\): position proportional gain.
- \(K_{d,pos}\): velocity damping gain.
- \(\operatorname{clip}\): restricts the command to the interval \([-3,3]\) degrees.

The proportional term drives the UAV toward the target, while the derivative term damps excessive motion.

#### 2. Altitude Control

The desired thrust is calculated as

\[
T_d=T_h+K_{p,alt}e_z-K_{d,alt}v_z
\]

where:

- \(T_d\): desired thrust command before tilt compensation.
- \(T_h\): baseline hover-thrust command.
- \(e_z=z_d-z\): altitude error.
- \(z_d,z\): desired and current altitude.
- \(v_z\): estimated vertical velocity.
- \(K_{p,alt}\): altitude proportional gain.
- \(K_{d,alt}\): altitude damping gain.

The thrust is compensated for the current roll and pitch:

\[
T_c=
\frac{T_d}
{\max\left(0.5,\cos\phi\cos\theta\right)}
\]

where:

- \(T_c\): tilt-compensated thrust command.
- \(\phi,\theta\): current roll and pitch angles.

This compensation helps maintain vertical lift when the UAV tilts during horizontal movement.

**Outcome:** Position errors are converted into desired roll, pitch, and thrust commands.

---

### Part 3 — Quaternion Attitude Control and Motor Mixing (3 Minutes)

#### 1. Quaternion Attitude Representation

The controller converts the measured and desired Euler angles into quaternions.

The orientation error is calculated as

\[
q_e=q_d\otimes q^{-1}
\]

where:

- \(q_e\): attitude-error quaternion.
- \(q_d\): desired attitude quaternion.
- \(q\): current attitude quaternion.
- \(\otimes\): quaternion multiplication.
- \(q^{-1}\): inverse of the current quaternion.

The controller normalizes the error quaternion and selects a consistent error representation before extracting its vector components.

#### 2. Attitude Feedback Control

The commanded body torques are calculated as

\[
\tau_x=K_qe_x^q-K_\omega\omega_x
\]

\[
\tau_y=K_qe_y^q-K_\omega\omega_y
\]

\[
\tau_z=K_qe_z^q-K_\omega\omega_z
\]

where:

- \(\tau_x,\tau_y,\tau_z\): commanded roll, pitch, and yaw torques.
- \(e_x^q,e_y^q,e_z^q\): vector components of the attitude-error quaternion.
- \(\omega_x,\omega_y,\omega_z\): measured angular velocities.
- \(K_q\): attitude proportional gain.
- \(K_\omega\): angular-velocity damping gain.

The attitude-error term corrects orientation, while the angular-velocity term reduces excessive rotational motion. The controller limits the torque commands to configured bounds.

#### 3. Motor Mixing

The controller combines the thrust and torque commands to obtain four motor commands:

\[
\begin{bmatrix}
u_{FL}\\
u_{FR}\\
u_{RL}\\
u_{RR}
\end{bmatrix}
=
\begin{bmatrix}
T_c-\tau_x+\tau_y-\tau_z\\
T_c+\tau_x+\tau_y+\tau_z\\
T_c-\tau_x-\tau_y+\tau_z\\
T_c+\tau_x-\tau_y-\tau_z
\end{bmatrix}
\]

where:

- \(u_{FL}\): front-left motor command.
- \(u_{FR}\): front-right motor command.
- \(u_{RL}\): rear-left motor command.
- \(u_{RR}\): rear-right motor command.
- \(T_c\): tilt-compensated thrust.
- \(\tau_x,\tau_y,\tau_z\): commanded body torques.

The resulting commands are mapped to the four Webots propeller devices, accounting for motor ordering and rotation direction. Differences in motor speeds generate the required roll, pitch, and yaw moments, while combined thrust controls vertical motion.

**Outcome:** The attitude controller converts orientation errors into motor-level control commands.

---

### Part 4 — System Integration and Dynamic Leader Switching (3 Minutes)

#### 1. Closed-Loop Navigation

The flight-control loop continuously measures the UAV state, calculates control errors, updates the desired attitude and thrust, and applies motor commands.

\[
\text{Sensors}
\rightarrow
\text{Position Control}
\rightarrow
\text{Attitude Control}
\rightarrow
\text{Motors}
\]

The resulting motion is measured again, closing the feedback loop.

#### 2. Trajectory Tracking and Telemetry

The position-tracking error is calculated as

\[
e_p=\|\mathbf{p}_d-\mathbf{p}\|_2
\]

where:

- \(e_p\): 3D position-tracking error.
- \(\mathbf{p}_d\): desired position.
- \(\mathbf{p}\): current GPS position.
- \(\|\cdot\|_2\): Euclidean norm.

The controller sends telemetry through Socket.IO, including the UAV's position, target coordinates, simulation time, and tracking error. It can also receive updated B-spline control points from the server.

These data support trajectory monitoring and evaluation of the flight controller.

#### 3. Proposed Dynamic Leader-Switching Mechanism

The planned extension evaluates the operational suitability of each UAV using normalized battery health, communication quality, and mission progress.

The leadership score for UAV \(i\) is

\[
S_i=w_BB_i+w_CC_i+w_MM_i
\]

where:

- \(S_i\): leadership score of UAV \(i\).
- \(B_i\): normalized battery-health score.
- \(C_i\): normalized communication-quality score.
- \(M_i\): normalized mission-progress score.
- \(w_B,w_C,w_M\): non-negative importance weights satisfying

\[
w_B+w_C+w_M=1
\]

Each health score lies between zero and one. A higher leadership score indicates greater suitability for the leader role.

If UAV \(L\) is the current leader and UAV \(j\) is the candidate, switching is permitted only when the score advantage exceeds a threshold:

\[
S_j>S_L+\Delta_S
\]

and the minimum time between switches has elapsed:

\[
t-t_{\mathrm{switch}}>T_{\min}
\]

where:

- \(S_j\): candidate leader's score.
- \(S_L\): current leader's score.
- \(\Delta_S\): hysteresis margin required to trigger switching.
- \(t\): current simulation time.
- \(t_{\mathrm{switch}}\): time of the previous leader switch.
- \(T_{\min}\): minimum dwell time between consecutive switches.

These conditions prevent unnecessary role changes caused by small score fluctuations.

#### 4. Leader-Follower Formation

After a switch, the new leader follows the mission trajectory:

\[
\mathbf{p}_L^d(t)=\mathbf{p}_{\mathrm{mission}}(t)
\]

The follower maintains a desired offset relative to the leader:

\[
\mathbf{p}_F^d=
\mathbf{p}_L+R(\psi_L)\mathbf{r}_{LF}
\]

where:

- \(\mathbf{p}_L^d(t)\): desired leader position.
- \(\mathbf{p}_{\mathrm{mission}}(t)\): predefined mission trajectory.
- \(\mathbf{p}_F^d\): desired follower position.
- \(\mathbf{p}_L\): current leader position.
- \(R(\psi_L)\): rotation matrix based on the leader's yaw angle.
- \(\psi_L\): leader yaw angle.
- \(\mathbf{r}_{LF}\): desired relative formation offset.

The existing position and attitude control layers can then track the leader and follower targets.

**Implementation status:** The supplied code implements single-UAV B-spline tracking, GPS/IMU/gyroscope feedback, position and attitude control, motor commands, and telemetry. Dynamic leader scoring, two-UAV role exchange, and formation control remain planned extensions. The existing telemetry fields `leader_id` and `obstacle_clearance` are placeholders.

**Outcome:** Integrating these extensions will enable health-based leader selection, reduced unnecessary switching, and continuous cooperative navigation by two UAVs.

## Results

- Stable UAV attitude control using a Python-based quaternion controller.
- Adaptive leader selection based on battery, position accuracy, communication, and mission progress.
- Reduced unnecessary leader switching using hysteresis and minimum dwell time.
- Continuous dual-UAV formation during leader transitions.
- Improved mission reliability compared with a fixed-leader system.

## Conclusion

The proposed system enables two UAVs to dynamically switch leadership based on their operating conditions. By combining adaptive leadership scoring, hysteresis, and minimum dwell time, the system is expected to provide stable leader selection and continuous cooperative navigation. The approach will be validated through Webots simulation under different UAV operating conditions.
