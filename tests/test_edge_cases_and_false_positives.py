from app.analysis.engine import CoachingEngine
from app.core.models import FrameInput, Language


def _frame(ex: str, t: float, angles: dict[str, float]) -> FrameInput:
    return FrameInput(exercise=ex, joints=None, angles=angles, timestamp=t)


def test_no_false_positive_when_idle_standing_squat() -> None:
    engine = CoachingEngine(session_id="idle1", language=Language.en, level="beginner")
    # Always "standing" knee angle: should not start a rep.
    for i in range(60):
        engine.analyze(_frame("squat", i * 0.05, {"knee_l": 175.0, "knee_r": 175.0, "torso_l_vs_vertical": 15.0}))
    assert engine.summary().reps == 0


def test_no_false_positive_when_idle_top_pushup() -> None:
    engine = CoachingEngine(session_id="idle2", language=Language.en, level="beginner")
    for i in range(60):
        engine.analyze(_frame("pushup", i * 0.05, {"elbow_l": 175.0, "elbow_r": 175.0}))
    assert engine.summary().reps == 0


def test_squat_rep_requires_down_then_up_transition() -> None:
    engine = CoachingEngine(session_id="sreq", language=Language.en, level="beginner")
    # Goes down but never comes back up to >=165: should not count.
    for i, k in enumerate([175, 160, 130, 115, 105, 110, 120, 130, 140]):
        engine.analyze(_frame("squat", i * 0.05, {"knee_l": float(k), "knee_r": float(k), "torso_l_vs_vertical": 20.0}))
    assert engine.summary().reps == 0


def test_pushup_rep_requires_lockout_return() -> None:
    engine = CoachingEngine(session_id="preq", language=Language.en, level="beginner")
    for i, e in enumerate([175, 160, 135, 120, 105, 110, 130, 150, 160]):
        engine.analyze(_frame("pushup", i * 0.05, {"elbow_l": float(e), "elbow_r": float(e)}))
    assert engine.summary().reps == 0


def test_borderline_thresholds_do_not_double_count() -> None:
    engine = CoachingEngine(session_id="border", language=Language.en, level="beginner")
    # Oscillate near transition thresholds; should count at most 1 rep when a full cycle occurs.
    series = [175, 166, 164, 166, 164, 166, 150, 120, 110, 120, 150, 164, 166, 164, 166, 175]
    for i, k in enumerate(series):
        engine.analyze(_frame("squat", i * 0.05, {"knee_l": float(k), "knee_r": float(k), "torso_l_vs_vertical": 20.0}))
    assert engine.summary().reps == 1

