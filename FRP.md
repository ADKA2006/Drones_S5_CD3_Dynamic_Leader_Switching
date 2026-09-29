### Drone Navigation

* [x] Development of basic manual UAV control using keyboard inputs.

* [x] Implementation of basic UAV movements, including forward, backward, left, right, and altitude control.

* [x] Development of autonomous UAV movement between specified start and end points.

### Obstacle Fed B-Spline Avoidance

* [x] Generation of a B-spline trajectory between the specified points for smooth autonomous navigation.

* [ ] Implementation of obstacle avoidance in a simulation environment {Webots, Pybullet, Mujoco} .

* [ ] Avoidance of obstacles along the planned trajectory and identification of required path changes.

* [x] Generation of a new B-spline trajectory for navigation around fed in obstacles.
      
* [x] Server feeds end points and obstacle info to drone and drone computes the trajectory in edge and moves accordingly

### Dynamic Leader System

* [ ] Extension of the single-UAV navigation system to two-UAV cooperative navigation.

* [ ] Use of four predefined points as the mission path for evaluating the Dynamic Leader Switching approach.

* [ ] Integration of Dynamic Leader Switching to allow either UAV to assume the leader role and continue the mission along the planned trajectory.
