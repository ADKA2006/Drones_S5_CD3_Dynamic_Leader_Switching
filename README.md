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

To prevent unnecessary switching caused by measurement fluctuations, the framework incorporates score hysteresis and a minimum leader dwell time. When leadership changes, the new leader continues the mission trajectory while the previous leader transitions to follower mode, maintaining formation continuity. The system is implemented and evaluated in a multi-UAV simulation environment using position control, quaternion-based attitude control, and motor-level dynamics.
