"""Interactive Dash application for the Robotic Writer simulation.

Provides a web-based GUI with:
    - 3D visualization of the robot arm, block circle, and writing line
    - Real-time simulation playback with animation controls
    - Tutorial mode: user types, robot writes
    - Ouija mode: ask a question, spirits respond
    - Forward/inverse kinematics explorer
"""

from __future__ import annotations

import math

import dash
from dash import dcc, html, Input, Output, State, callback, no_update, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np

from ..core.kinematics import ForwardKinematics, InverseKinematics, JointState
from ..core.robot import ScorbotIII
from ..core.writer import RoboticWriter, BlockCircle, WritingLine
from ..core.modes import generate_ouija_response


# ── Dash app ───────────────────────────────────────────────────────────────

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="Robotic Writer Simulator",
    suppress_callback_exceptions=True,
)

fk_engine = ForwardKinematics()


# ── Helper functions ───────────────────────────────────────────────────────

def create_robot_traces(joint_state: JointState) -> list:
    """Generate Plotly traces for the robot arm."""
    positions = fk_engine.joint_positions(joint_state)
    x, y, z = positions[:, 0], positions[:, 1], positions[:, 2]

    arm_trace = go.Scatter3d(
        x=x, y=y, z=z,
        mode="lines+markers",
        line=dict(color="#00d4ff", width=8),
        marker=dict(size=[8, 6, 6, 5, 5, 4], color="#00d4ff"),
        name="Robot Arm",
        hovertemplate="X:%{x:.1f} Y:%{y:.1f} Z:%{z:.1f}<extra>Joint</extra>",
    )

    ee = positions[-1]
    ee_trace = go.Scatter3d(
        x=[ee[0]], y=[ee[1]], z=[ee[2]],
        mode="markers",
        marker=dict(size=10, color="#ff4444", symbol="diamond"),
        name="End Effector",
        hovertemplate=f"EE: ({ee[0]:.1f}, {ee[1]:.1f}, {ee[2]:.1f})<extra></extra>",
    )

    return [arm_trace, ee_trace]


def create_block_circle_traces(
    positions: np.ndarray,
    characters: list[str],
    available: list[bool],
) -> list:
    """Generate traces for letter blocks.

    Available blocks are green, used blocks are blue (not red).
    """
    colors = ["#44ff44" if a else "#448AFF" for a in available]

    blocks_trace = go.Scatter3d(
        x=positions[:, 0], y=positions[:, 1], z=positions[:, 2],
        mode="markers+text",
        marker=dict(size=7, color=colors, opacity=0.9),
        text=characters,
        textposition="top center",
        textfont=dict(size=10, color="white"),
        name="Letter Blocks",
        hovertemplate="%{text}<br>X:%{x:.1f} Y:%{y:.1f}<extra></extra>",
    )

    # Circle outline
    if len(positions) > 0:
        r = np.sqrt(positions[0, 0] ** 2 + positions[0, 1] ** 2)
        z_h = positions[0, 2]
        angles = np.linspace(-math.pi, math.pi, 200)
        arc_trace = go.Scatter3d(
            x=r * np.cos(angles), y=r * np.sin(angles),
            z=np.full(200, z_h),
            mode="lines",
            line=dict(color="rgba(100,100,100,0.3)", width=2, dash="dot"),
            name="Block Circle", showlegend=False,
        )
        return [blocks_trace, arc_trace]

    return [blocks_trace]


def create_writing_line_traces(writing_line: WritingLine, num_slots: int = 15) -> list:
    """Generate traces for the writing arc slots."""
    positions = writing_line.get_slot_positions(num_slots)

    slots_trace = go.Scatter3d(
        x=positions[:, 0], y=positions[:, 1], z=positions[:, 2],
        mode="markers",
        marker=dict(size=5, color="rgba(255,255,100,0.5)", symbol="square"),
        name="Writing Slots",
        hovertemplate="Slot %{pointNumber}<br>X:%{x:.1f} Y:%{y:.1f}<extra></extra>",
    )

    arc_trace = go.Scatter3d(
        x=positions[:, 0], y=positions[:, 1], z=positions[:, 2],
        mode="lines",
        line=dict(color="rgba(255,255,100,0.3)", width=3),
        name="Writing Arc", showlegend=False,
    )

    return [slots_trace, arc_trace]


