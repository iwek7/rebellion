
class Prison():
    """Klasa odpowiadajaca za przetrzymywanie wiezniow"""
    def __init__(self, country):
        self.prisoners = []
        self.country = country

    def get_leaving_prisoners(self, record_data = False):
        """
        Usuwa wiezniow, ktorych wyrok uplunal z wiezienia i zwraca ich w liscie.
        Uwaga! Jesli nie zostana oslozeni przez 
        obiekt odbierajacy te liste to znikna.
        """
        prisoners_to_go = []
        # iteracja od tylu poniewaz usuwamy elementy w taki a nie innyc sposob
        for i in reversed(range(len(self.prisoners))): 
            # zmniejszenie wyroku
            self.prisoners[i].sentence_left -= 1  
            if self.prisoners[i].sentence_left <= 0:
                self.prisoners[i].jailed = False

                # to na potrzeby zbierania statystyk 
                self.prisoners[i].sentence_left = 0
                self.prisoners[i].sentence_total = 0

                self.prisoners[i].my_type = self.country.agent_types["PassiveCitizen"]
                prisoners_to_go.append(self.prisoners[i])

                del self.prisoners[i]
            else:
                if record_data:
                    self.prisoners[i].record_data()
        return prisoners_to_go
