from app.analysis.engine import CoachingEngine
from app.core.models import FrameInput, Joint, Language


def _j(name: str, x: float, y: float) -> Joint:
    return Joint(name=name, x=x, y=y, confidence=1.0)


def test_pushup_hips_sagging_detected() -> None:
    """
    Build a near-straight shoulder->ankle line at y=0, and put hips far off the line.
    The analyzer uses normalized perpendicular distance > 6% of body length.
    """

    engine = CoachingEngine(session_id="hips", language=Language.en, level="beginner")

    joints = [
        _j("shoulder_l", -1.0, 0.0),
        _j("shoulder_r", 1.0, 0.0),
        # Ankles further away to create a non-zero shoulder->ankle body length.
        _j("ankle_l", -1.0, 2.0),
        _j("ankle_r", 1.0, 2.0),
        # Move hips off the shoulder->ankle line (x=0) to exceed threshold.
        _j("hip_l", 0.4, 0.8),
        _j("hip_r", 0.8, 0.8),
        # minimal arms for pushup detection/angles not needed here
        _j("elbow_l", -1.0, 0.0),
        _j("wrist_l", -1.0, 0.0),
        _j("elbow_r", 1.0, 0.0),
        _j("wrist_r", 1.0, 0.0),
    ]

    frame = FrameInput(exercise="pushup", joints=joints, angles={"elbow_l": 150.0, "elbow_r": 150.0}, timestamp=0.0)
    resp = engine.analyze(frame)
    assert "hips_sagging" in resp.issues


def test_squat_knee_valgus_detected_left() -> None:
    engine = CoachingEngine(session_id="valgus", language=Language.en, level="beginner")

    # hips define width=2; threshold = 0.2
    # left knee medial relative to left ankle by 0.4 -> valgus
    joints = [
        _j("hip_l", -1.0, 0.0),
        _j("hip_r", 1.0, 0.0),
        _j("knee_l", -0.2, 1.0),
        _j("ankle_l", -0.8, 2.0),
        _j("knee_r", 0.8, 1.0),
        _j("ankle_r", 0.8, 2.0),
        _j("shoulder_l", -1.0, -1.0),
        _j("shoulder_r", 1.0, -1.0),
    ]
    frame = FrameInput(exercise="squat", joints=joints, angles={"knee_l": 110.0, "knee_r": 110.0}, timestamp=0.0)
    resp = engine.analyze(frame)
    assert "knee_valgus_left" in resp.issues

