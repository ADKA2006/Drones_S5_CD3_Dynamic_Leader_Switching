"""Mavic-2-Pro-My-Controller controller."""
import socketio
import numpy as np
from itertools import permutations

from controller import Supervisor, Keyboard
from Webots_Object import ObjectManager
from Quaternion import quaternion_ijk as quaternion
from Quaternion import euler2quaternion as e2q
from Quaternion import quaternion2euler as q2e
from Cubic_B_Spline import BSpline

robot = Supervisor()
keyboard = Keyboard()
manager = ObjectManager(robot)

POINTS = []
tempx = []
tempy = []
tempz = []
received_spline_data = None
spline_update_pending = False

socket = socketio.Client()

@socket.on("connect")
def connect():
    print("Connected")

    x, y, z = gps.getValues()
    socket.emit("sendData", {
        "x": float(x),
        "y": float(y),
        "z": float(z),
        "t": float(robot.getTime())
    })

@socket.on("BSpline")
def BSpline_Function(data):
    global received_spline_data, spline_update_pending

    received_spline_data = data
    spline_update_pending = True

    print("New B-spline data received from server")

def clamp(x, low, high):
    return max(min(x, high), low)

def get_permutations(lst):
    return [list(p) for p in permutations(lst)]  
    
def calculate_path_length(xs, ys, zs):
    if len(xs) < 2:
        return 0.0

    points = np.column_stack((xs, ys, zs))
    distances = np.diff(points, axis=0)

    return float(np.sum(np.linalg.norm(distances, axis=1)))
    
def apply_spline_update():
    global spline_update_pending
    global tempx, tempy, tempz
    global target_x, target_y, target_altitude
    global index_for_socket, POINTS, holding_position

    if not spline_update_pending or received_spline_data is None:
        return

    spline_update_pending = False
    data = received_spline_data

    try:
        new_x, new_y, new_z = BSpline(data["CPts"], data["p"])
        # original_length = calculate_path_length(tempx, tempy, tempz)

        # socket.emit("telemetry", {
            # "drone_id": "mavic_1",
            # "t": float(robot.getTime() - start_time),
            # "path_type": "Original",
            # "path_length": original_length
        # })

        if not len(new_x):
            print("New spline is empty; keeping the current path.")
            return

        # Create new control-point markers first.
        new_points = []
        for point in data["CPts"][1:]:
            new_points.append(manager.createObject(
                position=tuple(point),
                size=(0.1, 0.1, 0.1),
                color=data.get("colors", [1.0, 1.0, 1.0])
            ))

        # Remove old control-point markers.
        for point in POINTS:
            manager.deleteObject(point)

        POINTS = new_points
        tempx, tempy, tempz = new_x, new_y, new_z

        # Restart traversal on the newly calculated spline.
        index_for_socket = 0
        target_x = float(tempx[0])
        target_y = float(tempy[0])
        target_altitude = float(tempz[0])

        # Resume autonomous target tracking.
        holding_position = True

        print(f"Updated spline: {len(tempx)} points generated.")

    except (KeyError, TypeError, ValueError, IndexError) as exc:
        print(f"Could not update B-spline: {exc}")

timestep = int(robot.getBasicTimeStep())
keyboard.enable(timestep)

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


motors = [front_left_motor, front_right_motor, rear_right_motor, rear_left_motor]
for m in motors:
    m.setPosition(float("inf"))  
    m.setVelocity(0.0) 

robot.step(timestep)
start_time = robot.getTime()

socket.connect("http://127.0.0.1:5000")

print("B-spline data waiting from the server")
while robot.step(timestep) != -1 and received_spline_data is None:
    pass

flag = True
for i in received_spline_data["CPts"]:
    if flag:
        flag = False
        continue
    POINTS.append(manager.createObject(   
        position=(i[0], i[1], i[2]),
        size=(0.1, 0.1, 0.1),
        color=received_spline_data["colors"]
    ))
tempx, tempy, tempz = BSpline(received_spline_data["CPts"], received_spline_data["p"])
original_length = calculate_path_length(tempx, tempy, tempz)

socket.emit("telemetry", {
    "drone_id": "mavic_1",
    "t": float(robot.getTime() - start_time),
    "path_type": "Original",
    "path_length": original_length
})
print(f"Generated {len(tempx)} points. Starting motors and PID loop!")

roll, pitch, yaw = imu.getRollPitchYaw()
roll = np.rad2deg(roll)
pitch = np.rad2deg(pitch)
yaw = np.rad2deg(yaw)

desired_roll = 0
desired_pitch = 0
desired_yaw = yaw  # Lock onto initial heading so it doesn't spin violently on takeoff

Kp = 35   
Kd = 5    
tilt_constant = 5

# Start by targeting the first B-Spline point (or hover at (0,0,1.5) first)
target_x = tempx[0] if len(tempx) > 0 else 0.0
target_y = tempy[0] if len(tempy) > 0 else 0.0
target_altitude = tempz[0] if len(tempz) > 0 else 1.5

x, y, z = gps.getValues()
prev_x = x
prev_y = y
prev_altitude = z

Kp_pos = 1.5  
Kd_pos = 1.2  
Kp_alt = 17
Ki_alt = 5   

