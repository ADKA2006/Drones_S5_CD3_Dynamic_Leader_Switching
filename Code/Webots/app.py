from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from pathlib import Path
import sqlite3, json, time, random, colorsys, math
from datetime import datetime
import threading

# Dynamic leader-election state
LEADER_ID = None
LAST_LEADER_SWITCH = 0.0
LEADER_LOCK = threading.RLock()

LEADER_STALE_AFTER = 3.0       # Seconds without telemetry
LEADER_SWITCH_COOLDOWN = 5.0   # Minimum time between normal switches
LEADER_MIN_ADVANTAGE = 0.15    # Required normalized score advantage

# Latest election metrics, kept in memory for fast decisions.
DRONE_METRICS = {}

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "drone_dashboard.db"
PLOT_DIR = BASE_DIR / "static" / "generated_plots"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-for-your-project"
socket = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

PALETTE = [
    [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.4, 1.0],
    [1.0, 0.8, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 1.0],
    [1.0, 0.35, 0.0], [0.6, 0.0, 1.0], [1.0, 0.2, 0.5],
    [0.4, 1.0, 0.0], [0.5, 0.25, 0.0], [0.7, 0.7, 1.0],
]
# Stable SID->drone mapping for the current live connection; durable records use drone_id.
SID_TO_DRONE = {}


