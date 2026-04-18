# References

Theory, tooling, and inspiration consulted while building the Robotic Writer.

## 1. Robotics — Kinematics & Trajectory

1. **Craig, J. J.** *Introduction to Robotics: Mechanics and Control* (3rd ed.), Pearson, 2005. — canonical reference for the Denavit-Hartenberg convention and the FK/IK derivations used in [equations/kinematics.md](equations/kinematics.md).
2. **Spong, M. W., Hutchinson, S., Vidyasagar, M.** *Robot Modeling and Control*, Wiley, 2005. — planar 2R arm geometry underlying the θ₂, θ₃ closed-form solution.
3. **Siciliano, B., Khatib, O. (eds.)** *Springer Handbook of Robotics* (2nd ed.), 2016. — trajectory planning background (cubic / quintic splines).
4. **LaValle, S. M.** *Planning Algorithms*, Cambridge University Press, 2006. Free at http://lavalle.pl/planning/. — RRT formulation used in `src/core/rrt_planner.py`.

## 2. Scorbot III Hardware (Origin)

5. **Eshed Robotec, Scorbot-ER III User's Manual**, 1988. — physical parameters (link lengths, joint ranges) informing the DH table in the code.
6. **Universidad de Concepción, Curso Control Automático I (2004)** — lab assignment that seeded this project; see project origin note in the README.

## 3. Arduino / Stepper Motor Stack

7. **Pololu A4988 / DRV8825 datasheets** — step/direction logic that the `ArduinoAdapter` protocol targets. See [arduino_firmware.md](arduino_firmware.md).
8. **Arduino AccelStepper library** — acceleration profile design reference for the firmware half of the Arduino backend.

## 4. Web Stack

9. **Ramírez, S.** *FastAPI Documentation* — https://fastapi.tiangolo.com/. Pydantic schema patterns used for every endpoint in `src/api/main.py`.
10. **Plotly Dash Documentation** — https://dash.plotly.com/. Source for the callback patterns and 3D scene used in `src/frontend/app.py`.

## 5. Cursive / Bezier

11. **de Casteljau, P.** *Outillages méthodes calcul*, 1959. — algorithmic foundation for the Bezier curves generated in `core/cursive.py`.

## 6. Project-Internal

- [README.md](../README.md) — project overview, KPIs, quick start.
- [methodology.md](methodology.md) — problem statement.
- [architecture.md](architecture.md) — system decomposition.
- [equations/kinematics.md](equations/kinematics.md) — full FK/IK derivations.
- [arduino_firmware.md](arduino_firmware.md) — wire protocol for the Arduino backend.
- [development_history.md](development_history.md) — change log (re-exported from `Methodology_history.md`).
- [user_guide.md](user_guide.md) — end-user workflow.
