class Government():
    """
    Rzad kontroluje panstwo i jego policje (agentow typu Cop)
    Rzad chce sie za wszelka cene utrzymac przy wladzy i rozkazuje 
    policjata aresztowac obywateli (agentow typu Citizen).
    Wizerunek rzadu ma wplyw na sklonnosc 
    do przechodzenia Citizenow do stanu rebel.
    Do kometencji rzadu nalezy ustanawianie zasad dzialania policji.

    """
    def __init__(self, legitimacy):
        """Inicjacja zasad ustalanych przez rzad i jego charakterystyk."""

        # wspolczynnik poparcia rzadu w spoleczenstwie
        # waha sie od 0 do 1
        assert(legitimacy >= 0 and legitimacy <= 1)
        self.legitimacy = legitimacy
        # czasy wyrokow odpowiednio dla winnych aresztowanych
        # wyroki sa losowane z rozkladu jednostajnego
        self.rebel_jail_time = range(0, 30)
