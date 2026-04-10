from app.analysis.engine import CoachingEngine
from app.core.models import FrameInput, Language


def test_pushup_counts_one_rep_from_angles_only() -> None:
    engine = CoachingEngine(session_id="p1", language=Language.en, level="beginner")

    elbow_series = [175, 170, 150, 130, 110, 95, 110, 140, 170, 175]
    for i, e in enumerate(elbow_series):
        frame = FrameInput(
            exercise="pushup",
            joints=None,
            angles={"elbow_l": float(e), "elbow_r": float(e)},
            timestamp=float(i) * 0.05,
            frame_id=i,
        )
        engine.analyze(frame)

    summary = engine.summary()
    assert summary.reps == 1
    assert summary.avg_rep_score is not None

