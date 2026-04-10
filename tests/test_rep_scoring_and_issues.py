from app.analysis.engine import CoachingEngine
from app.core.models import FrameInput, Language


def _frame(ex: str, t: float, angles: dict[str, float]) -> FrameInput:
    return FrameInput(exercise=ex, joints=None, angles=angles, timestamp=t)


def test_squat_shallow_rep_scores_lower_and_flags_issue() -> None:
    engine = CoachingEngine(session_id="s_shallow", language=Language.en, level="beginner")

    # Down to only ~130 degrees (shallow), then back up.
    series = [175, 165, 150, 140, 132, 130, 135, 150, 165, 175]
    for i, k in enumerate(series):
        engine.analyze(_frame("squat", i * 0.05, {"knee_l": float(k), "knee_r": float(k), "torso_l_vs_vertical": 20.0}))

    summary = engine.summary()
    assert summary.reps == 1
    rep = summary.rep_summaries[0]
    assert rep.score < 100.0
    assert "shallow_depth" in rep.issues


def test_pushup_shallow_rep_scores_lower_and_flags_issue() -> None:
    engine = CoachingEngine(session_id="p_shallow", language=Language.en, level="beginner")

    # Down to only ~150 degrees (shallow), then back to lockout.
    series = [175, 170, 165, 160, 155, 150, 155, 160, 170, 175]
    for i, e in enumerate(series):
        engine.analyze(_frame("pushup", i * 0.05, {"elbow_l": float(e), "elbow_r": float(e)}))

    summary = engine.summary()
    assert summary.reps == 1
    rep = summary.rep_summaries[0]
    assert rep.score < 100.0
    assert "shallow_depth" in rep.issues

