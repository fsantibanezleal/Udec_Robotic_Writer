"""Interactive Dash application for the Robotic Writer simulation.

Provides a web-based GUI with:
    - 3D visualization of the robot arm, block circle, and writing line
    - Real-time simulation playback with animation controls
    - Forward/inverse kinematics explorer
    - Configuration panel for block circle and writing parameters
    - Action log viewer
"""

from __future__ import annotations

import math
import json

import dash
from dash import dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np

from ..core.kinematics import (
    ForwardKinematics,
    InverseKinematics,
    JointState,
    JOINT_LIMITS_DEG,
    SCORBOT_DH_TABLE,
)
from ..core.robot import ScorbotIII
from ..core.writer import RoboticWriter, BlockCircle, WritingLine


# ── Dash app ───────────────────────────────────────────────────────────────

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="Robotic Writer Simulator",
    suppress_callback_exceptions=True,
)

fk = ForwardKinematics()
ik = InverseKinematics()


# ── Helper functions ───────────────────────────────────────────────────────

def create_robot_traces(joint_state: JointState, name_prefix: str = "") -> list:
    """Generate Plotly traces for the robot arm visualization."""
    positions = fk.joint_positions(joint_state)
    x, y, z = positions[:, 0], positions[:, 1], positions[:, 2]

    # Robot arm links
    arm_trace = go.Scatter3d(
        x=x, y=y, z=z,
        mode="lines+markers",
        line=dict(color="#00d4ff", width=8),
        marker=dict(size=[8, 6, 6, 5, 5, 4], color="#00d4ff"),
        name=f"{name_prefix}Robot Arm",
        hovertemplate="X: %{x:.1f}<br>Y: %{y:.1f}<br>Z: %{z:.1f}<extra>Joint</extra>",
    )

    # End-effector marker
    ee = positions[-1]
    ee_trace = go.Scatter3d(
        x=[ee[0]], y=[ee[1]], z=[ee[2]],
        mode="markers",
        marker=dict(size=10, color="#ff4444", symbol="diamond"),
        name=f"{name_prefix}End Effector",
        hovertemplate=f"EE: ({ee[0]:.1f}, {ee[1]:.1f}, {ee[2]:.1f})<extra></extra>",
    )

    return [arm_trace, ee_trace]


def create_block_circle_traces(block_circle: BlockCircle) -> list:
    """Generate traces for the letter blocks on the circular arc."""
    positions = block_circle.get_arc_points()
    colors = ["#44ff44" if b.is_available else "#ff4444" for b in block_circle.blocks]
    labels = [b.character for b in block_circle.blocks]

    blocks_trace = go.Scatter3d(
        x=positions[:, 0], y=positions[:, 1], z=positions[:, 2],
        mode="markers+text",
        marker=dict(size=6, color=colors, opacity=0.9),
        text=labels,
        textposition="top center",
        textfont=dict(size=10, color="white"),
        name="Letter Blocks",
        hovertemplate="%{text}<br>X: %{x:.1f}<br>Y: %{y:.1f}<extra></extra>",
    )

    # Arc outline
    angles = np.linspace(-math.pi, math.pi, 200)
    arc_x = block_circle.radius_mm * np.cos(angles)
    arc_y = block_circle.radius_mm * np.sin(angles)
    arc_z = np.full_like(angles, block_circle.block_height_mm)

    arc_trace = go.Scatter3d(
        x=arc_x, y=arc_y, z=arc_z,
        mode="lines",
        line=dict(color="rgba(100,100,100,0.3)", width=2, dash="dot"),
        name="Block Circle",
        showlegend=False,
    )

    return [blocks_trace, arc_trace]


def create_writing_line_traces(writing_line: WritingLine, num_slots: int = 10) -> list:
    """Generate traces for the writing line slots."""
    positions = np.array([writing_line.slot_position(i) for i in range(num_slots)])

    slots_trace = go.Scatter3d(
        x=positions[:, 0], y=positions[:, 1], z=positions[:, 2],
        mode="markers",
        marker=dict(size=5, color="rgba(255,255,100,0.5)", symbol="square"),
        name="Writing Slots",
        hovertemplate="Slot %{pointNumber}<br>X: %{x:.1f}<br>Y: %{y:.1f}<extra></extra>",
    )

    # Writing line
    line_start = writing_line.start_xyz
    line_end = writing_line.slot_position(num_slots - 1)
    line_trace = go.Scatter3d(
        x=[line_start[0], line_end[0]],
        y=[line_start[1], line_end[1]],
        z=[line_start[2], line_end[2]],
        mode="lines",
        line=dict(color="rgba(255,255,100,0.3)", width=3),
        name="Writing Line",
        showlegend=False,
    )

    return [slots_trace, line_trace]


