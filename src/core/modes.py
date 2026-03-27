"""Writing modes: Tutorial and Ouija.

Tutorial mode: The user types a phrase and the robot writes it letter by letter,
showing the full pick-and-place process as an educational demonstration.

Ouija mode: The user asks a question and the robot "channels spirits" to write
a response. Responses are selected from a curated pool designed to feel
mysterious and random, like a real Ouija board experience.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from .writer import RoboticWriter, BlockCircle, WritingLine
from .robot import ScorbotIII


# ── Ouija response pool ───────────────────────────────────────────────────
# Grouped by question type for semi-intelligent matching.
# Each response is short enough for the robot to write (max ~15 chars).

OUIJA_GREETINGS = [
    "HELLO HUMAN",
    "GREETINGS",
    "I SEE YOU",
    "WELCOME",
    "AT LAST",
]

OUIJA_YES_NO = [
    "YES",
    "NO",
    "MAYBE",
    "ASK AGAIN",
    "NEVER",
    "ALWAYS",
    "SOON",
    "NOT YET",
    "DOUBTFUL",
    "CERTAIN",
    "PERHAPS",
    "WHY NOT",
]

OUIJA_WHO = [
    "A FRIEND",
    "NO ONE",
    "YOURSELF",
    "A GHOST",
    "THE WIND",
    "A SHADOW",
    "YOUR PAST",
    "A STRANGER",
    "TIME",
]

OUIJA_WHEN = [
    "TONIGHT",
    "TOMORROW",
    "NEVER",
    "SOON",
    "IN A DREAM",
    "AT DAWN",
    "YESTERDAY",
    "RIGHT NOW",
    "NEXT MOON",
]

OUIJA_WHERE = [
    "HERE",
    "NOWHERE",
    "BEHIND YOU",
    "FAR AWAY",
    "IN A BOOK",
    "THE SKY",
    "BELOW",
    "INSIDE",
]

OUIJA_WHAT = [
    "NOTHING",
    "THE TRUTH",
    "A SECRET",
    "SILENCE",
    "HOPE",
    "A RIDDLE",
    "PATIENCE",
    "COURAGE",
    "MYSTERY",
]

OUIJA_HOW = [
    "SLOWLY",
    "WITH CARE",
    "BY CHANCE",
    "TRUST IT",
    "LET GO",
    "BREATHE",
    "LISTEN",
    "WAIT",
]

OUIJA_MYSTERIOUS = [
    "BEWARE",
    "RUN",
    "LOOK UP",
    "DO NOT FEAR",
    "I KNOW",
    "REMEMBER",
    "FORGET IT",
    "WAKE UP",
    "ITS COMING",
    "GOODBYE",
    "HELP ME",
    "BELIEVE",
    "DONT LOOK",
    "IM HERE",
    "FIND ME",
    "THE END",
]


def classify_question(text: str) -> str:
    """Classify a question to select the appropriate response pool."""
    t = text.upper().strip().rstrip("?!.")

    if not t:
        return "mysterious"

    first_word = t.split()[0] if t.split() else ""

    # Greeting detection
    greetings = {"HI", "HELLO", "HEY", "HOLA", "GREETINGS", "SUP", "YO"}
    if first_word in greetings or t in greetings:
        return "greeting"

    # Yes/no questions
    yn_starters = {"IS", "ARE", "DO", "DOES", "DID", "WILL", "WOULD", "CAN",
                   "COULD", "SHOULD", "SHALL", "HAVE", "HAS", "AM", "WAS", "WERE"}
    if first_word in yn_starters:
        return "yes_no"

    # Wh-questions
    if first_word in {"WHO", "WHOM", "WHOSE"}:
        return "who"
    if first_word in {"WHEN"}:
        return "when"
    if first_word in {"WHERE"}:
        return "where"
    if first_word in {"WHAT", "WHICH"}:
        return "what"
    if first_word in {"HOW"}:
        return "how"
    if first_word in {"WHY"}:
        return "what"  # "why" gets philosophical answers

    return "mysterious"


RESPONSE_POOLS = {
    "greeting": OUIJA_GREETINGS,
    "yes_no": OUIJA_YES_NO,
    "who": OUIJA_WHO,
    "when": OUIJA_WHEN,
    "where": OUIJA_WHERE,
    "what": OUIJA_WHAT,
    "how": OUIJA_HOW,
    "mysterious": OUIJA_MYSTERIOUS,
}


def generate_ouija_response(question: str) -> str:
    """Generate a Ouija-style response to a question.

    The response is selected from a curated pool based on the question type,
    with some randomness to make it feel unpredictable.

    Args:
        question: The user's question.

    Returns:
        A short, mysterious response string.
    """
    category = classify_question(question)
    pool = RESPONSE_POOLS[category]

    # 20% chance of getting a "mysterious" response regardless of category
    if random.random() < 0.2 and category != "mysterious":
        pool = OUIJA_MYSTERIOUS

    return random.choice(pool)


@dataclass
class WritingSession:
    """A writing session that manages the robot and produces simulation data.

    Supports two modes:
        - tutorial: Robot writes exactly what the user typed.
        - ouija: Robot generates and writes a mysterious response.
    """

    mode: str  # "tutorial" or "ouija"
    user_input: str = ""
    robot_output: str = ""
    action_log: list = None
    simulation_data: dict = None

    def __post_init__(self):
        self.action_log = []

    def execute(
        self,
        block_circle: Optional[BlockCircle] = None,
        writing_line: Optional[WritingLine] = None,
    ) -> dict:
        """Run the writing session.

        Returns:
            Complete simulation data dict.
        """
        if self.mode == "tutorial":
            self.robot_output = self.user_input.upper()
        elif self.mode == "ouija":
            self.robot_output = generate_ouija_response(self.user_input)
        else:
            raise ValueError(f"Unknown mode: {self.mode}")

        robot = ScorbotIII(interpolation_steps=30)
        writer = RoboticWriter(
            robot=robot,
            block_circle=block_circle or BlockCircle(),
            writing_line=writing_line or WritingLine(),
        )

        self.action_log = writer.write_text(self.robot_output)
        self.simulation_data = writer.get_simulation_data()

        return {
            "mode": self.mode,
            "user_input": self.user_input,
            "robot_output": self.robot_output,
            "action_log": self.action_log,
            "simulation": self.simulation_data,
            "summary": {
                "total_actions": len(self.action_log),
                "characters_placed": sum(
                    1 for a in self.action_log if a["action"] == "place"
                ),
            },
        }
