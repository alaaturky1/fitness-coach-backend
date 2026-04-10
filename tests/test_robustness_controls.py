from app.analysis.engine import CoachingEngine
from app.core.models import FrameInput, Joint, Language


def _frame(ex: str, t: float, *, angles: dict[str, float] | None = None, joints: list[Joint] | None = None) -> FrameInput:
    return FrameInput(exercise=ex, joints=joints, angles=angles, timestamp=t)


def test_visibility_low_pauses_when_no_angles_and_missing_joints() -> None:
    engine = CoachingEngine(session_id="v1", language=Language.en, level="beginner")
    joints = [Joint(name="hip_l", x=0.0, y=0.0, confidence=0.9)]
    resp = engine.analyze(_frame("squat", 0.0, angles=None, joints=joints))
    assert resp.paused is True
    assert "visibility_low" in resp.issues
    assert resp.score == 0.0


def test_low_confidence_joints_pauses_when_no_angles() -> None:
    engine = CoachingEngine(session_id="v2", language=Language.en, level="beginner")
    joints = [
        Joint(name="hip_l", x=-1.0, y=0.0, confidence=0.2),
        Joint(name="hip_r", x=1.0, y=0.0, confidence=0.2),
        Joint(name="knee_l", x=-1.0, y=1.0, confidence=0.2),
        Joint(name="knee_r", x=1.0, y=1.0, confidence=0.2),
        Joint(name="ankle_l", x=-1.0, y=2.0, confidence=0.2),
        Joint(name="ankle_r", x=1.0, y=2.0, confidence=0.2),
        Joint(name="shoulder_l", x=-1.0, y=-1.0, confidence=0.2),
        Joint(name="shoulder_r", x=1.0, y=-1.0, confidence=0.2),
    ]
    resp = engine.analyze(_frame("squat", 0.0, angles=None, joints=joints))
    assert resp.paused is True
    assert "visibility_low" in resp.issues


def test_if_angles_provided_do_not_pause_even_when_joints_missing() -> None:
    engine = CoachingEngine(session_id="v3", language=Language.en, level="beginner")
    joints = [Joint(name="hip_l", x=0.0, y=0.0, confidence=0.1)]
    resp = engine.analyze(_frame("squat", 0.0, angles={"knee_l": 175.0, "knee_r": 175.0, "torso_l_vs_vertical": 20.0}, joints=joints))
    assert resp.paused is False


def test_rep_cooldown_prevents_double_counting() -> None:
    engine = CoachingEngine(session_id="cd1", language=Language.en, level="beginner")
    # Two fast squat reps back-to-back in < cooldown window. Only one should be counted.
    # Rep cycle: down (<=150) then up (>=165)
    # Include a couple of "top" frames after each ascent so smoothing doesn't prevent the >=165 lockout detection.
    series = [175, 140, 110, 175, 175, 140, 110, 175, 175]
    t = 0.0
    for k in series:
        engine.analyze(_frame("squat", t, angles={"knee_l": float(k), "knee_r": float(k), "torso_l_vs_vertical": 20.0}))
        t += 0.10  # 0.3s between rep completions
    assert engine.summary().reps == 1

