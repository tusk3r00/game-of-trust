import axelrod as axl
from axelrod import Action

class TradareLaTradare(axl.Player):
    """
    Cooperates initially. If the opponent ever defects,
    the player will defect continuously from that point onwards.

    This strategy starts by cooperating. It maintains an internal flag
    to track if the opponent has defected at any point during the game.
    Once the opponent defects for the first time, this strategy will
    switch to defecting continuously for all subsequent rounds.
    """

    name = "Tradare La Tradare"
    classifier = {
        'memory_depth': float('inf'),  # Remembers if the opponent has ever defected.
        'stochastic': False,           # The strategy is deterministic.
        'inspects_source': False,      # Does not inspect opponent's code.
        'manipulates_source': False,   # Does not manipulate opponent's code.
        'manipulates_state': False     # Does not manipulate opponent's internal state.
    }

    def __init__(self):
        """
        Initializes the player and sets a flag to track if the opponent
        has ever defected.
        """
        super().__init__()
        self.has_opponent_defected = False

    def strategy(self, opponent: axl.Player) -> Action:
        """
        The core logic of the TradareLaTradare strategy.

        - In the first round, the player cooperates.
        - If the `has_opponent_defected` flag is True (meaning the opponent
          has defected in a previous round), the player defects.
        - Otherwise, it checks the opponent's last move. If the opponent
          defected in the last round, the `has_opponent_defected` flag is
          set to True, and the player defects.
        - If the opponent cooperated in the last round and has not previously
          defected, the player continues to cooperate.

        Args:
            opponent: The opponent player object, providing access to
                      opponent's history.

        Returns:
            Action.C for Cooperate, or Action.D for Defect.
        """
        # If the opponent has defected in any previous round, defect continuously.
        if self.has_opponent_defected:
            return Action.D

        # In the very first round, always cooperate.
        if not self.history:
            return Action.C

        # Check the opponent's last move.
        # If the opponent defected, set the flag and defect.
        if opponent.history[-1] == Action.D:
            self.has_opponent_defected = True
            return Action.D
        else:
            # If the opponent cooperated in the last round, and has not
            # defected in any previous round (checked by the initial if
            # condition), then cooperate.
            return Action.C