def create_trajectory_trace(trajectory_positions: list) -> go.Scatter3d:
    """Create trajectory path trace."""
    if not trajectory_positions:
        return go.Scatter3d(x=[], y=[], z=[], mode="lines", name="Trajectory")
    pos = np.array(trajectory_positions)
    return go.Scatter3d(
        x=pos[:, 0], y=pos[:, 1], z=pos[:, 2],
        mode="lines",
        line=dict(color="rgba(255,100,255,0.4)", width=2),
        name="Trajectory",
    )


def build_figure(traces: list, title: str = "Robotic Writer 3D Simulation") -> go.Figure:
    """Build a 3D figure with consistent layout and uirevision to preserve camera."""
    fig = go.Figure(data=traces)
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X (mm)", range=[-500, 500],
                       backgroundcolor="rgba(0,0,0,0)", color="#aaa",
                       gridcolor="#333"),
            yaxis=dict(title="Y (mm)", range=[-500, 500],
                       backgroundcolor="rgba(0,0,0,0)", color="#aaa",
                       gridcolor="#333"),
            zaxis=dict(title="Z (mm)", range=[0, 600],
                       backgroundcolor="rgba(0,0,0,0)", color="#aaa",
                       gridcolor="#333"),
            aspectmode="cube",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.0)),
        ),
        paper_bgcolor="rgba(30,30,30,1)",
        plot_bgcolor="rgba(30,30,30,1)",
        font=dict(color="white"),
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(x=0, y=1, bgcolor="rgba(0,0,0,0.5)"),
        title=dict(text=title, x=0.5, font=dict(size=14)),
        # CRITICAL: uirevision preserves camera/zoom between updates
        uirevision="constant",
    )

    # Ground plane
    s = 500
    fig.add_trace(go.Mesh3d(
        x=[-s, s, s, -s], y=[-s, -s, s, s], z=[0, 0, 0, 0],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color="rgba(50,50,50,0.3)", name="Ground", showlegend=False,
    ))

    return fig


# ── Layout components ─────────────────────────────────────────────────────

def make_slider(id_str: str, label: str, min_val: float, max_val: float,
                value: float, step: float = 1.0) -> html.Div:
    """Create a labeled slider with proper dark-mode spacing."""
    return html.Div([
        html.Label(label, className="text-light",
                   style={"fontSize": "0.85rem", "marginBottom": "2px"}),
        dcc.Slider(
            id=id_str, min=min_val, max=max_val, value=value, step=step,
            marks=None,
            tooltip={"placement": "bottom", "always_visible": True},
        ),
    ], className="slider-container", style={"marginBottom": "30px"})


def make_config_slider(id_str: str, label: str, min_val: float, max_val: float,
                       value: float, step: float = 1.0) -> html.Div:
    """Slider for config panels with extra spacing."""
    return html.Div([
        html.Label(label, className="text-light",
                   style={"fontSize": "0.8rem", "marginBottom": "2px"}),
        dcc.Slider(
            id=id_str, min=min_val, max=max_val, value=value, step=step,
            marks=None,
            tooltip={"placement": "bottom", "always_visible": True},
        ),
    ], style={"marginBottom": "26px"})


# ── Sidebar ───────────────────────────────────────────────────────────────