Kd_alt = 25
hover_thrust = 68.5 
dt = timestep / 1000.0
holding_position = True

index_for_socket = 0
temp = robot.getTime()

while robot.step(timestep) != -1:
    apply_spline_update()
    
    value = keyboard.getKey()
    x, y, z = gps.getValues()
    if value != -1:
        holding_position = False
        if value == 314:
            desired_roll = tilt_constant
        elif value == 315:
            desired_pitch = -tilt_constant
        elif value == 316:
            desired_roll = -tilt_constant
        elif value == 317:
            desired_pitch = tilt_constant
    else:
        if not holding_position:
            target_x = x
            target_y = y
            holding_position = True

        error_x = target_x - x
        error_y = target_y - y

        vx = (x - prev_x) / dt
        vy = (y - prev_y) / dt

        prev_x = x
        prev_y = y

        desired_pitch = clamp(Kp_pos * error_x - Kd_pos * vx, -3, 3)
        desired_roll = clamp(-Kp_pos * error_y + Kd_pos * vy, -3, 3)

    _, _, altitude = gps.getValues()
    vertical_speed = (altitude - prev_altitude) / dt
    error = target_altitude - altitude

    desired_thrust = ( 
        hover_thrust
        + Kp_alt * error
        - Kd_alt * vertical_speed
    )
    prev_altitude = altitude

    roll, pitch, yaw = imu.getRollPitchYaw()
    roll = np.rad2deg(roll)
    pitch = np.rad2deg(pitch)
    yaw = np.rad2deg(yaw)

    desired_thrust /= max(0.5, np.cos(np.deg2rad(roll)) * np.cos(np.deg2rad(pitch))) 

    q_actual = e2q(psi=yaw, theta=pitch, phi=roll)
    q_desired = e2q(psi=desired_yaw, theta=desired_pitch, phi=desired_roll)
    error_q = q_desired * q_actual.I  
    error_q = error_q * (1.0 / error_q.N)
    if error_q.q0 < 0:
        error_q = -error_q

    ex = clamp(error_q.Q["i"], -1, 1)
    ey = clamp(error_q.Q["j"], -1, 1)
    ez = clamp(error_q.Q["k"], -1, 1)

    wx, wy, wz = gyro.getValues()
    Tx = clamp(Kp * ex - Kd * wx, -15, 15)
    Ty = clamp(Kp * ey - Kd * wy, -15, 15)
    Tz = clamp(Kp * ez - Kd * wz, -10, 10)

    FL = clamp(desired_thrust - Tx + Ty - Tz, -576, 576)
    FR = clamp(desired_thrust + Tx + Ty + Tz, -576, 576)
    RL = clamp(desired_thrust - Tx - Ty + Tz, -576, 576)
    RR = clamp(desired_thrust + Tx - Ty - Tz, -576, 576)

    perm = get_permutations([FL, FR, RL, RR])
    index = 23
    front_left_motor.setVelocity(perm[index][0])
    front_right_motor.setVelocity(-perm[index][1])
    rear_left_motor.setVelocity(-perm[index][2])
    rear_right_motor.setVelocity(perm[index][3])

    if robot.getTime() > temp:
        x, y, z = gps.getValues()
        current_time = robot.getTime() - start_time
    
        print(
            f"Pos: ({x:.2f}, {y:.2f}, {z:.2f}) | "
            f"Target: ({target_x:.2f}, {target_y:.2f}, {target_altitude:.2f}) | "
            f"WP: {index_for_socket}/{len(tempx)}"
        )
    
        # Position tracking error
        tracking_error = np.sqrt(
            (target_x - x) ** 2
            + (target_y - y) ** 2
            + (target_altitude - z) ** 2
        )
    
        # Send telemetry to the dashboard
        socket.emit("telemetry", {
            "drone_id": "mavic_1",
            "t": float(current_time),
        
            # Actual position
            "x": float(x),
            "y": float(y),
            "z": float(z),
        
            # Current target on the planned spline
            "target_x": float(target_x),
            "target_y": float(target_y),
            "target_z": float(target_altitude),
        
            # Tracking error
            "tracking_error": float(tracking_error),
        
            # Supply real values when these features are implemented
            "obstacle_clearance": None,
            "leader_id": None
        })
    
        error_thingy = 0.35
    
        if len(tempx) > 0 and index_for_socket < len(tempx):
            at_waypoint = (
                abs(x - target_x) < error_thingy
                and abs(y - target_y) < error_thingy
                and abs(z - target_altitude) < error_thingy
            )
    
            if at_waypoint:
                print("Reached waypoint:", index_for_socket)
    
                target_x = tempx[index_for_socket]
                target_y = tempy[index_for_socket]
                target_altitude = tempz[index_for_socket]
                index_for_socket += 1
                
                if index_for_socket >= len(tempx):
                    print("Spline completed.")
                    holding_position = True
    
                # if index_for_socket >= len(tempx):
                    # for point in POINTS:
                        # manager.deleteObject(point)
    
                    # POINTS.clear()
                    # tempx = []
                    # tempy = []
                    # tempz = []
    
        temp = robot.getTime() + 0.25
    pass