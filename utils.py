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
import pathlib
import textwrap
from typing import List

import axelrod as axl
import openai

# ---- inițializăm clientul OpenAI (API key trebuie să fie în variabila de mediu) ----
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# directorul în care salvăm strategiile generate
STRATEGY_DIR = pathlib.Path(__file__).parent / "strategies"
STRATEGY_DIR.mkdir(exist_ok=True)

SYSTEM_PROMPT = (
    "Ești un generator de cod Python concis. "
    "Primești o descriere (în română) a unei strategii pentru Prisoner's Dilemma repetat "
    "și generezi o clasă care extinde axelrod.Player și o implementează. "
    "Nu adăuga importuri în afară de axelrod și nu depăși 60 de linii de cod."
)


# --------------------------------------------------------------------------- #
def nl_to_player(name: str, description: str) -> pathlib.Path:
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
