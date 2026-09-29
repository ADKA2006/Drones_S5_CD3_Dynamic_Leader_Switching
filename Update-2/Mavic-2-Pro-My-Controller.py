"""Mavic-2-Pro-My-Controller controller."""
import socketio

from controller import Supervisor
from Webots_Object import ObjectManager

from controller import Robot, Keyboard
from Quaternion import quaternion_ijk as quaternion
from Quaternion import euler2quaternion as e2q
from Quaternion import quaternion2euler as q2e
import numpy as np

from Cubic_B_Spline import BSpline
robot = Supervisor()
keyboard = Keyboard()
manager = ObjectManager(robot)

POINTS = []
tempx = []
tempy = []
tempz = []


socket = socketio.Client()

@socket.on("connect")
def connect():
    print("connected")

@socket.on("BSpline")
def BSpline_Function(data):
    global tempx, tempy, tempz
    for i in data["CPts"]:
        POINTS.append(manager.createObject(
            position=i,
            size=(0.1, 0.1, 0.1),
            color=(0, 0, 0)
        ))
    tempx, tempy, tempz = BSpline(data["CPts"],data["p"])
    print(tempx)

socket.connect("http://127.0.0.1:5000")

socket.emit("sendData")




def clamp(x, low, high):
    return max(min(x, high), low)
    
from itertools import permutations

def get_permutations(lst):
    return [list(p) for p in permutations(lst)]

# t timestep = (int)wb_robot_get_basic_time_step();

 # Get and enable devices.
# DeviceTag camera = wb_robot_get_device("camera");
# _camera_enable(camera, timestep);
# DeviceTag front_left_led = wb_robot_get_device("front left led");
# DeviceTag front_right_led = wb_robot_get_device("front right led");
# DeviceTag imu = wb_robot_get_device("inertial unit");
# _inertial_unit_enable(imu, timestep);
# DeviceTag gps = wb_robot_get_device("gps");
# _gps_enable(gps, timestep);
# DeviceTag compass = wb_robot_get_device("compass");
# _compass_enable(compass, timestep);
# DeviceTag gyro = wb_robot_get_device("gyro");
# _gyro_enable(gyro, timestep);
# _keyboard_enable(timestep);
# DeviceTag camera_roll_motor = wb_robot_get_device("camera roll");
# DeviceTag camera_pitch_motor = wb_robot_get_device("camera pitch");
 # WbDeviceTag camera_yaw_motor = wb_robot_get_device("camera yaw");  // Not used in this example.

 # Get propeller motors and set them to velocity mode.
# DeviceTag front_left_motor = wb_robot_get_device("front left propeller");
# DeviceTag front_right_motor = wb_robot_get_device("front right propeller");
# DeviceTag rear_left_motor = wb_robot_get_device("rear left propeller");
# DeviceTag rear_right_motor = wb_robot_get_device("rear right propeller");
# DeviceTag motors[4] = {front_left_motor, front_right_motor, rear_left_motor, rear_right_motor};
timestep = int(robot.getBasicTimeStep())
front_left_motor = robot.getDevice("front left propeller")
front_right_motor = robot.getDevice("front right propeller")
rear_left_motor = robot.getDevice("rear left propeller")
rear_right_motor = robot.getDevice("rear right propeller")
gyro = robot.getDevice("gyro")
gyro.enable(timestep)
gps = robot.getDevice("gps")
gps.enable(timestep)

imu = robot.getDevice("inertial unit")
imu.enable(timestep)

motors = [front_left_motor,front_right_motor,rear_right_motor,rear_left_motor]
flag = True
for i in motors:
    i.setPosition(float("inf"))
    if flag:
        i.setVelocity(68.5)
    else:
        i.setVelocity(-68.5)
    flag = not flag

        
# while robot.step(timestep) != -1:
    # if robot.getTime()>1:
        # break
temp = 0
# desired_thrust = 70
roll, pitch, yaw = None, None, None
while robot.step(timestep) != -1:
    if robot.getTime()>0.1:
        roll, pitch, yaw = imu.getRollPitchYaw()
        roll = np.rad2deg(roll)
        pitch = np.rad2deg(pitch)
        yaw = np.rad2deg(yaw)
        break
# desired_roll = roll
# desired_pitch = pitch
# desired_yaw = yaw
desired_roll = 0
desired_pitch = 0
desired_yaw = 0
Kp = 42
Kd = 4

tilt_constant = 5

target_altitude = 2
target_x = 0
target_y = 0
prev_x = 0
prev_y = 0
Kp_pos = 1.5
Kd_pos = 0.8


Kp_alt = 17
Ki_alt = 5
Kd_alt = 25
alt_integral = 0.0
prev_error = 0.0
hover_thrust = 45    # Find experimentally
dt = timestep / 1000.0
prev_altitude = 0
holding_position = True

index_for_socket = 0