def create_trajectory_trace(trajectory_positions: list) -> go.Scatter3d:
    """Create a trace for the end-effector trajectory path."""
    if not trajectory_positions:
        return go.Scatter3d(x=[], y=[], z=[], mode="lines", name="Trajectory")

    pos = np.array(trajectory_positions)
    return go.Scatter3d(
        x=pos[:, 0], y=pos[:, 1], z=pos[:, 2],
        mode="lines",
        line=dict(color="rgba(255,100,255,0.5)", width=2),
        name="Trajectory",
    )


def create_base_figure() -> go.Figure:
    """Create the 3D figure with layout settings."""
    fig = go.Figure()
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X (mm)", range=[-500, 500], backgroundcolor="rgba(0,0,0,0)"),
            yaxis=dict(title="Y (mm)", range=[-500, 500], backgroundcolor="rgba(0,0,0,0)"),
            zaxis=dict(title="Z (mm)", range=[0, 600], backgroundcolor="rgba(0,0,0,0)"),
            aspectmode="cube",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.0)),
        ),
        paper_bgcolor="rgba(30,30,30,1)",
        plot_bgcolor="rgba(30,30,30,1)",
        font=dict(color="white"),
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(x=0, y=1, bgcolor="rgba(0,0,0,0.5)"),
        title=dict(text="Robotic Writer 3D Simulation", x=0.5),
    )

    # Ground plane
    ground_size = 500
    fig.add_trace(go.Mesh3d(
        x=[-ground_size, ground_size, ground_size, -ground_size],
        y=[-ground_size, -ground_size, ground_size, ground_size],
        z=[0, 0, 0, 0],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color="rgba(50,50,50,0.3)",
        name="Ground",
        showlegend=False,
    ))

    return fig


# ── Layout ─────────────────────────────────────────────────────────────────

def make_slider(id_str, label, min_val, max_val, value, step=1.0):
    """Create a labeled slider component."""
    return dbc.Row([
        dbc.Col(html.Label(label, className="text-light small"), width=3),
        dbc.Col(dcc.Slider(
            id=id_str, min=min_val, max=max_val, value=value, step=step,
            marks=None, tooltip={"placement": "bottom", "always_visible": True},
        ), width=9),
    ], className="mb-2")


sidebar = dbc.Card([
    dbc.CardHeader(html.H5("Control Panel", className="mb-0")),
    dbc.CardBody([
        # Tab selector
        dbc.Tabs(id="control-tabs", active_tab="tab-writer", children=[
            # Writer Tab
            dbc.Tab(label="Writer", tab_id="tab-writer", children=[
                html.Div([
                    html.Label("Text to Write:", className="text-light mt-3"),
                    dbc.Input(id="input-text", type="text", value="HELLO",
                              placeholder="Enter text...", maxLength=20, className="mb-2"),
                    html.Label("Block Circle Radius (mm):", className="text-light small"),
                    dcc.Slider(id="slider-radius", min=200, max=400, value=280, step=10,
                               marks=None, tooltip={"placement": "bottom", "always_visible": True}),
                    html.Label("Angular Separation (deg):", className="text-light small"),
                    dcc.Slider(id="slider-angle-sep", min=3, max=20, value=8, step=0.5,
                               marks=None, tooltip={"placement": "bottom", "always_visible": True}),
                    html.Label("Block Spacing (mm):", className="text-light small"),
                    dcc.Slider(id="slider-spacing", min=15, max=40, value=25, step=1,
                               marks=None, tooltip={"placement": "bottom", "always_visible": True}),
                    dbc.Button("Run Simulation", id="btn-simulate", color="primary",
                               className="w-100 mt-3", n_clicks=0),
                    dbc.Button("Reset", id="btn-reset", color="secondary",
                               className="w-100 mt-2", n_clicks=0),
                ], className="p-2"),
            ]),
            # Kinematics Tab
            dbc.Tab(label="Kinematics", tab_id="tab-kinematics", children=[
                html.Div([
                    html.H6("Joint Angles (degrees)", className="text-light mt-3"),
                    make_slider("slider-j1", "Base (θ₁)", -126.5, 126.5, 0, 0.5),
                    make_slider("slider-j2", "Shoulder (θ₂)", -120, 63, 0, 0.5),
                    make_slider("slider-j3", "Elbow (θ₃)", -90, 90, 0, 0.5),
                    make_slider("slider-j4", "Pitch (θ₄)", -250, 40, 0, 0.5),
                    make_slider("slider-j5", "Roll (θ₅)", -180, 180, 0, 0.5),
                    html.Hr(),
                    html.Div(id="fk-result", className="text-info small"),
                ], className="p-2"),
            ]),
        ]),
    ]),
], className="h-100", style={"backgroundColor": "rgba(40,40,40,1)"})


