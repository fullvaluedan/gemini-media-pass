"""Prompt guardrails for Flow video, and plain-English readings of gflow errors.

Flow refunds a blocked render but still blocks it. Prompts that name a real person or a famous movie character
were blocked every time in testing ("interests of third-party content providers"). A generic costume passes.
"""
from __future__ import annotations

import re
from typing import List, Optional

GUARDRAIL_TEXT = "One continuous shot, no cuts. No on-screen text or captions."

# Names Flow is known to block or very likely to block. Lowercase, matched as whole words.
PROTECTED_NAMES = [
    "jack sparrow", "captain jack", "harry potter", "hermione", "dumbledore", "voldemort", "gandalf", "frodo",
    "darth vader", "luke skywalker", "yoda", "han solo", "spider-man", "spiderman", "batman", "superman",
    "iron man", "tony stark", "captain america", "thor", "hulk", "wonder woman", "joker", "deadpool", "wolverine",
    "james bond", "indiana jones", "rocky balboa", "terminator", "mario", "luigi", "pikachu", "sonic",
    "mickey mouse", "elsa", "shrek", "homer simpson", "sherlock", "john wick", "barbie", "willy wonka",
    "taylor swift", "elon musk", "donald trump", "joe biden", "barack obama", "kim kardashian", "beyonce",
    "drake", "mrbeast", "mr beast", "johnny depp", "tom cruise", "keanu reeves", "leonardo dicaprio",
    "brad pitt", "the rock", "dwayne johnson", "oprah", "mark zuckerberg", "jeff bezos", "bill gates",
    "steve jobs", "sam altman", "jensen huang", "lionel messi", "cristiano ronaldo", "lebron james",
]
LOOKALIKE = re.compile(r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)*(?:-like|-inspired| lookalike| look-alike)\b"
                       r"|\b(?:played by|as seen in)\b")


def apply_guardrails(prompt: str, spoken_line: Optional[str] = None) -> str:
    """Append the no-cuts, no-captions instruction, and pin the dialogue when a line is given."""
    extra = GUARDRAIL_TEXT
    if spoken_line:
        extra += f' The speaker says only these exact words: "{spoken_line.strip()}" and stays silent after.'
    return f"{prompt.rstrip().rstrip('.')}. {extra}"


def third_party_names(prompt: str) -> List[str]:
    """Names or look-alike phrases in a prompt that Flow is likely to block."""
    low = prompt.lower()
    hits = [n for n in PROTECTED_NAMES if re.search(rf"(?<![\w-]){re.escape(n)}(?![\w-])", low)]
    hits += [m.group(0) for m in LOOKALIKE.finditer(prompt)]
    return hits


def third_party_warning(names: List[str]) -> str:
    return (f"Not sent, nothing spent. The prompt names {', '.join(repr(n) for n in names)}. Flow blocks real people "
            "and famous characters (\"interests of third-party content providers\"): a Jack Sparrow-like pirate was "
            "blocked 5 of 5 times. Describe a generic look instead (\"a weathered pirate in a red bandana\"), or use "
            "your own Flow avatar in a generic costume, which passes. Pass allow_names=True to send it anyway.")


MIGRATED = ("flow-host-migrated", "FlowHostMigratedError", "agent-only composer")
BLOCKED = ("third-party content", "third party content")
NOT_IN_CATALOG = "No local media record found"


def explain_flow_error(text: str) -> Optional[str]:
    """A plain-English reading of a known gflow failure, or None when the error is unknown."""
    if any(k in text for k in MIGRATED):
        return ("Your Google account was moved to Flow's new frontend (flow.google.com), and gflow cannot drive this "
                "request there yet. Nothing was spent.\n"
                "Works from here: text to video (`mode='t2v'`, count 1, no explicit resolution) and text to image.\n"
                "Do in the Flow web UI instead: image to image, image to video with a start frame, avatars, "
                "ingredients and character references. Download the result and keep editing locally.\n"
                "Retrying will not help: the switch is per account. Run `flow_doctor` to see what works.")
    if any(k in text.lower() for k in BLOCKED):
        return ("Flow blocked this prompt to protect third-party content (a real person, brand or famous character). "
                "Flow refunds blocked renders. Describe a generic look instead, or use your own Flow avatar "
                "in a generic costume.")
    if NOT_IN_CATALOG in text:
        return ("gflow only downloads media it made itself and keeps in its local catalog. This media ID is not there, "
                "which is normal for clips made in the Flow web UI. Download those from flow.google.com "
                "(open the clip, then Download).")
    if "unknown tool 'music'" in text or "unknown tool \"music\"" in text:
        return ("Your gflow version has no music generator (`gflow tools` only has prompt helpers). Make music at "
                "flowmusic.app or in the Flow web UI, download it, then run `flow_clip_qa` with kind='music' to check "
                "it has no lyrics.")
    return None
