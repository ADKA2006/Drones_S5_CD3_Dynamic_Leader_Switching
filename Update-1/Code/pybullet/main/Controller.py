import sys
import os
# for the buller lib
bullet_path = os.path.abspath("../bullet3/build_cmake/examples/pybullet")
if bullet_path not in sys.path:
    sys.path.insert(0, bullet_path)

import time
import pybullet as p
import pybullet_data
import numpy as np



pclient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0,0,-9.81)

dt = 1.0/240.0  # default timestep
p.setTimeStep(dt)

def clamp(x, low, high):
    return max(min(x, high), low)

# ground and drone
plane = p.loadURDF("plane.urdf")
drone = p.loadURDF("../bullet3/data/Quadrotor/quadrotor.urdf",[0,0,0.5],)

# Let the simulation settle for 20 steps
for _ in range(20):
    p.stepSimulation()

pos, orn = p.getBasePositionAndOrientation(drone)
x, y, z = pos
euler = p.getEulerFromQuaternion(orn)
roll, pitch, yaw = np.rad2deg(euler[0]), np.rad2deg(euler[1]), np.rad2deg(euler[2])

# Controller parameters
desired_roll = 0.0
desired_pitch = 0.0
desired_yaw = 0.0
# Kp = 42 # kp is the proportional gain, it is used to control the roll, pitch and yaw of the drone, it is used to calculate the torque required to achieve the desired roll, pitch and yaw
# Kd = 4 # kd is the derivative gain, it is used to control the roll, pitch and yaw of the drone, it is used to calculate the torque required to achieve the desired roll, pitch and yaw
tilt_constant = 5.0  # degrees
target_altitude = 2.0  
target_x = 0.0
target_y = 0.0
prev_x = x
prev_y = y
prev_altitude = z

Kp_pos = 1.5
Kd_pos = 0.8

Kp_alt = 17.0   # proportional gain
Ki_alt = 5.0    # integral gain
Kd_alt = 25.0   # derivative gain
mass = p.getDynamicsInfo(drone,-1)[0]# [0] is mass, [1] is lateral friction[2] is local inertia diagonal,[3] is local inertia position,[4] is local inertia orientation,[5] is restitution,[6] is rolling friction,[7] is spinning friction,[8] is contact damping,[9] is contact stiffness
hover_thrust = mass*9.81

Kp = 4.0 # Proportional gain for attitude
Kd = 1.0  # Derivative gain for gyro damping
k_yaw = 0.0245

holding_position = True

# For plotting
# Track the previous position to draw path lines
last_line_pos = [0.0, 0.0, 0.5]  # Matches your initial spawn point
trail_timer = 0

