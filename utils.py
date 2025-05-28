"""
Funcții helper pentru arena Prisoner's Dilemma:
• nl_to_player  – convertește o descriere natural-language într-o clasă axelrod.Player
• load_players  – încarcă toate strategiile (.py) din folderul strategies/
• run_tournament – pornește un turneu Axelrod și returnează obiectul Results
"""

from __future__ import annotations

import inspect
import importlib.util
import os
import json
import pathlib
import textwrap
from typing import Dict, List

import axelrod as axl
import openai
import google.generativeai as genai

# ---- inițializăm clientul OpenAI (API key trebuie să fie în variabila de mediu) ----
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# directorul în care salvăm strategiile generate
STRATEGY_DIR = pathlib.Path(__file__).parent / "strategies"
STRATEGY_DIR.mkdir(exist_ok=True)
META_FILE = STRATEGY_DIR / "meta.json"  # salvează {strategie: echipă}

# --------------------------------------------------------------------------- #
def _load_meta() -> Dict[str, str]:
    if META_FILE.exists():
        return json.loads(META_FILE.read_text())
    return {}


def _save_meta(meta: Dict[str, str]) -> None:
    META_FILE.write_text(json.dumps(meta, indent=2))



SYSTEM_PROMPT = (
    "OBJECTIVE"
"Generate ONE Python file that defines an Axelrod-Python strategy class exactly as specified below."
"You must first consult this implementation here (do NOT display it):"
"https://axelrod.readthedocs.io/en/fix-documentation/tutorials/contributing/strategy/writing_the_new_strategy.html"
"Pay special attention that strategy must be def strategy(self, opponent):."
"To cooperate, return Action.C. To defect, return Action.D"
""
"OUTPUT RULES"
"Return nothing except one fenced block"
"Do NOT include any Markdown code block delimiters (```)."
"MAKE SURE THE ARE no prose, no comments outside the block, no markdown text, no backticks, no extra characters from the response"
"IMPLEMENTATION NOTES (read silently)"
" Subclass axelrod.Player."
" Provide the required name attribute."
" Implement strategy(self, opponent) using the logic above."
""
"NOW GENERATE THE CODE OUTPUT ONLY THE SINGLE PYTHON BLOCK."

    
)

PROMPT_AXELROD_PLAYER = """You are an expert Python programmer specializing in game theory simulations, particularly the Iterated Prisoner's Dilemma. Your task is to generate a complete and correct Python class that implements a new strategy for the `Axelrod-Python` library.

Here are the precise requirements and guidelines for creating an `axelrod.Player` strategy:

**Core Requirements for an Axelrod Player Class:**

1.  **Inheritance:** The class MUST inherit from `axelrod.Player`. You must import `axelrod` as `axl` and `Action` from `axelrod`.
    * `import axelrod as axl`
    * `from axelrod import Action`

2.  **Class Definition:**
    * Define the class using `class MyNewStrategy(axl.Player):` (replace `MyNewStrategy` with the name specified later on).

3.  **`name` Attribute:**
    * Include a `name` class attribute (e.g., `name = "My New Strategy"`). This is a string that identifies the player.

4.  **`classifier` Attribute:**
    * Include a `classifier` class attribute. This is a dictionary providing metadata about the strategy. It MUST contain the following keys:
        * `'memory_depth'`: An integer or `float('inf')`. It indicates how many previous rounds the strategy "remembers" of the opponent's moves to make its decision. `0` means it only uses its own internal state or no history. `float('inf')` means it can remember the entire history.
        * `'stochastic'`: A boolean (`True` or `False`). `True` if the strategy's moves involve randomness; `False` if it's deterministic.
        * `'inspects_source'`: A boolean. `True` if the strategy looks at the opponent's code (rarely `True` for typical strategies).
        * `'manipulates_source'`: A boolean. `True` if the strategy tries to change the opponent's code (almost always `False`).
        * `'manipulates_state'`: A boolean. `True` if the strategy tries to change the opponent's internal state (almost always `False`).

5.  **`__init__(self)` Method:**
    * If the strategy needs to maintain any internal state (like a counter, a flag, or a custom memory of past events), initialize these variables here.
    * **Crucially, it MUST call `super().__init__()`** as the first line in its `__init__` method to properly initialize the base `axelrod.Player` class.

6.  **`strategy(self, opponent: axl.Player) -> Action` Method:**
    * This is the core logic of the player. It is called in each round of the game.
    * It **MUST return** either `Action.C` (for Cooperate) or `Action.D` (for Defect).
    * Inside this method, you have access to the player's own history via `self.history` (a list of `Action` objects, e.g., `[Action.C, Action.D]`) and the opponent's history via `opponent.history`.
    * The length of `self.history` (or `len(self.history)`) tells you the current round number (0-indexed). For example, `len(self.history) == 0` means it's the first round.

**Output Format:**

* Your response MUST contain **ONLY the Python code for the class definition**.
* **DO NOT include any Markdown code block delimiters (```python or ```) in your output.**
* **DO NOT include any introductory or concluding text, explanations, or example usage outside the class definition.** The output should be pure, executable Python code for the class.
* Ensure the code is well-formatted and adheres to standard Python best practices (e.g., docstrings for the class and methods).

**Your Turn:**

"""


