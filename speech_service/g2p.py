"""Chuyển từ tiếng Anh sang chuỗi âm vị.

Lexicon chứa từ trong nội dung seed (chính xác, viết tay); từ lạ rơi về luật.
Không dùng g2p_en/nltk: kéo theo mấy trăm MB dữ liệu cho một máy 8GB đã chật.
"""
import re

LEXICON: dict[str, list[str]] = {
    "a": ["ə"], "an": ["ə", "n"], "the": ["ð", "ə"], "and": ["æ", "n", "d"],
    "i": ["aɪ"], "you": ["j", "u"], "he": ["h", "i"], "she": ["ʃ", "i"],
    "it": ["ɪ", "t"], "we": ["w", "i"], "they": ["ð", "eɪ"], "me": ["m", "i"],
    "my": ["m", "aɪ"], "your": ["j", "ɔr"], "his": ["h", "ɪ", "z"], "her": ["h", "ɜr"],
    "is": ["ɪ", "z"], "am": ["æ", "m"], "are": ["ɑr"], "was": ["w", "ʌ", "z"],
    "were": ["w", "ɜr"], "be": ["b", "i"], "been": ["b", "ɪ", "n"],
    "have": ["h", "æ", "v"], "has": ["h", "æ", "z"], "had": ["h", "æ", "d"],
    "do": ["d", "u"], "does": ["d", "ʌ", "z"], "did": ["d", "ɪ", "d"],
    "work": ["w", "ɜr", "k"], "works": ["w", "ɜr", "k", "s"],
    "worked": ["w", "ɜr", "k", "t"], "working": ["w", "ɜr", "k", "ɪ", "ŋ"],
    "think": ["θ", "ɪ", "ŋ", "k"], "thinks": ["θ", "ɪ", "ŋ", "k", "s"],
    "thank": ["θ", "æ", "ŋ", "k"], "thanks": ["θ", "æ", "ŋ", "k", "s"],
    "this": ["ð", "ɪ", "s"], "that": ["ð", "æ", "t"], "these": ["ð", "i", "z"],
    "those": ["ð", "oʊ", "z"], "there": ["ð", "ɛr"], "then": ["ð", "ɛ", "n"],
    "three": ["θ", "r", "i"], "third": ["θ", "ɜr", "d"], "thirty": ["θ", "ɜr", "t", "i"],
    "sink": ["s", "ɪ", "ŋ", "k"], "in": ["ɪ", "n"], "on": ["ɑ", "n"], "at": ["æ", "t"],
    "to": ["t", "u"], "for": ["f", "ɔr"], "with": ["w", "ɪ", "ð"], "about": ["ə", "b", "aʊ", "t"],
    "sorry": ["s", "ɑ", "r", "i"], "please": ["p", "l", "i", "z"],
    "again": ["ə", "g", "ɛ", "n"], "say": ["s", "eɪ"], "said": ["s", "ɛ", "d"],
    "slowly": ["s", "l", "oʊ", "l", "i"], "repeat": ["r", "ɪ", "p", "i", "t"],
    "catch": ["k", "æ", "tʃ"], "understand": ["ʌ", "n", "d", "ər", "s", "t", "æ", "n", "d"],
    "meet": ["m", "i", "t"], "meeting": ["m", "i", "t", "ɪ", "ŋ"],
    "nice": ["n", "aɪ", "s"], "good": ["g", "ʊ", "d"], "morning": ["m", "ɔr", "n", "ɪ", "ŋ"],
    "hello": ["h", "ɛ", "l", "oʊ"], "how": ["h", "aʊ"], "what": ["w", "ʌ", "t"],
    "where": ["w", "ɛr"], "when": ["w", "ɛ", "n"], "who": ["h", "u"], "why": ["w", "aɪ"],
    "today": ["t", "ə", "d", "eɪ"], "tomorrow": ["t", "ə", "m", "ɑ", "r", "oʊ"],
    "yesterday": ["j", "ɛ", "s", "t", "ər", "d", "eɪ"],
    "team": ["t", "i", "m"], "office": ["ɑ", "f", "ɪ", "s"],
    "report": ["r", "ɪ", "p", "ɔr", "t"], "reports": ["r", "ɪ", "p", "ɔr", "t", "s"],
    "finish": ["f", "ɪ", "n", "ɪ", "ʃ"], "finished": ["f", "ɪ", "n", "ɪ", "ʃ", "t"],
    "ask": ["æ", "s", "k"], "asked": ["æ", "s", "k", "t"], "asks": ["æ", "s", "k", "s"],
    "send": ["s", "ɛ", "n", "d"], "sent": ["s", "ɛ", "n", "t"],
    "help": ["h", "ɛ", "l", "p"], "helps": ["h", "ɛ", "l", "p", "s"], "leave": ["l", "i", "v"],
    "day": ["d", "eɪ"], "days": ["d", "eɪ", "z"], "off": ["ɔ", "f"], "call": ["k", "ɔ", "l"],
    "calls": ["k", "ɔ", "l", "z"], "lunch": ["l", "ʌ", "n", "tʃ"], "coffee": ["k", "ɔ", "f", "i"],
    "order": ["ɔr", "d", "ər"], "check": ["tʃ", "ɛ", "k"], "checked": ["tʃ", "ɛ", "k", "t"],
    "bill": ["b", "ɪ", "l"], "table": ["t", "eɪ", "b", "ə", "l"],
    "hr": ["eɪ", "tʃ", "ɑr"], "server": ["s", "ɜr", "v", "ər"], "servers": ["s", "ɜr", "v", "ər", "z"],
    "network": ["n", "ɛ", "t", "w", "ɜr", "k"], "cloud": ["k", "l", "aʊ", "d"],
    "deploy": ["d", "ɪ", "p", "l", "ɔɪ"], "deployed": ["d", "ɪ", "p", "l", "ɔɪ", "d"],
    "deployment": ["d", "ɪ", "p", "l", "ɔɪ", "m", "ə", "n", "t"],
    "query": ["k", "w", "ɪ", "r", "i"], "cache": ["k", "æ", "ʃ"],
    "router": ["r", "aʊ", "t", "ər"], "ticket": ["t", "ɪ", "k", "ɪ", "t"],
    "tickets": ["t", "ɪ", "k", "ɪ", "t", "s"], "vpn": ["v", "i", "p", "i", "ɛ", "n"],
    "restart": ["r", "i", "s", "t", "ɑr", "t"], "issue": ["ɪ", "ʃ", "u"], "issues": ["ɪ", "ʃ", "u", "z"],
    "down": ["d", "aʊ", "n"], "up": ["ʌ", "p"], "back": ["b", "æ", "k"],
    "fixed": ["f", "ɪ", "k", "s", "t"], "fix": ["f", "ɪ", "k", "s"],
    "logs": ["l", "ɔ", "g", "z"], "since": ["s", "ɪ", "n", "s"], "affected": ["ə", "f", "ɛ", "k", "t", "ɪ", "d"],
    "tried": ["t", "r", "aɪ", "d"], "escalate": ["ɛ", "s", "k", "ə", "l", "eɪ", "t"],
    "uses": ["j", "u", "z", "ɪ", "z"], "use": ["j", "u", "z"], "needs": ["n", "i", "d", "z"],
    "needed": ["n", "i", "d", "ɪ", "d"], "need": ["n", "i", "d"],
    "department": ["d", "ɪ", "p", "ɑr", "t", "m", "ə", "n", "t"],
    "accounting": ["ə", "k", "aʊ", "n", "t", "ɪ", "ŋ"], "sales": ["s", "eɪ", "l", "z"],
    "colleagues": ["k", "ɑ", "l", "i", "g", "z"], "colleague": ["k", "ɑ", "l", "i", "g"],
    "projects": ["p", "r", "ɑ", "dʒ", "ɛ", "k", "t", "s"], "project": ["p", "r", "ɑ", "dʒ", "ɛ", "k", "t"],
    "sounds": ["s", "aʊ", "n", "d", "z"], "months": ["m", "ʌ", "n", "θ", "s"],
    "manager": ["m", "æ", "n", "ɪ", "dʒ", "ər"], "engineer": ["ɛ", "n", "dʒ", "ɪ", "n", "ɪr"],
    "available": ["ə", "v", "eɪ", "l", "ə", "b", "ə", "l"], "blocked": ["b", "l", "ɑ", "k", "t"],
    "blockers": ["b", "l", "ɑ", "k", "ər", "z"], "track": ["t", "r", "æ", "k"],
    "minh": ["m", "ɪ", "n"], "nam": ["n", "ɑ", "m"], "lan": ["l", "æ", "n"],
    "migration": ["m", "aɪ", "g", "r", "eɪ", "ʃ", "ə", "n"], "start": ["s", "t", "ɑr", "t"],
    "new": ["n", "u"], "here": ["h", "ɪr"], "week": ["w", "i", "k"], "last": ["l", "æ", "s", "t"],
}

