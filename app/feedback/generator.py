from __future__ import annotations

from app.core.models import Language


# Stored as unicode escape sequences to avoid editor/encoding issues on Windows.
ISSUE_TO_TEXT_ESCAPED: dict[str, dict[str, str]] = {
    "visibility_low": {
        "en": "Make sure your full body is visible to the camera.",
        "ar": "\\u062e\\u0644\\u064a \\u062c\\u0633\\u0645\\u0643 \\u0643\\u0644\\u0647 \\u0648\\u0627\\u0636\\u062d \\u0641\\u064a \\u0627\\u0644\\u0643\\u0627\\u0645\\u064a\\u0631\\u0627.",
    },
    "excessive_forward_lean": {
        "en": "Chest up, keep your torso more upright.",
        "ar": "\\u0627\\u0631\\u0641\\u0639 \\u0635\\u062f\\u0631\\u0643 \\u0648\\u062e\\u0644\\u064a \\u062c\\u0630\\u0639\\u0643 \\u0645\\u0633\\u062a\\u0642\\u064a\\u0645 \\u0623\\u0643\\u062a\\u0631.",
    },
    "knee_valgus_left": {
        "en": "Track your left knee over your toes.",
        "ar": "\\u062e\\u0644\\u0651\\u064a \\u0631\\u0643\\u0628\\u062a\\u0643 \\u0627\\u0644\\u0634\\u0645\\u0627\\u0644 \\u0641\\u0648\\u0642 \\u0635\\u0648\\u0627\\u0628\\u0639 \\u0631\\u062c\\u0644\\u0643.",
    },
    "knee_valgus_right": {
        "en": "Track your right knee over your toes.",
        "ar": "\\u062e\\u0644\\u0651\\u064a \\u0631\\u0643\\u0628\\u062a\\u0643 \\u0627\\u0644\\u064a\\u0645\\u064a\\u0646 \\u0641\\u0648\\u0642 \\u0635\\u0648\\u0627\\u0628\\u0639 \\u0631\\u062c\\u0644\\u0643.",
    },
    "hips_sagging": {
        "en": "Tighten your core—don’t let your hips drop.",
        "ar": "\\u0634\\u062f\\u0651 \\u0628\\u0637\\u0646\\u0643\\u2014\\u0645\\u0627 \\u062a\\u0633\\u064a\\u0628\\u0634 \\u0627\\u0644\\u062d\\u0648\\u0636 \\u064a\\u0647\\u0628\\u0637.",
    },
    "hips_off_line": {
        "en": "Keep your body in a straight line.",
        "ar": "\\u062e\\u0644\\u0651\\u064a \\u062c\\u0633\\u0645\\u0643 \\u062e\\u0637 \\u0645\\u0633\\u062a\\u0642\\u064a\\u0645.",
    },
    "shallow_depth": {
        "en": "Go a bit deeper while staying controlled.",
        "ar": "\\u0627\\u0646\\u0632\\u0644 \\u0623\\u0643\\u062a\\u0631 \\u0634\\u0648\\u064a\\u0629 \\u0645\\u0639 \\u062a\\u062d\\u0643\\u0651\\u0645.",
    },
    "unknown_exercise": {
        "en": "Tell me the exercise type to coach you better.",
        "ar": "\\u0642\\u0648\\u0644\\u064a \\u0647\\u0648 \\u0627\\u064a\\u0647 \\u0627\\u0644\\u062a\\u0645\\u0631\\u064a\\u0646 \\u0639\\u0634\\u0627\\u0646 \\u0627\\u062f\\u064a\\u0643 \\u0646\\u0635\\u064a\\u062d\\u0629 \\u0623\\u062f\\u0642.",
    },
}


DEFAULT_POSITIVE_ESCAPED = {
    "en": "Good rep. Keep it controlled.",
    "ar": "\\u062a\\u0645\\u0627\\u0645. \\u062e\\u0644\\u064a\\u0643 \\u0645\\u062a\\u062d\\u0643\\u0651\\u0645.",
}


def _unescape(s: str) -> str:
    # NOTE: s is ASCII; decode unicode escapes to real Unicode.
    return s.encode("utf-8").decode("unicode_escape")


def pick_feedback(language: Language, issues: list[str]) -> str:
    lang = language.value
    for issue in issues:
        txt = ISSUE_TO_TEXT_ESCAPED.get(issue)
        if txt:
            return _unescape(txt.get(lang, txt["en"]))
    return _unescape(DEFAULT_POSITIVE_ESCAPED.get(lang, DEFAULT_POSITIVE_ESCAPED["en"]))

