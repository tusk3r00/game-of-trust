import axelrod as axl
from axelrod import Action

class Cooperaresiadaptare(axl.Player):
    """
    Cooperates in the first round. Then, reacts to behavior:
    if the opponent cooperated in the previous round, this strategy cooperates;
    if the opponent defected in the previous round, this strategy defects.
    This strategy aims to find common ground by adapting to the opponent's last move,
    similar to Tit-for-Tat.
    """

    name = "Coopera si Adaptare"
    classifier = {
        'memory_depth': 1,
        'stochastic': False,
        'inspects_source': False,
        'manipulates_source': False,
        'manipulates_state': False
    }

    def __init__(self):
        """
        Initializes the player. Calls the superclass constructor to ensure
        proper setup of the Axelrod Player base class.
        """
        super().__init__()

    def strategy(self, opponent: axl.Player) -> Action:
        """
        Determines the player's next move.

        In the first round, the strategy cooperates.
        In subsequent rounds, it mimics the opponent's previous move.
        This is a classic Tit-for-Tat mechanism.

        Args:
            opponent: The opponent player object, providing access to their history.

        Returns:
            Action.C for Cooperate or Action.D for Defect.
        """
        if len(self.history) == 0:
            # First round, cooperate
            return Action.C
        else:
            # Subsequent rounds, mimic opponent's last move
            # opponent.history[-1] gives the opponent's move from the previous round
            return opponent.history[-1]