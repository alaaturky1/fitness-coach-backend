from app.analysis.engine import CoachingEngine
from app.core.models import FrameInput, Language


def test_squat_counts_one_rep_from_angles_only() -> None:
    engine = CoachingEngine(session_id="s1", language=Language.en, level="beginner")

    knee_series = [175, 165, 140, 120, 105, 95, 110, 140, 170, 175]
    for i, k in enumerate(knee_series):
        frame = FrameInput(
            exercise="squat",
            joints=None,
            angles={"knee_l": float(k), "knee_r": float(k), "torso_l_vs_vertical": 20.0},
            timestamp=float(i) * 0.05,
            frame_id=i,
        )
        engine.analyze(frame)

    summary = engine.summary()
    assert summary.reps == 1
    assert summary.avg_rep_score is not None
    assert 0.0 <= summary.avg_rep_score <= 100.0


def test_squat_flags_forward_lean() -> None:
    engine = CoachingEngine(session_id="s2", language=Language.en, level="beginner")
    frame = FrameInput(
        exercise="squat",
        joints=None,
        angles={"knee_l": 110.0, "knee_r": 110.0, "torso_l_vs_vertical": 60.0},
        timestamp=0.0,
        frame_id=0,
    )
    resp = engine.analyze(frame)
    assert "excessive_forward_lean" in resp.issues