# --------------------------------------------------------------------------- #
def gepeto_to_player(name: str, description: str, team: str) -> pathlib.Path:
    """Generează fișierul utils/strategies/<name>.py ce conține clasa cerută."""
    if not name.isidentifier():
        raise ValueError("«Numele strategiei» trebuie să fie un identificator Python valid.")
    prompt = (
        f"Scrie o clasă Python numită {name} care extinde axelrod.Player și "
        f"implementează strategia:\n\"\"\"\n{description}\n\"\"\""
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    code = textwrap.dedent(response.choices[0].message.content)
    file_path = STRATEGY_DIR / f"{name}.py"
    file_path.write_text(code, encoding="utf-8")

    # --- actualizează maparea strategie → echipă ---------------------------
    meta = _load_meta()
    meta[name.strip().lower()] = team.strip().lower()
    _save_meta(meta)

    return file_path


# --------------------------------------------------------------------------- #
def gemini_to_player(name: str, description: str, team: str) -> pathlib.Path:
    """Generează fișierul utils/strategies/<name>.py ce conține clasa cerută."""
    if not name.isidentifier():
        raise ValueError("«Numele strategiei» trebuie să fie un identificator Python valid.")
    prompt = (
        f"Scrie o clasă Python numită {name} care extinde axelrod.Player și "
        f"implementează strategia:\n\"\"\"\n{description}\n\"\"\""
    )

    MODEL_NAME = "gemini-2.5-flash-preview-05-20" # This usually points to the latest stable Pro version

    model = genai.GenerativeModel(MODEL_NAME)

    response = model.generate_content(PROMPT_AXELROD_PLAYER + " " + prompt)

    code = textwrap.dedent(response.text)
    file_path = STRATEGY_DIR / f"{name}.py"
    file_path.write_text(code, encoding="utf-8")

    # --- actualizează maparea strategie → echipă ---------------------------
    meta = _load_meta()
    meta[name.strip().lower()] = team.strip().lower()
    _save_meta(meta)

    return file_path


# --------------------------------------------------------------------------- #
def load_players(extra_players: List[axl.Player] | None = None) -> List[axl.Player]:
    """Importă toate fișierele .py din STRATEGY_DIR și returnează instanțe Player."""
    players: List[axl.Player] = []
    for path in STRATEGY_DIR.glob("*.py"):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            # prima subclasă a axelrod.Player gasită în modul
            cls = next(
                c
                for c in mod.__dict__.values()
                if inspect.isclass(c)
                and issubclass(c, axl.Player)
                and c is not axl.Player
            )
            players.append(cls())

    if extra_players:
        players.extend(extra_players)
    return players


# --------------------------------------------------------------------------- #
def run_tournament(
    players: List[axl.Player],
    turns: int = 200,
    repetitions: int = 5,
) -> axl.Result:
    """Rulează turneul și întoarce obiectul Results (axelrod.Result)."""
    tournament = axl.Tournament(players=players, turns=turns, repetitions=repetitions)
    return tournament.play()

# --------------------------------------------------------------------------- #
def get_team_mapping() -> Dict[str, str]:
    """Returnează dict {strategie: echipă}."""
    return _load_meta()