while robot.step(timestep) != -1:
    value = keyboard.getKey()
    x, y, z = gps.getValues()
    if value!=-1:    
        holding_position = False
        if value==314:
            desired_roll = tilt_constant
        elif value==315:
            desired_pitch = -tilt_constant
        elif value==316:
            desired_roll = -tilt_constant
        elif value==317:
            desired_pitch = tilt_constant
    else:

        # First frame after releasing the key
        if not holding_position:
            target_x = x
            target_y = y
    
            holding_position = True
    
        # Position error
        error_x = target_x - x
        error_y = target_y - y
    
        # GPS velocity
        vx = (x - prev_x) / dt
        vy = (z - prev_y) / dt
    
        prev_x = x
        prev_y = z
    
        # Position controller
        desired_pitch = (
            Kp_pos * error_x
            - Kd_pos * vx
        )
    
        desired_roll = (
            -Kp_pos * error_y
            + Kd_pos * vy
        )
    
        desired_roll = clamp(desired_roll, -4, 4)
        desired_pitch = clamp(desired_pitch, -4, 4)
    
        desired_yaw = 0
    _, _, altitude = gps.getValues()
    
    vertical_speed = (altitude - prev_altitude) / dt
    
    error = target_altitude - altitude
    
    desired_thrust = (
        hover_thrust
        + Kp_alt * error
        - Kd_alt * vertical_speed
    )
    
    prev_altitude = altitude
    
    # error = target_altitude - altitude
    
    # alt_integral += error * dt
    # alt_derivative = (error - prev_error) / dt
    
    # desired_thrust = (
        # hover_thrust
        # + Kp_alt * error
        # + Ki_alt * alt_integral
        # + Kd_alt * alt_derivative
    # )
    
    # prev_error = error
    
    
    roll, pitch, yaw = imu.getRollPitchYaw()
    roll = np.rad2deg(roll)
    pitch = np.rad2deg(pitch)
    yaw = np.rad2deg(yaw)
    
    desired_thrust /= max(0.5, np.cos(np.deg2rad(roll)) * np.cos(np.deg2rad(pitch)))
    
    q_actual = e2q(psi = yaw, theta = pitch, phi = roll)
    q_desired = e2q(psi = desired_yaw, theta = desired_pitch, phi = desired_roll)
    error = q_desired * q_actual.I # Conjugate is used in q_actual
    error = error * (1.0/error.N)
    if error.q0<0:
        error = -error
        # print("neg: ",robot.getTime())
    x = error.Q["i"]
    y = error.Q["j"]
    z = error.Q["k"]
    x = clamp(x,-1,1)
    y = clamp(y,-1,1)
    z = clamp(z,-1,1)
    wx, wy, wz = gyro.getValues()
    wx = wx
    wy = wy
    wz = wz
    # Tx = 50 * x - Kd * wx
    # Ty = 30 * y - Kd * wy
    # Tz = Kp * z - Kd * wz
    Tx = Kp * x - Kd * wx
    Ty = Kp * y - Kd * wy
    Tz = Kp * z - Kd * wz
    Tx = Tx*1
    Ty = Ty*1
    Tz = Tz*1
    # Tx = 0
    # Ty = 0
    # Tz = 5
    # Tz = 0
    Tx = clamp(Tx, -15, 15)
    Ty = clamp(Ty, -15, 15)
    Tz = clamp(Tz, -10, 10)
    # print("Torque: ",Tx,Ty,Tz)
    
    
    FL = desired_thrust - Tx + Ty - Tz
    FR = desired_thrust + Tx + Ty + Tz
    RL = desired_thrust - Tx - Ty + Tz
    RR = desired_thrust + Tx - Ty - Tz
    # print(f"Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}")
    # print(f"FL: {FL} FR: {FR} RL: {RL} RR: {RR}")
    # print(error)
    FL = clamp(FL, -576, 576)
    FR = clamp(FR, -576, 576)
    RL = clamp(RL, -576, 576)
    RR = clamp(RR, -576, 576)
    # front_left_motor.setVelocity(FL)
    # front_right_motor.setVelocity(-FR)
    # rear_left_motor.setVelocity(-RL)
    # rear_right_motor.setVelocity(RR)
    perm = get_permutations([FL,FR,RL,RR])
    # index = 10
    index = 23
    front_left_motor.setVelocity(perm[index][0])
    front_right_motor.setVelocity(-perm[index][1])
    rear_left_motor.setVelocity(-perm[index][2])
    rear_right_motor.setVelocity(perm[index][3])
    # print(roll, pitch, yaw)
    # print(q_actual)
    # print(q2e(q_actual))
    # print("Gyro: ",gyro.getValues())
    # print(f"Roll={roll:.2f}, x={x:.4f}, wx={wx:.4f}")
    # print(f"Pitch={pitch:.2f}, y={y:.4f}, wy={wy:.4f}")
    # print(f"Yaw={yaw:.2f}, z={z:.4f}, wz={wz:.4f}")
    if robot.getTime()>temp:
        # print(keyboard.getKey())
        # print(imu.getRollPitchYaw())
        # print(q_actual)
        # print(q_desired)
        # print(gps.getValues())
        x, y, z = gps.getValues()
        print("X: ", x, y, z)
        print(target_x, target_y, target_altitude)
        error_thingy = 0.5
        print("Len",len(tempx))
        if len(tempx)!=0 and abs(x-tempx[index_for_socket])<error_thingy and abs(y-tempy[index_for_socket])<error_thingy and abs(z-tempz[index_for_socket])<error_thingy:
            print("Inside IF")
            target_x = tempx[index_for_socket]
            target_y = tempy[index_for_socket]
            target_altitude = tempz[index_for_socket]
            index_for_socket += 1
            if index_for_socket>=len(tempx):
                for i in range(len(POINTS)):
                    manager.deleteObject(POINTS[i])
                tempx = []
        temp+=0.25
    pass