sidebar = dbc.Card([
    dbc.CardHeader(html.H5("Control Panel", className="mb-0")),
    dbc.CardBody([
        dbc.Tabs(id="control-tabs", active_tab="tab-tutorial", children=[
            # ── Tutorial Tab ──
            dbc.Tab(label="Tutorial", tab_id="tab-tutorial", children=[
                html.Div([
                    html.P("Type a phrase and the robot writes it letter by letter.",
                           className="text-muted small mt-2 mb-3"),
                    html.Label("Your phrase:", className="text-light mb-1"),
                    dbc.Input(id="input-text", type="text", value="HELLO",
                              placeholder="Type something...", maxLength=15,
                              className="mb-3"),
                    make_config_slider("slider-radius", "Block Circle Radius (mm)",
                                       200, 400, 280, 10),
                    make_config_slider("slider-angle-sep", "Angular Separation (deg)",
                                       3, 20, 8, 0.5),
                    make_config_slider("slider-spacing", "Slot Spacing (deg)",
                                       2, 8, 4, 0.5),
                    dbc.Switch(
                        id="switch-infinite",
                        label="Infinite block replacement",
                        value=True,
                        className="mb-3 text-light",
                    ),
                    dbc.Button("Write It!", id="btn-simulate", color="primary",
                               className="w-100 mt-2", n_clicks=0),
                    dbc.Button("Reset", id="btn-reset", color="secondary",
                               className="w-100 mt-2", n_clicks=0),
                ], className="p-2"),
            ]),
            # ── Ouija Tab ──
            dbc.Tab(label="Ouija", tab_id="tab-ouija", children=[
                html.Div([
                    html.Div(
                        html.Span("OUIJA",
                                  style={"fontSize": "1.5rem", "fontWeight": "bold",
                                         "letterSpacing": "0.5em", "color": "#9C27B0"}),
                        className="text-center mt-2 mb-2",
                    ),
                    html.P("Ask a question... the spirits will respond.",
                           className="text-muted small fst-italic mb-3"),
                    html.Label("Your question:", className="text-light mb-1"),
                    dbc.Input(id="input-ouija", type="text", value="",
                              placeholder="Ask the spirits...", maxLength=100,
                              className="mb-3"),
                    html.Div(id="ouija-response-preview", className="mb-2"),
                    dbc.Button("Consult the Spirits", id="btn-ouija", color="dark",
                               className="w-100 mt-1", n_clicks=0,
                               style={"backgroundColor": "#4A148C",
                                      "borderColor": "#7B1FA2"}),
                    dbc.Button("Ask Again", id="btn-ouija-reroll", color="secondary",
                               outline=True, className="w-100 mt-2", n_clicks=0,
                               size="sm"),
                    html.Hr(className="border-secondary"),
                    html.Div(id="ouija-history",
                             style={"maxHeight": "200px", "overflowY": "auto",
                                    "fontSize": "0.8rem"}),
                ], className="p-2"),
            ]),
            # ── Kinematics Tab ──
            dbc.Tab(label="Kinematics", tab_id="tab-kinematics", children=[
                html.Div([
                    html.H6("Joint Angles (degrees)",
                            className="text-light mt-3 mb-3"),
                    make_slider("slider-j1", "Base (J1)", -126.5, 126.5, 0, 0.5),
                    make_slider("slider-j2", "Shoulder (J2)", -120, 63, 0, 0.5),
                    make_slider("slider-j3", "Elbow (J3)", -90, 90, 0, 0.5),
                    make_slider("slider-j4", "Pitch (J4)", -250, 40, 0, 0.5),
                    make_slider("slider-j5", "Roll (J5)", -180, 180, 0, 0.5),
                    html.Hr(className="border-secondary"),
                    html.Div(id="fk-result", className="text-info small"),
                ], className="p-2"),
            ]),
        ]),
    ]),
], className="h-100", style={"backgroundColor": "rgba(40,40,40,1)"})


# ── Main content ──────────────────────────────────────────────────────────