main_content = html.Div([
    # 3D visualization
    dcc.Graph(id="graph-3d", style={"height": "60vh"}, config={"displayModeBar": True}),

    # Bottom panel: action log and animation
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Animation"),
                dbc.CardBody([
                    dcc.Slider(id="slider-frame", min=0, max=100, value=0, step=1,
                               marks=None, tooltip={"placement": "bottom", "always_visible": True}),
                    dbc.Row([
                        dbc.Col(dbc.Button("◀◀", id="btn-start", size="sm", color="info", className="w-100"), width=2),
                        dbc.Col(dbc.Button("◀", id="btn-prev", size="sm", color="info", className="w-100"), width=2),
                        dbc.Col(dbc.Button("▶ Play", id="btn-play", size="sm", color="success", className="w-100"), width=4),
                        dbc.Col(dbc.Button("▶", id="btn-next", size="sm", color="info", className="w-100"), width=2),
                        dbc.Col(dbc.Button("▶▶", id="btn-end", size="sm", color="info", className="w-100"), width=2),
                    ], className="mt-2"),
                    dcc.Interval(id="interval-play", interval=100, disabled=True),
                ]),
            ], style={"backgroundColor": "rgba(40,40,40,1)"}),
        ], md=5),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Action Log"),
                dbc.CardBody([
                    html.Div(
                        id="action-log",
                        style={"height": "150px", "overflowY": "auto", "fontSize": "0.8rem"},
                    ),
                ]),
            ], style={"backgroundColor": "rgba(40,40,40,1)"}),
        ], md=7),
    ], className="mt-2"),
])


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Robotic Writer Simulator", className="text-center text-primary my-3")),
    ]),
    dbc.Row([
        dbc.Col(sidebar, md=3),
        dbc.Col(main_content, md=9),
    ]),
    # Hidden stores for simulation data
    dcc.Store(id="store-sim-data", data=None),
    dcc.Store(id="store-playing", data=False),
], fluid=True, style={"backgroundColor": "rgba(20,20,20,1)", "minHeight": "100vh"})


# ── Callbacks ──────────────────────────────────────────────────────────────

@callback(
    Output("store-sim-data", "data"),
    Output("action-log", "children"),
    Input("btn-simulate", "n_clicks"),
    State("input-text", "value"),
    State("slider-radius", "value"),
    State("slider-angle-sep", "value"),
    State("slider-spacing", "value"),
    prevent_initial_call=True,
)
def run_simulation(n_clicks, text, radius, angle_sep, spacing):
    """Execute the writer simulation and store results."""
    if not text:
        return no_update, no_update

    block_circle = BlockCircle(
        radius_mm=radius,
        block_height_mm=50.0,
        min_angular_separation_deg=angle_sep,
    )
    writing_line = WritingLine(
        start_xyz=np.array([200.0, -120.0, 50.0]),
        spacing_mm=spacing,
    )
    robot = ScorbotIII(interpolation_steps=30)
    writer = RoboticWriter(robot=robot, block_circle=block_circle, writing_line=writing_line)

    action_log = writer.write_text(text.upper())
    sim_data = writer.get_simulation_data()

    # Build action log display
    log_items = []
    for i, action in enumerate(action_log):
        color = {
            "pick": "text-success", "place": "text-warning",
            "start": "text-primary", "done": "text-primary",
            "space": "text-muted", "skip": "text-danger",
        }.get(action["action"], "text-light")
        log_items.append(html.Div(
            f"[{i}] {action['description']}",
            className=color,
        ))

    return sim_data, log_items


