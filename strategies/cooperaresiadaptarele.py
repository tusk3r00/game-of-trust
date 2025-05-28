import axelrod as axl
from axelrod import Action

class Cooperaresiadaptarele(axl.Player):
    """
    A strategy that always defects, regardless of the opponent's history or actions.
    Named "Cooperaresiadaptarele" (CooperateAndAdapt) as per the request,
    but implements an always-defect strategy.
    """
    name = "Cooperaresiadaptarele"
    classifier = {
        'memory_depth': 0,  # Does not remember opponent's moves
        'stochastic': False,  # Deterministic
        'inspects_source': False,  # Does not look at opponent's code
        'manipulates_source': False,  # Does not change opponent's code
        'manipulates_state': False  # Does not change opponent's internal state
    }

    def __init__(self):
        """
        Initializes the player. Calls the superclass constructor.
        No specific state needed for this strategy.
        """
        super().__init__()

    def strategy(self, opponent: axl.Player) -> Action:
        """
        Always returns Defect (Action.D).
        """
        return Action.D