main_content = html.Div([
    # 3D visualization
    dcc.Graph(id="graph-3d", style={"height": "60vh"},
              config={"displayModeBar": True, "scrollZoom": True}),

    # Bottom panel
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Animation", className="py-2"),
                dbc.CardBody([
                    html.Div([
                        dcc.Slider(id="slider-frame", min=0, max=100, value=0, step=1,
                                   marks=None,
                                   tooltip={"placement": "bottom",
                                            "always_visible": True}),
                    ], style={"marginBottom": "20px"}),
                    dbc.ButtonGroup([
                        dbc.Button("<<", id="btn-start", size="sm", color="info",
                                   n_clicks=0),
                        dbc.Button("<", id="btn-prev", size="sm", color="info",
                                   n_clicks=0),
                        dbc.Button("Play", id="btn-play", size="sm", color="success",
                                   n_clicks=0, style={"minWidth": "80px"}),
                        dbc.Button(">", id="btn-next", size="sm", color="info",
                                   n_clicks=0),
                        dbc.Button(">>", id="btn-end", size="sm", color="info",
                                   n_clicks=0),
                    ], className="w-100 d-flex justify-content-center"),
                    dcc.Interval(id="interval-play", interval=80, disabled=True,
                                 n_intervals=0),
                ], className="py-2"),
            ], style={"backgroundColor": "rgba(40,40,40,1)"}),
        ], md=5),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Action Log", className="py-2"),
                dbc.CardBody([
                    html.Div(
                        id="action-log",
                        style={"height": "120px", "overflowY": "auto",
                               "fontSize": "0.78rem"},
                    ),
                ], className="py-2"),
            ], style={"backgroundColor": "rgba(40,40,40,1)"}),
        ], md=7),
    ], className="mt-2"),
])


# ── App layout ────────────────────────────────────────────────────────────

app.layout = dbc.Container([

    dbc.Row([
        dbc.Col(html.H2("Robotic Writer Simulator",
                         className="text-center text-primary my-3")),
    ]),
    dbc.Row([
        dbc.Col(sidebar, md=3),
        dbc.Col(main_content, md=9),
    ]),
    # Hidden stores
    dcc.Store(id="store-sim-data", data=None),
    dcc.Store(id="store-playing", data=False),
    dcc.Store(id="store-ouija-response", data=""),
    dcc.Store(id="store-ouija-history", data=[]),
], fluid=True, style={"backgroundColor": "rgba(20,20,20,1)", "minHeight": "100vh"})


# ═══════════════════════════════════════════════════════════════════════════
# CALLBACKS
# ═══════════════════════════════════════════════════════════════════════════

def _run_writer(text: str, radius: float, angle_sep: float, spacing: float,
                infinite: bool = True):
    """Execute writer simulation. Returns (sim_data, log_html)."""
    block_circle = BlockCircle(
        radius_mm=radius,
        block_height_mm=50.0,
        min_angular_separation_deg=angle_sep,
    )
    writing_line = WritingLine(
        radius_mm=radius + 20,
        angular_spacing_deg=spacing,
    )
    robot = ScorbotIII(interpolation_steps=30)
    writer = RoboticWriter(robot=robot, block_circle=block_circle,
                           writing_line=writing_line,
                           infinite_replacement=infinite)

    action_log = writer.write_text(text)
    sim_data = writer.get_simulation_data()

    log_items = []
    for i, action in enumerate(action_log):
        color = {
            "pick": "text-success", "place": "text-warning",
            "start": "text-primary", "done": "text-primary",
            "space": "text-muted", "skip": "text-danger",
        }.get(action["action"], "text-light")
        log_items.append(html.Div(
            f"[{i}] {action['description']}", className=color,
        ))

    return sim_data, log_items


# ── Tutorial simulation ───────────────────────────────────────────────────

