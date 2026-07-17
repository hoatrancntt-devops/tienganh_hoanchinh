"""Nhận xét tiếng Việt sinh từ luật. Task tần suất cao nhất trong app, giá 0 token."""

PHONEME_TIPS = {
    "θ": "âm /θ/ (think): đặt đầu lưỡi chạm mép răng trên rồi thổi hơi ra",
    "ð": "âm /ð/ (this): lưỡi chạm răng chứ không chạm lợi, có rung thanh quản",
    "s": "âm /s/ cuối từ: giữ lưỡi ở vị trí cũ và xì hơi thêm nửa nhịp",
    "z": "âm /z/ cuối từ: như /s/ nhưng có rung — sờ cổ họng sẽ thấy",
    "t": "âm /t/ cuối từ: chặn hơi bằng lưỡi ở lợi rồi thả nhẹ, không cần bật mạnh",
    "d": "âm /d/ cuối từ: như /t/ nhưng có rung, đây là dấu hiệu quá khứ",
    "k": "âm /k/ cuối từ: chặn hơi ở cuống lưỡi rồi thả",
    "ŋ": "âm /ŋ/ (-ing): hơi đi qua mũi, miệng không cần khép",
    "r": "âm /r/: cong lưỡi lên nhưng không chạm vào đâu cả",
    "l": "âm /l/: đầu lưỡi chạm lợi trên, hơi thoát hai bên",
    "ʃ": "âm /ʃ/ (sh): tròn môi một chút, hơi đi qua khe rộng hơn /s/",
    "tʃ": "âm /tʃ/ (ch): chặn rồi xì, như /t/ + /ʃ/ dính liền",
    "v": "âm /v/: răng trên chạm môi dưới và rung — khác /w/ tròn môi",
}


def _band(v: float) -> str:
    return "tốt" if v >= 75 else "khá" if v >= 50 else "cần luyện"


def build_feedback(scores: dict, kind: str) -> str:
    pron = scores["pronunciation"]
    flu = scores["fluency"]
    comm = scores["communication"]
    diff = scores.get("phoneme_diff") or {}
    missing = diff.get("missing_phonemes") or []
    inserted = diff.get("inserted_phonemes") or []
    words = diff.get("words") or []

    if not scores.get("transcript", "").strip():
        return "Mình chưa nghe được gì. Bạn kiểm tra micro và nói to hơn một chút nhé."

    parts: list[str] = []
    if pron >= 75:
        parts.append("Phát âm của bạn rõ, người nghe hiểu được.")
    elif comm >= 70:
        parts.append("Ý của bạn tới được người nghe.")
    elif pron >= 50:
        parts.append("Bạn đã nói được cả câu, đó là phần khó nhất.")

    tip_given = False
    for ph in missing:
        if ph in PHONEME_TIPS:
            parts.append(f"Bạn đang thiếu {PHONEME_TIPS[ph]}.")
            tip_given = True
            break
    if not tip_given and "ə" in inserted:
        parts.append("Bạn đang thêm một nguyên âm vào cuối từ (kiểu “work-sờ”). "
                     "Dừng hơi ngay sau phụ âm, đừng mở miệng thêm.")
        tip_given = True

    weak = [w for w in words if w["score"] < 50]
    if not tip_given and weak:
        worst = min(weak, key=lambda w: w["score"])
        parts.append(f"Từ “{worst['word']}” chưa rõ — nghe lại giọng mẫu rồi thử riêng từ đó.")

    if flu < 50 and scores.get("pause_ratio", 0) > 0.5:
        parts.append("Bạn ngắt quãng hơi nhiều. Đọc chậm cả câu một lượt sẽ tự nhiên hơn là nhặt từng từ.")
    elif flu < 50 and scores.get("wpm", 0) > 170:
        parts.append("Bạn nói hơi nhanh nên các âm dính vào nhau. Chậm lại một chút.")

    if kind in ("respond", "short_answer") and comm < 50:
        parts.append("Câu trả lời chưa bám vào câu hỏi. Trả lời thẳng và ngắn là đủ.")

    if not parts:
        parts.append(f"Phát âm {_band(pron)}, trôi chảy {_band(flu)}. Giữ nhịp này nhé.")
    return " ".join(parts[:3])
