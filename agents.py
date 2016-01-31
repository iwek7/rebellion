
import random
import math
import numpy as np

class Agent():
    """
    Agent jest czlonkiem spoleczenstwa. Istnieja dwa rodzaje agentow:
    Cop i Citizen. Obie te klasy dziedzicza z klasy Agent.
    """

    def __init__(self, country, id, location = None):
        """Inicjacja zmiennych charakteryzujacych agenta."""

        self.country = country
        self.id = id
        # lista typow agentow
        # przeniesc inicjacje tego do country
        self.agent_type = { "None": 0 ,
                            "ActiveCitizen" : 1, 
                            "PassiveCitizen" : 2,
                            "Cop" : 3,
                            "Prisoner" : 4
                            }
        # w klasach, ktore dziedzicza jest robiony override tego
        self.my_type = self.agent_type["None"]
        # dziedziczace klasy nadpisza
        # wizje rozumiemy jako odleglosc kratek
        self.vision_range = 0.0

        if location == None:
            self.location = self.country.get_free_location(True)
        else: 
            self.location = location
        self.country.occupied_fields[self.location] = self



        # Flagi dla poszczegolnych typow citizenow
        # inicjowane puste
 
        self.sentence_total = None
        self.sentence_left = None
        self.made_arrest = None  
        self.vision_range = None
        self.risk_aversion = None
        self.grievance = None
        self.perceived_hardship = None
        self.rebel_threshold = None

    def get_visible_fields(self):
        """ 
        Zwraca liste tupli ze wszystkich mozliwymi lokalizacjami    
        w zasiegu wizji agenta.
        """
        fields_in_vision = []
        for x in range(self.location[0] - self.vision_range, 
                        self.vision_range + self.location[0] + 1):
            for y in range(self.location[1] - self.vision_range, 
                        self.vision_range + self.location[1] + 1):
                # upewnic sie ze pole jest na mapie i ze na nim nie stoimy
                if ((y != self.location[1] or x != self.location[0]) and 
                    (y >= 0 and y < self.country.dimension) and
                    (x >= 0 and x < self.country.dimension)):
                    fields_in_vision.append((x,y))
        return fields_in_vision

    def move_agent(self): 
        """
        Zmiana lokalizacji na losowa dostepna w zasiegu wzroku agenta.
        """
        visible_fields = self.get_visible_fields()
        free_fields = [field for field in visible_fields
                 if self.country.occupied_fields[field].my_type == 0]
        # brak dostepnych pol - nie ruszamy sie
        if len(free_fields) == 0:
            return 
        # przejscie do nowej lokalizacji 
        old_loc = self.location
        self.location = random.choice(free_fields)

        # usuwamy pustego agenta explicite - nie jest to konieczne bo mamy garbage collector
        del self.country.occupied_fields[self.location]
        self.country.occupied_fields[self.location] = self
        # zwolnienie starego miejsca - wstawiamy agenta token
        self.country.occupied_fields[old_loc] = Agent(self.country, -1, old_loc)
        
  
    def update_agent(self, record_data = False):
        """
        Definicja do zmiany przez dziedziczace klasy.
        Ta metoda odpowiada za aktualizowanie wszystkich atrybutow agenta.
        
        """
        pass

    def record_data(self):
        """Citizen dodaje swoje statystyki do dataframe ze statystykami obiektu country."""
        self.country.statistics[self.my_type].iloc[
                -1, self.country.statistics[self.my_type].columns.get_loc("number_of_agents")] += 1
        self.country.statistics[self.my_type].iloc[
                -1, self.country.statistics[self.my_type].columns.get_loc("total_grievance")] += self.grievance
        self.country.statistics[self.my_type].iloc[
                -1, self.country.statistics[self.my_type].columns.get_loc("total_preceived_hardship")] += self.perceived_hardship
        self.country.statistics[self.my_type].iloc[
                -1, self.country.statistics[self.my_type].columns.get_loc("total_risk_aversion")] += self.risk_aversion