_DIGRAPHS = [
    ("tch", ["tʃ"]), ("sch", ["s", "k"]), ("th", ["θ"]), ("sh", ["ʃ"]), ("ch", ["tʃ"]),
    ("ph", ["f"]), ("ck", ["k"]), ("ng", ["ŋ"]), ("qu", ["k", "w"]), ("wh", ["w"]),
    ("ee", ["i"]), ("ea", ["i"]), ("oo", ["u"]), ("ou", ["aʊ"]), ("ow", ["aʊ"]),
    ("ai", ["eɪ"]), ("ay", ["eɪ"]), ("oa", ["oʊ"]), ("oi", ["ɔɪ"]), ("oy", ["ɔɪ"]),
    ("er", ["ər"]), ("ir", ["ɜr"]), ("ur", ["ɜr"]), ("ar", ["ɑr"]), ("or", ["ɔr"]),
]
_SINGLE = {
    "a": "æ", "e": "ɛ", "i": "ɪ", "o": "ɑ", "u": "ʌ", "y": "i",
    "b": "b", "c": "k", "d": "d", "f": "f", "g": "g", "h": "h", "j": "dʒ",
    "k": "k", "l": "l", "m": "m", "n": "n", "p": "p", "r": "r", "s": "s",
    "t": "t", "v": "v", "w": "w", "x": "k", "z": "z",
}


