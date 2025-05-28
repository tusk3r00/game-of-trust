import axelrod as axl
from axelrod import Action

class CooperationWin(axl.Player):
    """
    A strategy that aims for cooperation.

    It starts by cooperating. If in the previous round both players cooperated,
    it continues to cooperate. If it cooperated in the previous round but the
    opponent defected (betrayal), it then defects. In all other scenarios
    (e.g., if it defected in the previous round, regardless of opponent's move),
    it reverts to cooperation, attempting to re-establish a cooperative phase.
    """

    name = "Cooperation Win"
    classifier = {
        'memory_depth': 1,
        'stochastic': False,
        'inspects_source': False,
        'manipulates_source': False,
        'manipulates_state': False
    }

    def __init__(self):
        """
        Initializes the CooperationWin player.
        """
        super().__init__()

    def strategy(self, opponent: axl.Player) -> Action:
        """
        Determines the player's move for the current round.

        Parameters
        ----------
        opponent : axl.Player
            The opponent player in the current match.

        Returns
        -------
        axelrod.Action
            The chosen move: Action.C for Cooperate, Action.D for Defect.
        """
        # "Cooperez inițial." (Cooperate initially.)
        if not self.history:
            return Action.C

        my_last_move = self.history[-1]
        opponent_last_move = opponent.history[-1]

        # "Dacă nu (am fost trădată), schimb."
        # (If not (I was betrayed), change.)
        # This condition is met if we cooperated last round and the opponent defected.
        if my_last_move == Action.C and opponent_last_move == Action.D:
            return Action.D

        # "Dacă a mers bine (cooperare reciprocă), repet."
        # (If it went well (mutual cooperation), repeat.)
        # This falls into the general 'return Action.C' below, as it's not a betrayal.
        # This 'else' also covers cases where 'my_last_move' was Action.D,
        # leading the player to attempt cooperation again.
        return Action.C