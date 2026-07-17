"""Ba trục điểm: phát âm, trôi chảy, giao tiếp.

Không dùng transcript thô làm điểm phát âm — whisper tự sửa lỗi về từ đúng.
Chấm ở mức âm vị, trộn thêm word probability của whisper.
"""
import difflib
import re

from speech_service.g2p import word_to_phonemes

WPM_IDEAL = (90, 160)     # A1-A2 nói chậm là bình thường
PAUSE_BAD = 0.45


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z']+", text.lower())


def _phoneme_score(expected_word: str, said_word: str, prob: float) -> tuple[float, dict]:
    exp = word_to_phonemes(expected_word)
    said = word_to_phonemes(said_word)
    if not exp:
        return 100.0, {}
    matcher = difflib.SequenceMatcher(None, exp, said)
    ratio = matcher.ratio()
    missing, inserted = [], []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ("delete", "replace"):
            missing.extend(exp[i1:i2])
        if tag in ("insert", "replace"):
            inserted.extend(said[j1:j2])
    confidence = max(0.0, min(1.0, prob)) if prob > 0 else 0.7
    score = 100.0 * (0.70 * ratio + 0.30 * confidence)
    return round(score, 1), {"missing": missing, "inserted": inserted}


def score_pronunciation(expected_text: str, words: list[dict]) -> tuple[float, dict]:
    exp_words = _words(expected_text)
    said = [{"w": re.sub(r"[^a-z']", "", w["word"].lower()), "p": w.get("prob", 0.0)}
            for w in words]
    said = [s for s in said if s["w"]]
    if not exp_words:
        return 0.0, {"words": [], "missing_phonemes": [], "inserted_phonemes": []}
    if not said:
        return 0.0, {"words": [{"word": w, "score": 0.0} for w in exp_words],
                     "missing_phonemes": [], "inserted_phonemes": []}
    matcher = difflib.SequenceMatcher(None, exp_words, [s["w"] for s in said])
    per_word, missing_all, inserted_all = [], [], []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                sc, diff = _phoneme_score(exp_words[i1 + k], said[j1 + k]["w"], said[j1 + k]["p"])
                per_word.append({"word": exp_words[i1 + k], "score": sc})
                missing_all.extend(diff.get("missing", []))
                inserted_all.extend(diff.get("inserted", []))
        elif tag == "replace":
            for k in range(i2 - i1):
                if j1 + k < j2:
                    sc, diff = _phoneme_score(exp_words[i1 + k], said[j1 + k]["w"], said[j1 + k]["p"])
                    per_word.append({"word": exp_words[i1 + k], "score": sc})
                    missing_all.extend(diff.get("missing", []))
                    inserted_all.extend(diff.get("inserted", []))
                else:
                    per_word.append({"word": exp_words[i1 + k], "score": 0.0})
                    missing_all.extend(word_to_phonemes(exp_words[i1 + k]))
        elif tag == "delete":
            for k in range(i1, i2):
                per_word.append({"word": exp_words[k], "score": 0.0})
                missing_all.extend(word_to_phonemes(exp_words[k]))
    overall = sum(w["score"] for w in per_word) / len(per_word) if per_word else 0.0
    return round(overall, 1), {
        "words": per_word,
        "missing_phonemes": sorted(set(missing_all)),
        "inserted_phonemes": sorted(set(inserted_all)),
    }


def score_fluency(words: list[dict], duration_s: float) -> tuple[float, float, float]:
    if not words or duration_s <= 0.3:
        return 0.0, 0.0, 1.0
    wpm = len(words) / duration_s * 60
    speech_time = sum(w["end"] - w["start"] for w in words)
    pause_ratio = max(0.0, 1 - speech_time / duration_s)
    if WPM_IDEAL[0] <= wpm <= WPM_IDEAL[1]:
        wpm_score = 100.0
    elif wpm < WPM_IDEAL[0]:
        wpm_score = max(0.0, 100 * wpm / WPM_IDEAL[0])
    else:
        wpm_score = max(40.0, 100 - (wpm - WPM_IDEAL[1]) * 0.7)
    pause_score = 100.0 if pause_ratio <= PAUSE_BAD else max(0.0, 100 - (pause_ratio - PAUSE_BAD) * 220)
    return round(0.6 * wpm_score + 0.4 * pause_score, 1), round(wpm, 1), round(pause_ratio, 3)


def score_communication(expected_text: str, transcript: str, accept_patterns: list[str]) -> float:
    said = set(_words(transcript))
    if not said:
        return 0.0
    if expected_text:
        exp = _words(expected_text)
        if not exp:
            return 0.0
        hit = sum(1 for w in exp if w in said)
        return round(100.0 * hit / len(exp), 1)
    best = 0.0
    for pattern in accept_patterns:
        keys = {w for w in _words(re.sub(r"\{.*?\}", "", pattern)) if len(w) > 2}
        if not keys:
            continue
        best = max(best, len(keys & said) / len(keys))
    if not accept_patterns:
        return 75.0 if len(said) >= 4 else 45.0
    return round(100.0 * best, 1)


def score_attempt(expected_text: str, transcript: str, words: list[dict], duration_s: float,
                  kind: str, accept_patterns: list[str]) -> dict:
    pron, diff = score_pronunciation(expected_text or transcript, words)
    flu, wpm, pause = score_fluency(words, duration_s)
    comm = score_communication(expected_text, transcript, accept_patterns)
    weights = {
        "read_aloud": {"pronunciation": 1.0, "fluency": 0.0, "communication": 0.0},
        "shadow": {"pronunciation": 0.7, "fluency": 0.2, "communication": 0.1},
        "repeat": {"pronunciation": 0.6, "fluency": 0.0, "communication": 0.4},
        "respond": {"pronunciation": 0.2, "fluency": 0.3, "communication": 0.5},
        "short_answer": {"pronunciation": 0.2, "fluency": 0.3, "communication": 0.5},
    }.get(kind, {"pronunciation": 0.5, "fluency": 0.2, "communication": 0.3})
    overall = (pron * weights["pronunciation"] + flu * weights["fluency"] + comm * weights["communication"])
    return {
        "pronunciation": pron, "fluency": flu, "communication": comm,
        "overall": round(overall, 1), "wpm": wpm, "pause_ratio": pause, "phoneme_diff": diff,
    }