def db():
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS drones (
            drone_id TEXT PRIMARY KEY, label TEXT NOT NULL, color TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'disconnected', last_seen REAL,
            control_points TEXT NOT NULL DEFAULT '[]', degree INTEGER NOT NULL DEFAULT 3,
            created_at REAL NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT, drone_id TEXT NOT NULL,
            sim_time REAL, received_at REAL NOT NULL, payload TEXT NOT NULL)""")
        con.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_drone_time ON telemetry(drone_id, sim_time)")


def distinct_color(index):
    if index < len(PALETTE):
        return PALETTE[index][:]
    # Golden-ratio hue stepping avoids adjacent random hues being too similar.
    hue = (index * 0.618033988749895) % 1.0
    return list(colorsys.hsv_to_rgb(hue, 0.95, 1.0))


def get_drone(drone_id):
    with db() as con:
        row = con.execute("SELECT * FROM drones WHERE drone_id=?", (drone_id,)).fetchone()
        return dict(row) if row else None

def leader_score(drone_id):
    """Calculate a normalized fitness score for leader election."""
    metrics = DRONE_METRICS.get(drone_id, {})

    battery = metrics.get("battery_pct", 100.0)
    health = metrics.get("health_score", 1.0)
    link = metrics.get("link_quality", 1.0)

    try:
        battery = max(0.0, min(100.0, float(battery))) / 100.0
        health = max(0.0, min(1.0, float(health)))
        link = max(0.0, min(1.0, float(link)))
    except (TypeError, ValueError):
        return 0.0

    # Higher battery, health and link quality are better.
    return 0.50 * battery + 0.30 * health + 0.20 * link


def elect_leader(force=False):
    """
    Elect or replace the leader.

    Disconnected/stale drones cannot lead. A normal switch requires
    a meaningful score improvement and respects the cooldown.
    """
    global LEADER_ID, LAST_LEADER_SWITCH

    now = time.time()

    with LEADER_LOCK:
        with db() as con:
            rows = con.execute(
                "SELECT drone_id, status, last_seen FROM drones"
            ).fetchall()

        # A drone is eligible only while its connection and telemetry
        # are both fresh.
        connected_ids = set(SID_TO_DRONE.values())
        eligible = [
            row["drone_id"]
            for row in rows
            if row["drone_id"] in connected_ids
            and row["status"] == "connected"
            and row["last_seen"] is not None
            and now - row["last_seen"] <= LEADER_STALE_AFTER
        ]

        if not eligible:
            if LEADER_ID is not None:
                old_leader = LEADER_ID
                LEADER_ID = None
                LAST_LEADER_SWITCH = now

                socket.emit("leader_update", {
                    "leader_id": None,
                    "previous_leader_id": old_leader,
                    "reason": "no_eligible_drones",
                    "scores": {}
                })
            return

        scores = {did: leader_score(did) for did in eligible}

        # Deterministic tie-break: lexicographically smallest drone ID.
        best_id = min(eligible, key=lambda did: (-scores[did], did))

        # No leader, or the current leader is no longer eligible.
        if LEADER_ID not in eligible:
            previous = LEADER_ID
            LEADER_ID = best_id
            LAST_LEADER_SWITCH = now
            reason = "initial_election" if previous is None else "leader_unavailable"

        else:
            current_score = scores[LEADER_ID]
            best_score = scores[best_id]

            # Don't change leaders on tiny score fluctuations.
            if best_id == LEADER_ID:
                return

            if not force and now - LAST_LEADER_SWITCH < LEADER_SWITCH_COOLDOWN:
                return

            if not force and best_score < current_score + LEADER_MIN_ADVANTAGE:
                return

            previous = LEADER_ID
            LEADER_ID = best_id
            LAST_LEADER_SWITCH = now
            reason = "better_candidate"

        print(
            f"[LEADER] {previous} -> {LEADER_ID} | "
            f"reason={reason} | scores={scores}"
        )

        socket.emit("leader_update", {
            "leader_id": LEADER_ID,
            "previous_leader_id": previous,
            "reason": reason,
            "scores": scores,
            "timestamp": now
        })


def public_drone(row):
    d = dict(row)
    d["color"] = json.loads(d["color"])
    d["control_points"] = json.loads(d["control_points"])
    d["last_seen_text"] = datetime.fromtimestamp(d["last_seen"]).strftime("%H:%M:%S") if d.get("last_seen") else "Never"
    return d


def broadcast_drones():
    with db() as con:
        rows = con.execute("SELECT * FROM drones ORDER BY created_at").fetchall()
    socket.emit("drone_list", [public_drone(r) for r in rows])


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/drones")
def api_drones():
    with db() as con:
        rows = con.execute("SELECT * FROM drones ORDER BY created_at").fetchall()
    return jsonify([public_drone(r) for r in rows])


@app.route("/api/plots/<filename>")
def plot_file(filename):
    # Generated plots are static images; no arbitrary filesystem paths are accepted.
    if "/" in filename or "\\" in filename or not filename.endswith(".png"):
        return "Invalid plot name", 400
    return send_from_directory(PLOT_DIR, filename)


@socket.on("connect")
def on_connect(auth=None):
    print("Dashboard connected:", request.sid)
    emit("dashboard_ready", {"ok": True})


@socket.on("registerDrone")
def register_drone(data):
    """Drone should send a persistent ID, e.g. mavic_1, not only a Socket.IO SID."""
    data = data or {}
    drone_id = str(data.get("drone_id", "")).strip()
    if not drone_id or len(drone_id) > 80:
        emit("server_error", {"message": "registerDrone requires a stable drone_id (max 80 chars)."})
        return

    now = time.time()
    with db() as con:
        row = con.execute("SELECT * FROM drones WHERE drone_id=?", (drone_id,)).fetchone()
        if row:
            color = json.loads(row["color"])
            label = str(data.get("label") or row["label"])
            con.execute("UPDATE drones SET label=?, status='connected', last_seen=? WHERE drone_id=?", (label, now, drone_id))
        else:
            count = con.execute("SELECT COUNT(*) FROM drones").fetchone()[0]
            color = distinct_color(count)
            label = str(data.get("label") or drone_id)
            con.execute("INSERT INTO drones(drone_id,label,color,status,last_seen,control_points,degree,created_at) VALUES(?,?,?,?,?,?,?,?)",
                        (drone_id, label, json.dumps(color), "connected", now, "[]", 3, now))
        row = con.execute("SELECT * FROM drones WHERE drone_id=?", (drone_id,)).fetchone()
    SID_TO_DRONE[request.sid] = drone_id
    emit("drone_registered", {"drone_id": drone_id, "color": color,
                               "control_points": json.loads(row["control_points"]), "p": row["degree"]})
    broadcast_drones()
    elect_leader()
    # If a saved path exists, resend it after registration/reconnection.
    points = json.loads(row["control_points"])
    if points:
        emit("BSpline", {"CPts": points, "p": row["degree"], "colors": color})


@socket.on("disconnect")
def on_disconnect(reason=None):
    drone_id = SID_TO_DRONE.pop(request.sid, None)
    if drone_id:
        with db() as con:
            con.execute("UPDATE drones SET status='disconnected' WHERE drone_id=?", (drone_id,))
        print(f"Drone disconnected (record preserved): {drone_id}")
        broadcast_drones()        
        DRONE_METRICS.pop(drone_id, None)
        elect_leader()


@socket.on("sendData")
def send_data(data):
    """Backward-compatible registration + initial position event from the original controller."""
    data = data or {}
    drone_id = SID_TO_DRONE.get(request.sid) or data.get("drone_id")
    if not drone_id:
        # Temporary fallback so old controllers still show up. A stable ID is strongly recommended.
        drone_id = f"session_{request.sid[:12]}"
        register_drone({"drone_id": drone_id, "label": drone_id})
    payload = dict(data)
    payload.setdefault("t", data.get("time", 0.0))
    store_telemetry(str(drone_id), payload)
    # Only send a default path if none has been saved yet.
    drone = get_drone(str(drone_id))
    if drone and not json.loads(drone["control_points"]):
        try:
            x, y, z = (float(data.get(k, 0.0)) for k in ("x", "y", "z"))
            points = [[x, y, z], [0, 4, 2], [4, 4, 2], [4, 0, 2]]
            with db() as con:
                con.execute("UPDATE drones SET control_points=?, degree=3 WHERE drone_id=?", (json.dumps(points), str(drone_id)))
            socket.emit("BSpline", {"CPts": points, "p": 3, "colors": json.loads(drone["color"])}, to=request.sid)
        except (TypeError, ValueError):
            pass


@socket.on("telemetry")
def receive_telemetry(data):
    data = data or {}
    drone_id = SID_TO_DRONE.get(request.sid) or str(data.get("drone_id", "")).strip()
    if not drone_id:
        emit("server_error", {"message": "Send registerDrone with a stable drone_id before telemetry."})
        return
    if get_drone(drone_id) is None:
        register_drone({"drone_id": drone_id})
    store_telemetry(drone_id, data)
        # Cache the latest election metrics.
    DRONE_METRICS[drone_id] = {
        "battery_pct": data.get("battery_pct", 100.0),
        "health_score": data.get("health_score", 1.0),
        "link_quality": data.get("link_quality", 1.0),
    }

    # Re-evaluate the leader using the latest drone state.
    elect_leader()
    with db() as con:
        con.execute("UPDATE drones SET status='connected', last_seen=? WHERE drone_id=?", (time.time(), drone_id))
    # Lightweight live status; detailed histories stay in SQLite until a plot is requested.
    data["leader_id"] = LEADER_ID

    socket.emit("telemetry_update", {
        "drone_id": drone_id,
        "payload": data,
        "leader_id": LEADER_ID
    })


def store_telemetry(drone_id, payload):
    now = time.time()
    try:
        sim_time = float(payload.get("t", payload.get("time", 0.0)))
        if not math.isfinite(sim_time): sim_time = 0.0
    except (TypeError, ValueError):
        sim_time = 0.0
    with db() as con:
        con.execute("INSERT INTO telemetry(drone_id,sim_time,received_at,payload) VALUES(?,?,?,?)",
                    (drone_id, sim_time, now, json.dumps(payload, allow_nan=False, default=str)))
        con.execute("UPDATE drones SET status='connected', last_seen=? WHERE drone_id=?", (now, drone_id))


@socket.on("setControlPoints")
def set_control_points(data):
    """Dashboard -> drone. data: {drone_id, control_points:[[x,y,z],...], degree:3}."""
    data = data or {}
    drone_id = str(data.get("drone_id", ""))
    points = data.get("control_points")
    degree = int(data.get("degree", 3))
    if not drone_id or not isinstance(points, list) or len(points) < degree + 1:
        emit("server_error", {"message": "Provide a drone_id and at least degree+1 control points."})
        return
    try:
        cleaned = [[float(v) for v in point] for point in points]
        if any(len(point) != 3 for point in cleaned) or not all(math.isfinite(v) for p in cleaned for v in p):
            raise ValueError
    except (TypeError, ValueError):
        emit("server_error", {"message": "Each control point must contain three finite numbers: [x,y,z]."})
        return
    if degree < 1 or degree >= len(cleaned):
        emit("server_error", {"message": "Degree must be >=1 and less than the number of control points."})
        return
    with db() as con:
        con.execute("UPDATE drones SET control_points=?, degree=? WHERE drone_id=?",
                    (json.dumps(cleaned), degree, drone_id))
    target_sid = next((sid for sid, did in SID_TO_DRONE.items() if did == drone_id), None)
    if target_sid:
        socket.emit("BSpline", {"CPts": cleaned, "p": degree,
                                 "colors": json.loads(get_drone(drone_id)["color"])}, to=target_sid)
        emit("control_points_saved", {"drone_id": drone_id, "sent": True, "message": "Saved and sent to connected drone."})
    else:
        emit("control_points_saved", {"drone_id": drone_id, "sent": False,
                                       "message": "Saved. Drone is disconnected; path will be sent when it reconnects."})
    broadcast_drones()


@socket.on("deleteDrone")
def delete_drone(data):
    drone_id = str((data or {}).get("drone_id", ""))
    if not drone_id:
        return
    # Explicit user action only: delete both the persistent record and telemetry.
    with db() as con:
        con.execute("DELETE FROM telemetry WHERE drone_id=?", (drone_id,))
        con.execute("DELETE FROM drones WHERE drone_id=?", (drone_id,))
    for sid, did in list(SID_TO_DRONE.items()):
        if did == drone_id:
            SID_TO_DRONE.pop(sid, None)
    emit("drone_deleted", {"drone_id": drone_id})
    broadcast_drones()
    DRONE_METRICS.pop(drone_id, None)
    elect_leader(force=True)


PLOT_INFO = {
    "trajectory_3d": "Actual 3D trajectory",
    "coordinates_time": "Position coordinates vs time",
    "tracking_error": "Position tracking error vs time",
    "planned_actual_3d": "B-spline planned vs actual trajectory",
    "obstacle_clearance": "Minimum obstacle clearance vs time",
    "path_length": "Original vs replanned path length",
    "uav_trajectories": "UAV 1 and UAV 2 trajectories",
    "leader_identity": "Leader identity vs time",
}


def read_telemetry(drone_ids=None):
    with db() as con:
        if drone_ids:
            marks = ",".join("?" for _ in drone_ids)
            rows = con.execute(f"SELECT drone_id,sim_time,payload FROM telemetry WHERE drone_id IN ({marks}) ORDER BY id", drone_ids).fetchall()
        else:
            rows = con.execute("SELECT drone_id,sim_time,payload FROM telemetry ORDER BY id").fetchall()
    result = []
    for row in rows:
        try: payload = json.loads(row["payload"])
        except json.JSONDecodeError: continue
        payload["_drone_id"] = row["drone_id"]
        payload["_sim_time"] = row["sim_time"]
        result.append(payload)
    return result


def finite_number(payload, key):
    try:
        val = float(payload.get(key))
        return val if math.isfinite(val) else None
    except (TypeError, ValueError):
        return None


@socket.on("generatePlot")
def generate_plot(data):
    data = data or {}
    plot_type = data.get("plot_type")
    drone_ids = data.get("drone_ids") or None
    if plot_type not in PLOT_INFO:
        emit("plot_error", {"message": "Unknown plot type."})
        return
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    except ImportError:
        emit("plot_error", {"message": "Install matplotlib: pip install matplotlib"})
        return

    rows = read_telemetry(drone_ids)
    if not rows:
        emit("plot_error", {"message": "No telemetry has been stored yet."})
        return

    fig = plt.figure(figsize=(9, 6))
    ax = None
    try:
        if plot_type in ("trajectory_3d", "planned_actual_3d", "uav_trajectories"):
            ax = fig.add_subplot(111, projection="3d")
        if plot_type == "trajectory_3d":
            grouped = {}
            for r in rows:
                x,y,z = (finite_number(r,k) for k in ("x","y","z"))
                if None not in (x,y,z): grouped.setdefault(r["_drone_id"], [[],[],[]]); grouped[r["_drone_id"]][0].append(x); grouped[r["_drone_id"]][1].append(y); grouped[r["_drone_id"]][2].append(z)
            for did,(xs,ys,zs) in grouped.items(): ax.plot(xs,ys,zs,label=did)
            ax.set(xlabel="X position (m)", ylabel="Y position (m)", zlabel="Z position (m)", title=PLOT_INFO[plot_type]); ax.legend()
        elif plot_type == "coordinates_time":
            for key,label in (("x","X position (m)"),("y","Y position (m)"),("z","Z position (m)")):
                for did in sorted({r["_drone_id"] for r in rows}):
                    pts=[(finite_number(r,"t") if finite_number(r,"t") is not None else r["_sim_time"],finite_number(r,key)) for r in rows if r["_drone_id"]==did]
                    pts=[p for p in pts if p[1] is not None]
                    if pts: ax = fig.add_subplot(3,1, {"x":1,"y":2,"z":3}[key]) if False else None
                # Three separate axes for X/Y/Z
            fig.clear()
            for i,(key,label) in enumerate((("x","X position (m)"),("y","Y position (m)"),("z","Z position (m)")),1):
                a=fig.add_subplot(3,1,i)
                for did in sorted({r["_drone_id"] for r in rows}):
                    pts=[(finite_number(r,"t") if finite_number(r,"t") is not None else r["_sim_time"],finite_number(r,key)) for r in rows if r["_drone_id"]==did]
                    pts=[p for p in pts if p[1] is not None]
                    if pts: a.plot([p[0] for p in pts],[p[1] for p in pts],label=did)
                a.set_ylabel(label); a.grid(True,alpha=.3)
                if i==1: a.legend(loc="best")
            fig.axes[-1].set_xlabel("Time (s)"); fig.suptitle(PLOT_INFO[plot_type]); fig.tight_layout()
        elif plot_type == "tracking_error":
            grouped={}
            for r in rows:
                t=finite_number(r,"t"); t=r["_sim_time"] if t is None else t
                e=finite_number(r,"tracking_error")
                if e is None:
                    actual=[finite_number(r,k) for k in ("x","y","z")]
                    desired=[finite_number(r,k) for k in ("target_x","target_y","target_z")]
                    if all(v is not None for v in actual+desired): e=math.sqrt(sum((actual[i]-desired[i])**2 for i in range(3)))
                if e is not None: grouped.setdefault(r["_drone_id"],[[],[]]); grouped[r["_drone_id"]][0].append(t); grouped[r["_drone_id"]][1].append(e)
            for did,(ts,es) in grouped.items(): ax.plot(ts,es,label=did)
            ax.set(xlabel="Time (s)",ylabel="Position tracking error (m)",title=PLOT_INFO[plot_type]); ax.grid(True,alpha=.3); ax.legend()
            if not grouped: raise ValueError("Send tracking_error or target_x, target_y, target_z in telemetry to plot tracking error.")
        elif plot_type == "planned_actual_3d":
            did = (drone_ids or [rows[-1]["_drone_id"]])[0]
            drone=get_drone(did)
            if drone:
                cp=json.loads(drone["control_points"])
                if cp:
                    ax.plot([p[0] for p in cp],[p[1] for p in cp],[p[2] for p in cp],"--o",label="Saved control polygon")
            for drone_id in sorted({r["_drone_id"] for r in rows}):
                if drone_ids and drone_id not in drone_ids: continue
                pts=[(finite_number(r,"x"),finite_number(r,"y"),finite_number(r,"z")) for r in rows if r["_drone_id"]==drone_id]
                pts=[p for p in pts if None not in p]
                if pts: ax.plot([p[0] for p in pts],[p[1] for p in pts],[p[2] for p in pts],label=f"{drone_id} actual")
            ax.set(xlabel="X position (m)",ylabel="Y position (m)",zlabel="Z position (m)",title=PLOT_INFO[plot_type]); ax.legend()
            # Control points are a control polygon, not an evaluated B-spline curve.
        elif plot_type == "obstacle_clearance":
            grouped={}
            for r in rows:
                t=finite_number(r,"t"); t=r["_sim_time"] if t is None else t
                v=finite_number(r,"obstacle_clearance")
                if v is not None: grouped.setdefault(r["_drone_id"],[[],[]]); grouped[r["_drone_id"]][0].append(t); grouped[r["_drone_id"]][1].append(v)
            for did,(ts,vs) in grouped.items(): ax.plot(ts,vs,label=did)
            ax.set(xlabel="Time (s)",ylabel="Minimum obstacle clearance (m)",title=PLOT_INFO[plot_type]); ax.grid(True,alpha=.3); ax.legend()
            if not grouped: raise ValueError("Send obstacle_clearance (meters) with telemetry to plot obstacle clearance.")
        elif plot_type == "path_length":
            # One event/record per path version, with path_type and path_length fields.
            values={"Original":[],"Replanned":[]}
            for r in rows:
                kind=str(r.get("path_type", "" )).title(); length=finite_number(r,"path_length")
                if kind in values and length is not None: values[kind].append(length)
            labels=[]; heights=[]
            for kind in values:
                if values[kind]: labels.append(kind); heights.append(values[kind][-1])
            if not heights: raise ValueError("Send path_type='Original'/'Replanned' and path_length in telemetry when each path is created.")
            ax.bar(labels,heights); ax.set(ylabel="Path length (m)",title=PLOT_INFO[plot_type]); ax.grid(True,axis="y",alpha=.3)
        elif plot_type == "uav_trajectories":
            for did in sorted({r["_drone_id"] for r in rows}):
                pts=[(finite_number(r,"x"),finite_number(r,"y"),finite_number(r,"z")) for r in rows if r["_drone_id"]==did]
                pts=[p for p in pts if None not in p]
                if pts: ax.plot([p[0] for p in pts],[p[1] for p in pts],[p[2] for p in pts],label=did)
            ax.set(xlabel="X position (m)",ylabel="Y position (m)",zlabel="Z position (m)",title=PLOT_INFO[plot_type]); ax.legend()
        elif plot_type == "leader_identity":
            leaders=[]
            for r in rows:
                t=finite_number(r,"t"); t=r["_sim_time"] if t is None else t
                leader=r.get("leader_id")
                if leader is not None: leaders.append((t,str(leader)))
            if not leaders: raise ValueError("Send leader_id='UAV 1' or 'UAV 2' in telemetry to plot leader identity.")
            unique={v:i for i,v in enumerate(sorted({v for _,v in leaders}))}
            ax.step([t for t,_ in leaders],[unique[v] for _,v in leaders],where="post")
            ax.set_yticks(list(unique.values()),list(unique.keys())); ax.set(xlabel="Time (s)",ylabel="Leader identity",title=PLOT_INFO[plot_type]); ax.grid(True,alpha=.3)
        fig.tight_layout()
        stamp=int(time.time()*1000)
        filename=f"{plot_type}_{stamp}.png"
        fig.savefig(PLOT_DIR/filename,dpi=140,bbox_inches="tight")
        emit("plot_ready", {"plot_type": plot_type, "title": PLOT_INFO[plot_type],
                            "url": f"/api/plots/{filename}", "filename": filename})
    except Exception as exc:
        emit("plot_error", {"message": str(exc)})
    finally:
        plt.close(fig)


init_db()

if __name__ == "__main__":
    # Install: pip install flask flask-socketio matplotlib
    socket.run(app, host="0.0.0.0", port=5000, debug=False)