class Citizen(Agent):
    """
    Citizen jest czescia populacji i ma poziom niezadowolenia z rzadu.
    Citizen wedruje losowo i wyraza swoje niezadowolenie z natezeniem 
    zaleznym odobecnosci policjantow w jego polu widzenia.
    """
    def __init__(self, country, id):
        """
        Inicjacja zmiennych charakteryzujacych citizena.
        """ 
        super().__init__(country, id)
        # obiekt musi wiedziec kim jest w spoleczenstwie
        self.my_type = self.agent_type["PassiveCitizen"]

        # poczucie niesczescia obywatela
        self.perceived_hardship = random.uniform(0, 1)
        # sklonnosc obywatela do ryzyka
        self.risk_aversion = random.uniform(0, 1)
        self.grievance = (self.perceived_hardship * 
                        (1 - self.country.government.legitimacy))

        # o ile musi byc wieksza zlosc niz ryzyko
        self.rebel_threshold = 0.1
        # stala uzywana przy kalkulowaniu prawd aresztowania
        # pozwala utrzymac sensowne ratio gdy w polu widzena jest tylko jeden
        # Citizen i Cop 
        self.arrest_const = 2.3 #-math.log(0.1)
        
        
        # zmienne okreslajace dlugosc wyroku
        self.sentence_left = 0
        self.sentence_total = 0
        self.vision_range = 6
     
 
    def calculate_cops_ratio_in_vision(self):
        """
        Iloraz agentow typu Cop i aktywnych citizen w sasiedztwie tego agenta.
        Agent zawsze liczy siebie jako aktywnego.
        """
        visible_agents = self.get_visible_fields()
        cops_in_vision = [loc for loc in visible_agents 
                if (self.country.occupied_fields[loc].my_type == 
                                    self.agent_type["Cop"])]

        actives_in_vision = [loc for loc in visible_agents 
            if (self.country.occupied_fields[loc].my_type ==
                         self.agent_type["ActiveCitizen"])]
            # + 1 bo wlicza sameo siebie
        return len(cops_in_vision) / float(len(actives_in_vision) + 1)

    # funkcja floor uzyta na stosunku copow do citizenow sprawia, 
    # ze model osiaga zbieznosc
    def calculate_arrest_probability(self):
        """
        Kalkulacja prawdopodobienstwa aresztowania na podstawie
        ilosci citizenow, copow i stalej modelu

        """
        return int(self.calculate_cops_ratio_in_vision() > 1)       
        # return (1 - math.exp(-self.arrest_const * 
        #                 math.floor(self.calculate_cops_ratio_in_vision())))
        
    def update_rebel_state(self):
        """
        na podstawie risk_aversion i arrest_prob 
        podejmuje decyzje o przejsciu do stanu rebel
        """
        if (self.grievance - self.calculate_arrest_probability() * self.risk_aversion > 
                                self.rebel_threshold) == True:
            self.my_type = self.agent_type["ActiveCitizen"]
        else:
            self.my_type = self.agent_type["PassiveCitizen"]
        
    # parametr count_arrests nic nie robi tutaj, robi w copie
    def update_agent(self, record_data = False):
        """
        Metoda odpowiedzialna za aktualizowanie wszystkich atrybutow agenta.
        """
        super().update_agent(record_data)

        self.update_rebel_state()
        self.move_agent()
        if record_data:
            self.record_data()


class Cop(Agent):
    """
    Cop to policjant pilnujacy porzadku w imieniu rzadu. Moze on 
    aresztowac obywateli, ktorzy otwarcie protestuja 
    przeciwko urzedujacej wladzy.

    """
    def __init__(self, country, id):
        """
        Inicjowanie zmiennych charakteryzujacych agenta typu cop.
        """
        super().__init__(country, id)
        self.my_type = self.agent_type["Cop"]
        self.vision_range = 6
        # flaga pokazujaca czy cop kogos aresztowal
        self.made_arrest = False

    def arrest_active_citizen(self):
        """
        Umiesc losowego aktywnego obywatela w polu widzenia w wiezieniu.
        Zwraca prawde jesli doszlo do aresztowania.
        """

        visible_agents = self.get_visible_fields()
        # wybor tylko obywateli typu Citizen z atrybutem active == True
        actives_in_vision = [agent for agent in visible_agents 
            if (self.country.occupied_fields[agent].my_type ==
                         self.agent_type["ActiveCitizen"])
            ]
        # wybranie obywatela do aresztowania
        if len(actives_in_vision) == 0:
            return False # brak aktywnych obywateli w polu widzenia
        arrested = random.choice(actives_in_vision)
        # aresztowanie Citizena
        self.country.occupied_fields[arrested].my_type = self.agent_type["Prisoner"]
        # policjant wyznacza wyrok
        self.country.occupied_fields[arrested].sentence_total = (
                random.choice(self.country.government.rebel_jail_time)      
                            )
        self.country.occupied_fields[arrested].sentence_left = self.country.occupied_fields[arrested].sentence_total

        # aresztowany znajduje sie w wiezieniu
        prisoner = self.country.occupied_fields[arrested]
        self.country.prison.prisoners.append(
                                prisoner)

         # policjant przesuwa sie na pole, ktore zajmowal citizen
        old_loc = self.location
        self.location = arrested
        self.country.occupied_fields[arrested] = self
     
        # # zwalnianie opuszczonego pola
        self.country.occupied_fields[old_loc] = Agent(self.country,-1, old_loc)
        
        return True

    def update_agent(self, record_data = False):
        """
        Ta metoda odpowiada za aktualizowanie wszystkich atrybutow agenta i 
        przeprowadzanie przez niego czynnosci.
        """
         # ustawmy flage aresztowania
         # obecnie nie jest uzywana ale klasa statisticsOffice uzywa tego do zbierania danych
         # narazie ta klasa nie jest uzywana ale to zostawiam
        self.made_arrest = self.arrest_active_citizen()
        if record_data:
            self.record_data(self.made_arrest)



        self.move_agent()

    # override
    def record_data(self, made_arrest):        
        self.country.statistics[self.my_type].iloc[
            -1, self.country.statistics[self.my_type].columns.get_loc(
                                        "number_of_arrests")] += int(made_arrest) 
        
