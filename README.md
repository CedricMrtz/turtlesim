# ros2_tutorial_pkg — ROS 2 Humble Tutorial

A beginner-friendly package that walks you through the two most important
ROS 2 concepts:

1. **Publish / Subscribe messaging** — the `talker` and `listener` nodes
2. **Driving a simulated robot** — the `turtle_square` and `turtle_pose_logger`
   nodes working with `turtlesim`

Three launch files let you bring up each demo with a single command.

---

## Table of Contents

- [Prerequisites & Build](#prerequisites--build)
- [Package Structure](#package-structure)
- [Concept: How ROS 2 Nodes Communicate](#concept-how-ros-2-nodes-communicate)
- [Nodes](#nodes)
  - [talker](#1-talker)
  - [listener](#2-listener)
  - [turtle\_square](#3-turtle_square)
  - [turtle\_pose\_logger](#4-turtle_pose_logger)
- [Launch Files](#launch-files)
  - [talker\_listener.launch.py](#1-talker_listenerlaunchpy)
  - [turtle\_square.launch.py](#2-turtle_squarelaunchpy)
  - [full\_demo.launch.py](#3-full_demolaunchpy)
- [Running the Demos](#running-the-demos)
- [Inspecting the System at Runtime](#inspecting-the-system-at-runtime)
- [Next Steps](#next-steps)

---

## Prerequisites & Build

```bash
# 1 — Source ROS 2 Humble
source /opt/ros/humble/setup.bash

# 2 — Install turtlesim if needed (ships with the desktop install)
sudo apt install ros-humble-turtlesim

# 3 — Copy this package into your workspace and build
cd ~/ros2_ws/src
cp -r /path/to/ros2_tutorial_pkg .

cd ~/ros2_ws
colcon build --packages-select ros2_tutorial_pkg

# 4 — Source the overlay so ROS 2 can find your package
source install/setup.bash
```

> **Tip:** Add `source ~/ros2_ws/install/setup.bash` to your `~/.bashrc` so
> you don't have to re-run it in every new terminal.

---

## Package Structure

```
ros2_tutorial_pkg/
│
├── ros2_tutorial_pkg/          # Python package (the actual node code)
│   ├── __init__.py
│   ├── talker.py               # Publisher node
│   ├── listener.py             # Subscriber node
│   ├── turtle_square.py        # TurtleSim controller
│   └── turtle_pose_logger.py   # TurtleSim pose reader
│
├── launch/                     # Launch files
│   ├── talker_listener.launch.py
│   ├── turtle_square.launch.py
│   └── full_demo.launch.py
│
├── resource/
│   └── ros2_tutorial_pkg       # Empty ament index marker (required)
│
├── package.xml                 # Package metadata & dependencies
├── setup.py                    # Python entry points
└── setup.cfg                   # Install paths for executables
```

---

## Concept: How ROS 2 Nodes Communicate

Before diving into the nodes, here is the mental model you need:

```
 ┌─────────────────────────────────────────────────────┐
 │                   ROS 2 DDS Bus                     │
 │                                                     │
 │   [talker]  ──publishes──►  /chatter  ──►  [listener] │
 │                                                     │
 │   [turtle_square]  ──►  /turtle1/cmd_vel  ──►  [turtlesim] │
 │   [turtlesim]      ──►  /turtle1/pose     ──►  [turtle_pose_logger] │
 └─────────────────────────────────────────────────────┘
```

- A **node** is a single executable process with one job.
- A **topic** is a named channel that carries a specific message type.
- **Publishers** send messages to a topic; **subscribers** receive them.
- Nodes never talk to each other directly — they only read from and write
  to topics. This decoupling is the core design principle of ROS.

---

## Nodes

### 1. `talker`

**File:** `ros2_tutorial_pkg/talker.py`

The simplest possible publisher. It counts up from zero and sends a
`std_msgs/msg/String` message every second (by default).

**What it publishes**

| Topic | Type | Description |
|---|---|---|
| `/chatter` | `std_msgs/msg/String` | `"Hello World: N"` where N increments each publish |

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `publish_rate` | `float` | `1.0` | How many messages per second to publish (Hz) |

**How it works**

The node creates a `Publisher` on `/chatter` and a `Timer` that fires at
`publish_rate` Hz. Each time the timer fires, `timer_callback` builds a
`String` message, publishes it, and increments the counter. Nothing else
happens — the node just waits for the next timer tick.

**Run it alone**

```bash
ros2 run ros2_tutorial_pkg talker

# Override the rate via the command line
ros2 run ros2_tutorial_pkg talker --ros-args -p publish_rate:=5.0
```

---

### 2. `listener`

**File:** `ros2_tutorial_pkg/listener.py`

The counterpart to the talker. It subscribes to `/chatter` and prints
every message it receives to the terminal.

**What it subscribes to**

| Topic | Type | Description |
|---|---|---|
| `/chatter` | `std_msgs/msg/String` | Messages published by the talker |

**Parameters:** none

**How it works**

The node creates a `Subscription` with a queue depth of 10. Whenever a
message arrives on `/chatter`, the ROS 2 executor calls
`listener_callback`, which logs the message data. The node has no timers
and no publishers — it is purely reactive.

> **Key insight:** The talker and listener are completely independent
> processes. They do not need to start at the same time. If you start the
> listener first, it will simply wait. If you stop the talker and restart
> it, the listener will seamlessly continue receiving messages.

**Run it alone**

```bash
ros2 run ros2_tutorial_pkg listener
```

---

### 3. `turtle_square`

**File:** `ros2_tutorial_pkg/turtle_square.py`

A controller node that drives `turtle1` (the default turtle in
`turtlesim`) in a continuous square. It demonstrates the most common
robot control pattern: publish velocity commands on a timer, read sensor
feedback from a subscription.

**What it publishes**

| Topic | Type | Description |
|---|---|---|
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | Forward and rotational velocity commands |

**What it subscribes to**

| Topic | Type | Description |
|---|---|---|
| `/turtle1/pose` | `turtlesim/msg/Pose` | Current position and heading of the turtle |

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `side_length` | `float` | `2.0` | Approximate side length of the square in turtlesim units |

**How it works**

The node runs a simple two-state machine at 20 Hz:

```
  ┌──────────────────────────────────────────────────┐
  │  State: DRIVE                                    │
  │  Publish: linear.x = 1.0 m/s                    │
  │  Duration: side_length / 1.0 seconds             │
  └──────────────┬───────────────────────────────────┘
                 │ elapsed >= drive_duration
                 ▼
  ┌──────────────────────────────────────────────────┐
  │  State: TURN                                     │
  │  Publish: angular.z = 0.9 rad/s                  │
  │  Duration: (π/2) / 0.9 ≈ 1.75 seconds (90°)     │
  └──────────────┬───────────────────────────────────┘
                 │ elapsed >= turn_duration
                 ▼
            back to DRIVE  (repeat forever)
```

After every four sides it logs `"Square #N complete!"`.

The pose subscription does not gate the state machine — it is available
for future extensions (e.g. stopping when a wall is close). This is a
deliberate teaching choice: open-loop timing is the easiest starting
point before introducing closed-loop feedback.

**Run it alone** (requires `turtlesim_node` to already be running)

```bash
# Terminal 1
ros2 run turtlesim turtlesim_node

# Terminal 2
ros2 run ros2_tutorial_pkg turtle_square
ros2 run ros2_tutorial_pkg turtle_square --ros-args -p side_length:=3.5
```

---

### 4. `turtle_pose_logger`

**File:** `ros2_tutorial_pkg/turtle_pose_logger.py`

A read-only observer node. It listens to `/turtle1/pose` and prints the
turtle's position and velocity at a human-readable rate. `turtlesim`
publishes pose at ~62 Hz, which is far too fast to read in a terminal,
so this node down-samples it.

**What it subscribes to**

| Topic | Type | Description |
|---|---|---|
| `/turtle1/pose` | `turtlesim/msg/Pose` | Current x, y, θ, linear & angular velocity |

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `log_rate` | `float` | `2.0` | How many times per second to print the pose (Hz) |

**How it works**

A subscription always stores the latest `Pose` message in
`self._latest_pose`. A separate timer fires at `log_rate` Hz and reads
that cached value to produce one log line. This decouples the incoming
data rate (62 Hz) from the display rate (2 Hz by default), a pattern
that is very common in ROS diagnostic nodes.

**Example output**

```
[turtle_pose_logger]: Pose → x=5.544  y=5.544  θ=0.000 rad  speed=0.000 m/s
[turtle_pose_logger]: Pose → x=6.544  y=5.544  θ=0.000 rad  speed=1.000 m/s
```

**Run it alone** (requires `turtlesim_node`)

```bash
ros2 run ros2_tutorial_pkg turtle_pose_logger
ros2 run ros2_tutorial_pkg turtle_pose_logger --ros-args -p log_rate:=1.0
```

---

## Launch Files

A launch file starts multiple nodes with a single command and can pass
parameters, remap topics, and set namespaces. All launch files in this
package live in the `launch/` directory and follow the
`*.launch.py` naming convention required by ROS 2.

### 1. `talker_listener.launch.py`

**Purpose:** Run the pub-sub demo — the "Hello World" of ROS 2.

**Nodes started**

| Node name | Executable | Notes |
|---|---|---|
| `talker` | `ros2_tutorial_pkg/talker` | Publishes to `/chatter` |
| `listener` | `ros2_tutorial_pkg/listener` | Subscribes to `/chatter` |

**Launch arguments**

| Argument | Default | Description |
|---|---|---|
| `publish_rate` | `1.0` | Passed to the talker's `publish_rate` parameter |

**Usage**

```bash
# Default (1 Hz)
ros2 launch ros2_tutorial_pkg talker_listener.launch.py

# Faster (5 Hz)
ros2 launch ros2_tutorial_pkg talker_listener.launch.py publish_rate:=5.0
```

**Expected terminal output**

```
[talker-1] [INFO]: Publishing: "Hello World: 0"
[listener-2] [INFO]: I heard: "Hello World: 0"
[talker-1] [INFO]: Publishing: "Hello World: 1"
[listener-2] [INFO]: I heard: "Hello World: 1"
```

---

### 2. `turtle_square.launch.py`

**Purpose:** Open a TurtleSim window and watch the turtle drive itself
around a square while the pose logger reports its position.

**Nodes started**

| Node name | Executable | Notes |
|---|---|---|
| `turtlesim` | `turtlesim/turtlesim_node` | Opens the simulation window |
| `turtle_square` | `ros2_tutorial_pkg/turtle_square` | Sends velocity commands |
| `turtle_pose_logger` | `ros2_tutorial_pkg/turtle_pose_logger` | Logs turtle position |

**Launch arguments**

| Argument | Default | Description |
|---|---|---|
| `side_length` | `2.0` | Forwarded to `turtle_square`'s `side_length` parameter |
| `log_rate` | `2.0` | Forwarded to `turtle_pose_logger`'s `log_rate` parameter |

**Usage**

```bash
# Default square
ros2 launch ros2_tutorial_pkg turtle_square.launch.py

# Bigger square, slower log
ros2 launch ros2_tutorial_pkg turtle_square.launch.py side_length:=3.0 log_rate:=1.0
```

**What to expect**

A blue window opens with a turtle at the centre. After a short delay the
turtle begins moving forward, turns 90° left, moves forward again, and
so on, tracing a square repeatedly. The terminal shows alternating output
from `turtle_square` (state transitions) and `turtle_pose_logger` (pose
snapshots).

---

### 3. `full_demo.launch.py`

**Purpose:** Run every node in the package simultaneously — useful for
demos and for seeing how multiple independent sub-systems coexist on the
same ROS 2 graph.

**Nodes started**

| Node name | Executable |
|---|---|
| `talker` | `ros2_tutorial_pkg/talker` |
| `listener` | `ros2_tutorial_pkg/listener` |
| `turtlesim` | `turtlesim/turtlesim_node` |
| `turtle_square` | `ros2_tutorial_pkg/turtle_square` |
| `turtle_pose_logger` | `ros2_tutorial_pkg/turtle_pose_logger` |

**Launch arguments**

| Argument | Default | Description |
|---|---|---|
| `publish_rate` | `1.0` | Talker publish rate (Hz) |
| `side_length` | `2.0` | Square side length (turtlesim units) |
| `log_rate` | `2.0` | Pose logger rate (Hz) |

**Usage**

```bash
# All defaults
ros2 launch ros2_tutorial_pkg full_demo.launch.py

# Custom values
ros2 launch ros2_tutorial_pkg full_demo.launch.py \
  publish_rate:=2.0 \
  side_length:=3.0 \
  log_rate:=1.0
```

> **Note:** The talker/listener and turtlesim demos are completely
> independent — they use different topics and do not interfere with each
> other. Running them together is purely for convenience.

---

## Running the Demos

### Option A — One launch command

```bash
# Pub-sub only
ros2 launch ros2_tutorial_pkg talker_listener.launch.py

# TurtleSim only
ros2 launch ros2_tutorial_pkg turtle_square.launch.py

# Everything
ros2 launch ros2_tutorial_pkg full_demo.launch.py
```

### Option B — Nodes one at a time (good for learning)

Open a separate terminal for each node. Remember to source ROS 2 in each one.

```bash
# Terminal 1 — turtlesim window
ros2 run turtlesim turtlesim_node

# Terminal 2 — drive the turtle
ros2 run ros2_tutorial_pkg turtle_square

# Terminal 3 — watch the pose
ros2 run ros2_tutorial_pkg turtle_pose_logger

# Terminal 4 — start the talker
ros2 run ros2_tutorial_pkg talker

# Terminal 5 — start the listener
ros2 run ros2_tutorial_pkg listener
```

---

## Inspecting the System at Runtime

While any demo is running, open a new terminal and try these commands:

```bash
# See all active nodes
ros2 node list

# See all active topics and their types
ros2 topic list -t

# Print every message on /chatter as it arrives
ros2 topic echo /chatter

# Print the current turtle pose (Ctrl-C to stop)
ros2 topic echo /turtle1/pose

# See publish rate of a topic
ros2 topic hz /chatter
ros2 topic hz /turtle1/cmd_vel

# Full info about a node (publishers, subscribers, parameters)
ros2 node info /talker
ros2 node info /turtle_square

# List parameters of a running node
ros2 param list /talker
ros2 param get /talker publish_rate

# Change a parameter at runtime
ros2 param set /talker publish_rate 3.0

# Visualise the full node/topic graph
ros2 run rqt_graph rqt_graph
```

---

## Next Steps

Once you are comfortable with this package, here are natural progressions:

- **Custom message types** — define your own `.msg` file in a separate
  `_interfaces` package and use it instead of `std_msgs/String`.
- **Services** — add a `TeleportAbsolute` service call to `turtle_square`
  so it resets the turtle to the centre before each square.
- **Parameters at runtime** — use `ros2 param set` to change
  `publish_rate` or `side_length` while the nodes are running and watch
  the behaviour change without restarting.
- **Closed-loop control** — replace the open-loop timer in `turtle_square`
  with feedback from the pose subscription to get a more accurate square.
- **Namespacing** — launch two turtles with different namespaces
  (`/turtle1` and `/turtle2`) and drive them independently.

---

## License

Apache-2.0