def _rule_based(word: str) -> list[str]:
    out, i = [], 0
    while i < len(word):
        hit = None
        for pat, ph in _DIGRAPHS:
            if word.startswith(pat, i):
                hit = (pat, ph)
                break
        if hit:
            out.extend(hit[1])
            i += len(hit[0])
            continue
        ch = word[i]
        if ch == "e" and i == len(word) - 1 and len(word) > 3:
            i += 1
            continue
        if ch in _SINGLE:
            out.append(_SINGLE[ch])
        i += 1
    return out


def word_to_phonemes(word: str) -> list[str]:
    w = re.sub(r"[^a-z']", "", word.lower())
    if not w:
        return []
    if w in LEXICON:
        return list(LEXICON[w])
    for suffix in ("s", "ed", "ing"):
        if w.endswith(suffix) and w[: -len(suffix)] in LEXICON:
            base = list(LEXICON[w[: -len(suffix)]])
            if suffix == "s":
                extra = ["s"] if base[-1] in {"p", "t", "k", "f", "θ"} else ["z"]
            elif suffix == "ed":
                extra = ["t"] if base[-1] in {"p", "k", "f", "s", "ʃ", "tʃ", "θ"} else ["d"]
            else:
                extra = ["ɪ", "ŋ"]
            return base + extra
    return _rule_based(w)


def text_to_phonemes(text: str) -> list[list[str]]:
    return [word_to_phonemes(w) for w in re.findall(r"[A-Za-z']+", text)]


def in_lexicon(word: str) -> bool:
    return re.sub(r"[^a-z']", "", word.lower()) in LEXICON