@callback(
    Output("store-sim-data", "data"),
    Output("action-log", "children"),
    Output("slider-frame", "value", allow_duplicate=True),
    Input("btn-simulate", "n_clicks"),
    State("input-text", "value"),
    State("slider-radius", "value"),
    State("slider-angle-sep", "value"),
    State("slider-spacing", "value"),
    State("switch-infinite", "value"),
    prevent_initial_call=True,
)
def run_tutorial(n_clicks, text, radius, angle_sep, spacing, infinite):
    if not text:
        return no_update, no_update, no_update
    sim_data, log_items = _run_writer(text.upper(), radius, angle_sep, spacing,
                                      infinite)
    return sim_data, log_items, 0


# ── Ouija preview ─────────────────────────────────────────────────────────

@callback(
    Output("store-ouija-response", "data"),
    Output("ouija-response-preview", "children"),
    Input("input-ouija", "value"),
    Input("btn-ouija-reroll", "n_clicks"),
    prevent_initial_call=True,
)
def preview_ouija(question, _reroll):
    if not question:
        return "", html.Div()
    response = generate_ouija_response(question)
    return response, dbc.Alert(
        [html.Strong("The spirits say: "), response],
        color="dark", className="mb-0 py-2",
        style={"backgroundColor": "rgba(74,20,140,0.3)",
               "borderColor": "#7B1FA2", "color": "#CE93D8"},
    )


# ── Ouija simulation ─────────────────────────────────────────────────────

@callback(
    Output("store-sim-data", "data", allow_duplicate=True),
    Output("action-log", "children", allow_duplicate=True),
    Output("slider-frame", "value", allow_duplicate=True),
    Output("store-ouija-history", "data"),
    Output("ouija-history", "children"),
    Input("btn-ouija", "n_clicks"),
    State("input-ouija", "value"),
    State("store-ouija-response", "data"),
    State("store-ouija-history", "data"),
    State("slider-radius", "value"),
    State("slider-angle-sep", "value"),
    State("slider-spacing", "value"),
    State("switch-infinite", "value"),
    prevent_initial_call=True,
)
def run_ouija(n_clicks, question, response, history, radius, angle_sep, spacing,
              infinite):
    if not response:
        return no_update, no_update, no_update, no_update, no_update

    sim_data, log_items = _run_writer(response, radius, angle_sep, spacing,
                                      infinite)

    updated_history = (history or []) + [{"question": question, "answer": response}]

    history_items = []
    for entry in reversed(updated_history[-10:]):
        history_items.append(html.Div([
            html.Span(f"Q: {entry['question']}", className="text-muted"),
            html.Br(),
            html.Span(f"A: {entry['answer']}", className="text-warning fw-bold"),
        ], className="mb-2 border-bottom border-secondary pb-1"))

    return sim_data, log_items, 0, updated_history, history_items


# ── 3D view update ────────────────────────────────────────────────────────

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
def update_3d_view(sim_data, frame, j1, j2, j3, j4, j5, active_tab,
                   reset_clicks, radius, angle_sep, spacing):
    traces = []

    if active_tab == "tab-kinematics":
        # Manual kinematics explorer
        joint_state = JointState.from_degrees([j1, j2, j3, j4, j5])
        traces.extend(create_robot_traces(joint_state))
        bc = BlockCircle(radius_mm=radius, min_angular_separation_deg=angle_sep)
        pos = bc.get_arc_points()
        chars = [b.character for b in bc.blocks]
        avail = [True] * len(bc.blocks)
        traces.extend(create_block_circle_traces(pos, chars, avail))

    elif sim_data is not None and active_tab != "tab-kinematics":
        # Simulation playback
        traj = sim_data["trajectory"]
        positions = traj.get("positions", [])
        joint_angles = traj.get("joint_angles_deg", [])

        if positions and joint_angles:
            max_frame = len(positions) - 1
            frame_idx = min(max(0, frame or 0), max_frame)

            angles = joint_angles[frame_idx]
            joint_state = JointState.from_degrees(angles)
            traces.extend(create_robot_traces(joint_state))
            traces.append(create_trajectory_trace(positions[:frame_idx + 1]))

        # Block circle - all blocks always green (infinite replacement),
        # except used ones shown in blue
        bc_data = sim_data.get("block_circle", {})
        bc_positions = bc_data.get("positions", [])
        bc_chars = bc_data.get("characters", [])
        bc_available = bc_data.get("available", [])
        if bc_positions:
            traces.extend(create_block_circle_traces(
                np.array(bc_positions), bc_chars, bc_available,
            ))

        # Writing arc
        wl_data = sim_data.get("writing_line", {})
        if wl_data:
            wl = WritingLine(
                radius_mm=wl_data.get("radius_mm", 300.0),
                center_angle_deg=wl_data.get("center_angle_deg", -25.0),
                angular_spacing_deg=wl_data.get("angular_spacing_deg", 4.0),
                height_mm=wl_data.get("height_mm", 50.0),
            )
            traces.extend(create_writing_line_traces(wl))

    else:
        # Default view
        joint_state = JointState()
        traces.extend(create_robot_traces(joint_state))
        bc = BlockCircle(radius_mm=radius, min_angular_separation_deg=angle_sep)
        pos = bc.get_arc_points()
        chars = [b.character for b in bc.blocks]
        avail = [True] * len(bc.blocks)
        traces.extend(create_block_circle_traces(pos, chars, avail))
        wl = WritingLine(radius_mm=radius + 20, angular_spacing_deg=spacing)
        traces.extend(create_writing_line_traces(wl))

    return build_figure(traces)


