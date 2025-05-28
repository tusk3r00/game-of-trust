import axelrod as axl
from axelrod import Action
import random

class Random(axl.Player):
    """
    A player that cooperates 80% of the time and defects 20% of the time,
    independent of the opponent's history.
    """
    name = "Random 80/20"
    classifier = {
        'memory_depth': 0,
        'stochastic': True,
        'inspects_source': False,
        'manipulates_source': False,
        'manipulates_state': False
    }

    def __init__(self):
        """
        Initializes the Random player.
        """
        super().__init__()

    def strategy(self, opponent: axl.Player) -> Action:
        """
        Decides to Cooperate 80% of the time or Defect 20% of the time.

        Args:
            opponent: The opponent player object (not used in this strategy).

        Returns:
            Action.C for Cooperate, or Action.D for Defect.
        """
        if random.random() <= 0.8:
            return Action.C
        return Action.D