while p.isConnected():
    pos,orn = p.getBasePositionAndOrientation(drone)
    x,y,z = pos
    altitude = z

    euler = p.getEulerFromQuaternion(orn)
    roll = np.rad2deg(euler[0])
    pitch = np.rad2deg(euler[1])
    yaw = np.rad2deg(euler[2])

    lin_vel, ang_vel = p.getBaseVelocity(drone)
    vx,vy,vz = lin_vel
    wx,wy,wz = ang_vel

    # Keyboard inputs
    keys = p.getKeyboardEvents()
    
    # Check Exit Condition (Q or q key)
    if (ord('q') in keys and (keys[ord('q')] & p.KEY_IS_DOWN)) or (ord('Q') in keys and (keys[ord('Q')] & p.KEY_IS_DOWN)):
        print("bye")
        break

    key_active = False

    if p.B3G_LEFT_ARROW in keys and (keys[p.B3G_LEFT_ARROW] & p.KEY_IS_DOWN):
        desired_roll = tilt_constant
        key_active = True
    elif p.B3G_RIGHT_ARROW in keys and (keys[p.B3G_RIGHT_ARROW] & p.KEY_IS_DOWN):
        desired_roll = -tilt_constant
        key_active = True
    else:
        desired_roll = 0.0

    if p.B3G_UP_ARROW in keys and (keys[p.B3G_UP_ARROW] & p.KEY_IS_DOWN):
        desired_pitch = -tilt_constant
        key_active = True
    elif p.B3G_DOWN_ARROW in keys and (keys[p.B3G_DOWN_ARROW] & p.KEY_IS_DOWN):
        desired_pitch = tilt_constant
        key_active = True
    else:
        desired_pitch = 0.0

    if ord('e') in keys and (keys[ord('e')] & p.KEY_IS_DOWN):
        target_altitude += 0.01

    if ord('s') in keys and (keys[ord('s')] & p.KEY_IS_DOWN):
        target_altitude -= 0.01

    # 3. Position Controller
    if key_active:
        holding_position = False
    else:
        if not holding_position:
            target_x = x
            target_y = y
            holding_position = True

        # Position error
        error_x = target_x - x
        error_y = target_y - y

        desired_pitch = clamp(Kp_pos*error_x-Kd_pos* vx,-4.0,4.0)  
        desired_roll  = clamp(-Kp_pos*error_y + Kd_pos* vy,-4.0,4.0)
        desired_yaw   = 0.0

    prev_x = x
    prev_y = y

    # Altitude Controller
    vertical_speed = vz
    target_altitude = clamp(target_altitude,0.25,5.0)
    alt_error = target_altitude - altitude

    desired_thrust = hover_thrust + Kp_alt * alt_error - Kd_alt * vertical_speed
    desired_thrust = max(0.0,desired_thrust)
    prev_altitude = altitude



    costilt = np.cos(np.deg2rad(roll)) * np.cos(np.deg2rad(pitch))
    desired_thrust /= max(0.5, costilt)
    desired_thrust = max(0.0, desired_thrust)
    q_actual = orn
    q_desired = p.getQuaternionFromEuler([np.deg2rad(desired_roll), np.deg2rad(desired_pitch), np.deg2rad(desired_yaw)])
    error = p.getDifferenceQuaternion(q_actual, q_desired)
    if error[3] < 0:
        error = [-val for val in error]
    err_x = clamp(error[0],-1.0,1.0)
    err_y = clamp(error[1],-1.0,1.0)
    err_z = clamp(error[2],-1.0,1.0)
    Tx = Kp*err_x- Kd *wx
    Ty = Kp* err_y-Kd* wy
    Tz = Kp*err_z -Kd*wz
    Tx = clamp(Tx,-15.0,15.0)
    Ty = clamp(Ty,-15.0,15.0)
    Tz = clamp(Tz,-10.0,10.0)

    L = 0.175   # plus design quad check once more 
    f_base  = desired_thrust / 4.0
    f_pitch = Ty / (2.0*L)
    f_roll  = Tx / (2.0*L)
    # f_yaw   = Tz / (4.0*k_yaw)

    
    f1_raw = f_base-f_pitch
    f2_raw = f_base+f_roll   
    f3_raw = f_base+ f_pitch  
    f4_raw = f_base-f_roll  

    maxthrustpermotor = 20
    f1 = clamp(f1_raw,0.0,maxthrustpermotor)
    f2 = clamp(f2_raw,0.0,maxthrustpermotor)
    f3 = clamp(f3_raw,0.0,maxthrustpermotor)
    f4 = clamp(f4_raw,0.0,maxthrustpermotor)

    print(roll,desired_roll,Tx,err_x,err_y,err_z)

    rpositions = [[L,0,0],[0,L,0],[-L,0,0],[0,-L,0]]
    forces = [f1,f2,f3,f4]

    for force,pos in zip(forces,rpositions):
        p.applyExternalForce(drone,-1,[0,0,force],pos,p.LINK_FRAME)
    # netyaw = k_yaw *(f1-f2+ f3-f4)
    p.applyExternalTorque(drone, -1,[0,0,Tz],p.LINK_FRAME)
    p.stepSimulation()


        # Plot flight path segment every 5 simulation steps to avoid crowding the GPU
    trail_timer += 1
    if trail_timer % 5 == 0:
        current_pos, _ = p.getBasePositionAndOrientation(drone)
        
        # Draw a bright red line segment from the last position to the current position
        # lifeTime=30 keeps the line visible on screen for 30 seconds before fading
        p.addUserDebugLine(
            lineFromXYZ=last_line_pos,
            lineToXYZ=current_pos,
            lineColorRGB=[1, 0, 0],  # Red path [Red, Green, Blue]
            lineWidth=2,
            lifeTime=30.0  
        )
        
        # Update the history tracker
        last_line_pos = current_pos


    time.sleep(dt)

#     print(
#     f"key_active={key_active}"
#     f"Roll={roll:.2f}, Pitch={pitch:.2f}, "
#     f"DesiredRoll={desired_roll:.2f}, DesiredPitch={desired_pitch:.2f}, "
#     f"Tx={Tx:.2f}, Ty={Ty:.2f}"
# )
if p.isConnected():
    p.disconnect()
    print("Disconnected")