# ── Frame slider max ──────────────────────────────────────────────────────

@callback(
    Output("slider-frame", "max"),
    Input("store-sim-data", "data"),
)
def update_frame_max(sim_data):
    if sim_data is None:
        return 100
    n = len(sim_data.get("trajectory", {}).get("positions", []))
    return max(n - 1, 1)


# ── FK display ────────────────────────────────────────────────────────────

@callback(
    Output("fk-result", "children"),
    Input("slider-j1", "value"),
    Input("slider-j2", "value"),
    Input("slider-j3", "value"),
    Input("slider-j4", "value"),
    Input("slider-j5", "value"),
)
def update_fk_display(j1, j2, j3, j4, j5):
    joint_state = JointState.from_degrees([j1, j2, j3, j4, j5])
    result = fk_engine.compute(joint_state)
    pos = result["position"]
    return html.Div([
        html.P("End Effector Position:", className="mb-1 fw-bold text-info"),
        html.P(f"X = {pos[0]:.2f} mm", className="mb-0 text-light"),
        html.P(f"Y = {pos[1]:.2f} mm", className="mb-0 text-light"),
        html.P(f"Z = {pos[2]:.2f} mm", className="mb-0 text-light"),
    ])


# ── Play / Pause toggle ──────────────────────────────────────────────────

@callback(
    Output("interval-play", "disabled"),
    Output("store-playing", "data"),
    Output("btn-play", "children"),
    Input("btn-play", "n_clicks"),
    State("store-playing", "data"),
    prevent_initial_call=True,
)
def toggle_play(n_clicks, playing):
    new_playing = not playing
    return (not new_playing), new_playing, ("Pause" if new_playing else "Play")


# ── Frame navigation (play interval + buttons) ───────────────────────────

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
def update_frame(_n_intervals, _start, _end, _prev, _next,
                 current_frame, max_frame):
    trigger_id = ctx.triggered_id
    if trigger_id is None:
        return no_update

    if trigger_id == "interval-play":
        nf = (current_frame or 0) + 3
        return nf if nf <= max_frame else 0
    elif trigger_id == "btn-start":
        return 0
    elif trigger_id == "btn-end":
        return max_frame
    elif trigger_id == "btn-prev":
        return max(0, (current_frame or 0) - 5)
    elif trigger_id == "btn-next":
        return min(max_frame, (current_frame or 0) + 5)

    return no_update


# ── Server ────────────────────────────────────────────────────────────────

server = app.server

if __name__ == "__main__":
    app.run(debug=True, port=8050)