@callback(
    Output("graph-3d", "figure"),
    Input("store-sim-data", "data"),
    Input("slider-frame", "value"),
    Input("slider-j1", "value"),
    Input("slider-j2", "value"),
    Input("slider-j3", "value"),
    Input("slider-j4", "value"),
    Input("slider-j5", "value"),
    Input("control-tabs", "active_tab"),
    Input("btn-reset", "n_clicks"),
    State("slider-radius", "value"),
    State("slider-angle-sep", "value"),
    State("slider-spacing", "value"),
)
def update_3d_view(sim_data, frame, j1, j2, j3, j4, j5, active_tab, reset_clicks,
                   radius, angle_sep, spacing):
    """Update the 3D visualization based on current state."""
    fig = create_base_figure()

    if active_tab == "tab-kinematics":
        # Manual kinematics exploration
        joint_state = JointState.from_degrees([j1, j2, j3, j4, j5])
        traces = create_robot_traces(joint_state)
        for t in traces:
            fig.add_trace(t)
        # Show default block circle for reference
        bc = BlockCircle(radius_mm=radius, min_angular_separation_deg=angle_sep)
        for t in create_block_circle_traces(bc):
            fig.add_trace(t)

    elif sim_data is not None:
        # Simulation playback
        traj = sim_data["trajectory"]
        positions = traj.get("positions", [])
        joint_angles = traj.get("joint_angles_deg", [])

        if positions and joint_angles:
            # Clamp frame index
            max_frame = len(positions) - 1
            frame_idx = min(max(0, frame), max_frame)

            # Robot at current frame
            angles = joint_angles[frame_idx]
            joint_state = JointState.from_degrees(angles)
            for t in create_robot_traces(joint_state):
                fig.add_trace(t)

            # Trajectory path up to current frame
            traj_trace = create_trajectory_trace(positions[:frame_idx + 1])
            fig.add_trace(traj_trace)

        # Block circle (with availability status)
        bc_data = sim_data.get("block_circle", {})
        bc_positions = bc_data.get("positions", [])
        bc_chars = bc_data.get("characters", [])
        bc_available = bc_data.get("available", [])
        if bc_positions:
            pos = np.array(bc_positions)
            colors = ["#44ff44" if a else "#ff4444" for a in bc_available]
            fig.add_trace(go.Scatter3d(
                x=pos[:, 0], y=pos[:, 1], z=pos[:, 2],
                mode="markers+text",
                marker=dict(size=6, color=colors, opacity=0.9),
                text=bc_chars,
                textposition="top center",
                textfont=dict(size=10, color="white"),
                name="Letter Blocks",
            ))

        # Writing line
        wl_data = sim_data.get("writing_line", {})
        if wl_data:
            wl = WritingLine(
                start_xyz=np.array(wl_data["start"]),
                direction=np.array(wl_data["direction"]),
                spacing_mm=wl_data["spacing_mm"],
            )
            for t in create_writing_line_traces(wl):
                fig.add_trace(t)
    else:
        # Default view: robot at home + empty block circle
        joint_state = JointState()
        for t in create_robot_traces(joint_state):
            fig.add_trace(t)
        bc = BlockCircle(radius_mm=radius, min_angular_separation_deg=angle_sep)
        for t in create_block_circle_traces(bc):
            fig.add_trace(t)
        wl = WritingLine(spacing_mm=spacing)
        for t in create_writing_line_traces(wl):
            fig.add_trace(t)

    return fig


@callback(
    Output("slider-frame", "max"),
    Input("store-sim-data", "data"),
)
def update_frame_slider_max(sim_data):
    """Set frame slider range based on simulation data."""
    if sim_data is None:
        return 100
    positions = sim_data.get("trajectory", {}).get("positions", [])
    return max(len(positions) - 1, 1)


@callback(
    Output("fk-result", "children"),
    Input("slider-j1", "value"),
    Input("slider-j2", "value"),
    Input("slider-j3", "value"),
    Input("slider-j4", "value"),
    Input("slider-j5", "value"),
)
def update_fk_display(j1, j2, j3, j4, j5):
    """Show forward kinematics result for manual joint angles."""
    joint_state = JointState.from_degrees([j1, j2, j3, j4, j5])
    result = fk.compute(joint_state)
    pos = result["position"]
    return html.Div([
        html.P(f"End Effector Position:", className="mb-1 fw-bold"),
        html.P(f"X = {pos[0]:.2f} mm", className="mb-0"),
        html.P(f"Y = {pos[1]:.2f} mm", className="mb-0"),
        html.P(f"Z = {pos[2]:.2f} mm", className="mb-0"),
    ])


@callback(
    Output("interval-play", "disabled"),
    Output("store-playing", "data"),
    Output("btn-play", "children"),
    Input("btn-play", "n_clicks"),
    State("store-playing", "data"),
    prevent_initial_call=True,
)
def toggle_play(n_clicks, playing):
    """Toggle animation play/pause."""
    new_playing = not playing
    return not new_playing, new_playing, "⏸ Pause" if new_playing else "▶ Play"


@callback(
    Output("slider-frame", "value"),
    Input("interval-play", "n_intervals"),
    Input("btn-start", "n_clicks"),
    Input("btn-end", "n_clicks"),
    Input("btn-prev", "n_clicks"),
    Input("btn-next", "n_clicks"),
    State("slider-frame", "value"),
    State("slider-frame", "max"),
    prevent_initial_call=True,
)
def update_frame(n_intervals, start_clicks, end_clicks, prev_clicks, next_clicks,
                 current_frame, max_frame):
    """Advance/control animation frame."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update

    trigger = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger == "interval-play":
        new_frame = current_frame + 1
        return new_frame if new_frame <= max_frame else 0
    elif trigger == "btn-start":
        return 0
    elif trigger == "btn-end":
        return max_frame
    elif trigger == "btn-prev":
        return max(0, current_frame - 1)
    elif trigger == "btn-next":
        return min(max_frame, current_frame + 1)

    return no_update


# ── Server ─────────────────────────────────────────────────────────────────

server = app.server  # For ASGI/WSGI deployment

if __name__ == "__main__":
    app.run(debug=True, port=8050)
